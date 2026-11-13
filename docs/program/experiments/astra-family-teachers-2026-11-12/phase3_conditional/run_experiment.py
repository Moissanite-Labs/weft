#!/usr/bin/env python3
"""Offline phase3 tool-assisted teacher orchestration. Never reads credentials."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
import numpy as np
import lab

CONFIG={'version':'conditional-passing-v3','seeds':[101,211,307],'rounds':4,'candidates_per_round':4,
        'max_output_tokens':8000,'teacher_model':'gpt-6-astra','low_drift_budget':.001,
        'hazard_absolute_budget':.0005,'hazard_relative_budget':.02,'rollout_seeds':[1701,1702,1703],
        'primary_required_improvement':.10,'gradient_steps':600}
ROOT=Path(__file__).resolve().parent


def read(path): return json.loads(path.read_text())
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def experiments(out): return [read(p) for p in sorted((out/'experiments').glob('*.json'))]
def name(seed,round): return f'seed-{seed}.tools.round-{round}'
def code_hashes():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'lab.py',ROOT/'run_experiment.py',ROOT/'PROTOCOL.md']}


def gate(source,candidate,exp):
    gates={}; score=0.
    for split in ('validation','validation_shift'):
        before=lab.conditional_metrics(source,exp[split],source)
        after=lab.conditional_metrics(candidate,exp[split],source)
        checks={k:after[k]<before[k]-1e-10 for k in ('left_active_mse','right_active_mse','paired_context_contrast_mse')}
        checks['hazard']=after['hazard_mse']<=before['hazard_mse']+max(CONFIG['hazard_absolute_budget'],CONFIG['hazard_relative_budget']*before['hazard_mse'])
        checks['unchanged']=after['unchanged_context_drift']<=CONFIG['low_drift_budget']
        checks['frozen']=after['frozen_equal']
        gates[split]={'checks':checks,'metrics':after,'accepted':all(checks.values())}
        score+=after['paired_context_contrast_mse']/2
    return {'accepted':all(v['accepted'] for v in gates.values()),'selection_score':score,'gate':gates}


def selected(records):
    eligible=[r for r in records if r.get('accepted')]
    return min(eligible,key=lambda r:r['selection_score']) if eligible else None


def make_request(exp,round,history):
    packet=lab.teacher_packet(exp['source'],exp['train'],exp['validation'],examples=24)
    packet['training_diagnostics']=lab.analysis_packet(exp['source'],exp['train'])
    packet['round']=round; packet['rounds_total']=4
    packet['feedback']=history; packet['selection_rules']=CONFIG
    packet['operator_schema']=[
        {'op':'delta','edits':[{'tensor':'w2','index':[0,4],'delta':.1}]},
        {'op':'set_hidden','unit':4,'weights':[0.,0.,0.,0.,0.,0.,0.,0.],'bias':0.},
        {'op':'scale_output','output':0,'units':[4,5],'scale':1.1},
        {'op':'ridge_readout','units':list(range(16)),'alpha':.01,'blend':.5}]
    packet['operator_semantics']='Every candidate starts from ORIGINAL source. At most12 operators. set_hidden replaces an editable incoming row and bias. scale_output multiplies selected outgoing coefficients (abs(scale)<=4). delta adds coordinate changes. Every intermediate candidate must obey source-relative abs delta1.5 and L2<=5. ridge_readout fits ONLY movement outgoing coefficients and biases using all384 TRAIN examples, with low-urgency weight8 and baseline movement targets there. It solves residual-logit ridge around current weights, then projects total proposal to box/L2. alpha .0001..100; blend0..1. Ridge is ordinary numerical fitting, not evidence of direct weight reading. Hidden changes can affect hazard, so preserve it. Validation and shifted-validation rows are private. Four candidates per round, all evaluated simultaneously; feedback next round. Suggest distinct candidates, including manual surgery and fitting when useful.'
    return {'model':CONFIG['teacher_model'],'store':False,'max_output_tokens':CONFIG['max_output_tokens'],
            'instructions':'Return only strict JSON {"hypothesis":string,"candidates":[{"label":string,"operations":[operator,...]},...]}. Exactly4 candidates, at most12 operators each. No code or markdown. Acquire BOTH opposite passing directions and paired context contrast while retaining hazard and nonpositive-urgency outputs. Context x7 is -1 or+1. A global movement gain does not acquire the conditional skill. You may redesign plastic hidden features and optionally fit their movement readout with the disclosed ridge operator. No test or sibling data are available.',
            'input':json.dumps(packet,allow_nan=False)}


def extract(envelope):
    response=envelope.get('response',{})
    if response.get('status') not in ('completed',None): raise ValueError('response not completed')
    chunks=[c['text'] for item in response.get('output',[]) if item.get('type')=='message' for c in item.get('content',[]) if c.get('type')=='output_text']
    value=json.loads(''.join(chunks))
    if not isinstance(value,dict) or set(value)!={'hypothesis','candidates'} or not isinstance(value['hypothesis'],str) or not isinstance(value['candidates'],list) or len(value['candidates'])!=4:
        raise ValueError('expected hypothesis and exactly4 candidates')
    return value


def process(out,create=True):
    if read(out/'config.json')!=CONFIG: raise ValueError('configuration changed')
    if read(out/'code-lock.json')!=code_hashes(): raise ValueError('registered code/protocol changed')
    pending=[]
    for exp in experiments(out):
        history=[]
        for round in range(1,5):
            stem=name(exp['seed'],round); req=out/'requests'/f'{stem}.json'
            response=req.with_suffix('.response.json'); saved=out/'candidates'/f'{stem}.json'
            expected=make_request(exp,round,history)
            if not req.exists():
                if not create: raise ValueError('missing request')
                write(req,expected)
            elif read(req)!=expected: raise ValueError('request binding changed')
            if not response.exists(): pending.append(str(req)); break
            envelope=read(response)
            if 'response' not in envelope: raise ValueError('transport failure not a candidate')
            binding={'experiment_hash':lab.fingerprint(exp),'request_hash':lab.fingerprint(expected),'response_hash':lab.fingerprint(envelope),'config_hash':lab.fingerprint(CONFIG)}
            record={'seed':exp['seed'],'round':round,'binding':binding,'candidates':[]}
            try:
                proposal=extract(envelope); record['hypothesis']=proposal['hypothesis']
                for index,spec in enumerate(proposal['candidates']):
                    item={'index':index,'specification':spec}
                    try:
                        compiled=lab.compile_candidate(exp['source'],exp['train'],spec)
                        item.update(compiled); item.update(gate(exp['source'],compiled['cell'],exp)); item['valid']=True
                    except (ValueError,TypeError,KeyError,IndexError,np.linalg.LinAlgError) as exc:
                        item.update({'valid':False,'accepted':False,'error':str(exc)})
                    record['candidates'].append(item)
            except (ValueError,TypeError,KeyError) as exc:
                record['error']=str(exc)
                record['candidates']=[{'index':i,'valid':False,'accepted':False,'error':'invalid response consumes scheduled probe slot'} for i in range(4)]
            if saved.exists() and read(saved)!=record: raise ValueError('candidate replay mismatch')
            if not saved.exists(): write(saved,record)
            history.append({'round':round,'hypothesis':record.get('hypothesis'),'error':record.get('error'),
                            'candidates':[{k:v for k,v in c.items() if k!='cell'} for c in record['candidates']]})
    return pending


def measurements(cell,exp,reference=None):
    reference=exp['source'] if reference is None else reference
    return {split:lab.conditional_metrics(cell,exp[split],reference) for split in ('train','validation','validation_shift','test','test_shift')}


def controls(exp):
    source=exp['source']; black=[]; ridge=[]
    for i in range(16):
        patch=lab.random_patch(exp['seed']*100+i,[.4,1.,2.,4.][i%4])
        cell=lab.apply_patch(source,patch)
        black.append({'index':i,'patch':patch,'cell':cell,**gate(source,cell,exp)})
        spec={'label':f'deterministic-ridge-{i}','operations':[{'op':'ridge_readout','units':list(range(16)),'alpha':[.0001,.001,.01,.1][i//4],'blend':[.1,.25,.5,1.][i%4]}]}
        result=lab.compile_candidate(source,exp['train'],spec)
        ridge.append({'index':i,**result,**gate(source,result['cell'],exp)})
    result=[]
    for label,records in [('blackbox16',black),('ridge_grid16',ridge)]:
        best=selected(records); cell=best['cell'] if best else source
        result.append({'name':label,'selected_index':best['index'] if best else None,'trace':records,'cell':cell,'metrics':measurements(cell,exp)})
    gradient=lab.gradient_diagnostic(source,exp['train'],steps=CONFIG['gradient_steps'])
    result.extend([{'name':'no_edit','cell':source,'metrics':measurements(source,exp)},
                   {'name':'gradient600_diagnostic','not_budget_matched':True,'cell':gradient,'metrics':measurements(gradient,exp)}])
    return result


def finish(out):
    if process(out): raise ValueError('teacher requests pending')
    results=[]
    for exp in experiments(out):
        records=[c for r in range(1,5) for c in read(out/'candidates'/f'{name(exp["seed"],r)}.json')['candidates']]
        variants={}
        for kind in ('combined','manual_direct_surgery','ordinary_ridge_fitting'):
            group=records if kind=='combined' else [r for r in records if r.get('mechanism')==kind]
            best=selected(group); patch=best['patch'] if best else {'edits':[]}; cell=lab.apply_patch(exp['source'],patch)
            siblings=[]
            for sibling in exp['siblings']:
                variants_s={'no_edit':sibling}
                for alignment in ('aligned','raw'):
                    variants_s[alignment]=lab.apply_patch(sibling,lab.transfer_patch(patch,exp['source'],sibling,alignment=='aligned'))
                siblings.append({'id':sibling['id'],'variants':{k:{'cell':v,'metrics':measurements(v,exp,sibling)} for k,v in variants_s.items()}})
            variants[kind]={'selected_label':best.get('label') if best else None,'selected_mechanism':best.get('mechanism') if best else None,
                            'attempted_candidates':len(group),'patch':patch,'cell':cell,'metrics':measurements(cell,exp),'siblings':siblings}
        all_controls=controls(exp)
        colony=[]
        for rs in CONFIG['rollout_seeds']:
            baseline=[exp['source']]+exp['siblings']; edited=[variants['combined']['cell']]+[s['variants']['aligned']['cell'] for s in variants['combined']['siblings']]
            colony.append({'seed':rs,'baseline':lab.rollout(baseline,rs),'edited':lab.rollout(edited,rs),'oracle_target':lab.rollout(baseline,rs,oracle=True)})
        results.append({'seed':exp['seed'],'variants':variants,'controls':all_controls,'exploratory_colony':colony})
    value={'config':CONFIG,'results':results}
    if (out/'results.json').exists() and read(out/'results.json')!=value: raise ValueError('results changed')
    write(out/'results.json',value)
    hashes={str(p.relative_to(out)):lab.fingerprint(read(p)) for p in sorted(out.rglob('*.json')) if p.name!='manifest.json'}
    write(out/'manifest.json',{'code_hashes':code_hashes(),'artifact_hashes':hashes,'numpy_version':np.__version__})
    return value


def replay(out):
    manifest=read(out/'manifest.json')
    if manifest['code_hashes']!=code_hashes(): raise ValueError('replay code mismatch')
    for name_,digest in manifest['artifact_hashes'].items():
        if lab.fingerprint(read(out/name_))!=digest: raise ValueError('artifact changed: '+name_)
    expected=read(out/'results.json')
    with tempfile.TemporaryDirectory() as temp:
        destination=Path(temp)/'data'; shutil.copytree(out,destination)
        for p in (destination/'candidates').glob('*.json'): p.unlink()
        (destination/'results.json').unlink(); (destination/'manifest.json').unlink()
        actual=finish(destination)
        if actual!=expected: raise ValueError('numeric replay mismatch')
    return {'exact_replay':True,'results_hash':lab.fingerprint(expected)}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['prepare','advance','finish','replay']); parser.add_argument('--out',type=Path,default=ROOT/'data'); args=parser.parse_args(); out=args.out.resolve()
    if args.command=='prepare':
        if out.exists() and any(out.iterdir()): raise ValueError('prepare requires empty directory')
        write(out/'config.json',CONFIG); write(out/'code-lock.json',code_hashes())
        for seed in CONFIG['seeds']: write(out/'experiments'/f'seed-{seed}.json',lab.generate_experiment(seed))
        pending=process(out); print('\n'.join(pending))
    elif args.command=='advance': print('\n'.join(process(out)))
    elif args.command=='finish': finish(out); print(str(out/'results.json'))
    else: print(json.dumps(replay(out)))

if __name__=='__main__': main()
