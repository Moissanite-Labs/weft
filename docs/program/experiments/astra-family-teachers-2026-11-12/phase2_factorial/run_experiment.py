#!/usr/bin/env python3
"""Offline, append-only teacher request orchestration; never imports an API client."""
from __future__ import annotations
import argparse
import copy
import json
import platform
import sys
from pathlib import Path
import numpy as np
import lab

ARMS = ('weights_hidden', 'weights_only', 'hidden_only', 'neither')
CONFIG = {'rounds': 2, 'rounds_by_arm': {arm:2 for arm in ARMS}, 'examples':48, 'transcript_significant_digits':8, 'source_seeds':[71,89,107,131,163], 'random_draws': 32, 'rollout_seeds': [1701,1702,1703], 'hazard_relative_tolerance': .02,
          'hazard_absolute_tolerance': .0002, 'low_urgency_drift_mse_budget': .0005,
          'target_min_improvement': 1e-8, 'selection_metric': 'movement_mse',
          'teacher_model': 'gpt-6-astra', 'random_distribution': 'posthoc, never selected'}


def native(x):
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, np.generic): return x.item()
    raise TypeError(type(x).__name__)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False, default=native)+'\n')


def read(path): return json.loads(path.read_text())
def stem(seed, arm, round): return f'seed-{seed}.{arm}.round-{round}'
def experiments(out): return [(p, read(p)) for p in sorted((out/'experiments').glob('*.json'))]


def gate(source, candidate, validation):
    before, after = lab.evaluate(source, validation), lab.evaluate(candidate, validation)
    x = np.asarray(validation['x'])
    low = x[:, 6] <= 0
    drift = float(np.mean((lab.predict(candidate, x[low])[:, :2]-lab.predict(source, x[low])[:, :2])**2))
    tests = {'target_improved': after['active_movement_mse'] < before['active_movement_mse']-CONFIG['target_min_improvement'] and after['movement_mse'] < before['movement_mse']-CONFIG['target_min_improvement'],
             'hazard_preserved': after['hazard_mse'] <= before['hazard_mse']+max(CONFIG['hazard_absolute_tolerance'], CONFIG['hazard_relative_tolerance']*before['hazard_mse']),
             'low_urgency_preserved': drift <= CONFIG['low_urgency_drift_mse_budget']}
    return {'accepted': all(tests.values()), 'checks': tests, 'validation_metrics': after, 'low_urgency_drift_mse': drift}


def transcript(value):
    if isinstance(value,float): return float(format(value,'.8g'))
    if isinstance(value,dict): return {k:transcript(v) for k,v in value.items()}
    if isinstance(value,list): return [transcript(v) for v in value]
    return value


def request(out, exp, arm, round, history):
    packet = lab.teacher_packet(exp['source'], exp['train'], exp['validation'], examples=CONFIG['examples'])
    weights = arm in ('weights_hidden','weights_only')
    hidden = arm in ('weights_hidden','hidden_only')
    if not hidden:
        for example in packet['examples']: example.pop('hidden',None)
    if not weights:
        for tensor,shape in lab.SHAPES.items():
            packet['cell'][tensor]={'shape':list(shape),'values':'withheld'}
    packet['visibility']={'numerical_weights':weights,'hidden_activations':hidden}
    packet['previous_proposals']=history
    packet['preregistered_gate']=CONFIG
    packet['proposal_number']=round
    value={'model':CONFIG['teacher_model'],'store':False,'max_output_tokens':6000,
           'instructions':('You are the gpt-6-astra policy-editing teacher. Return only strict JSON with exactly hypothesis '
                           '(a string) and edits (an array of {tensor,index,delta}). No code or markdown. Every delta is '
                           'cumulative relative to the ORIGINAL source cell, never relative to prior edits. Improve active '
                           'movement while preserving hazard and low-urgency behavior. Frozen coordinates and all limits '
                           'are mandatory. You have two proposals total. Prior validation feedback is the only feedback; '
                           'no held-out tests or siblings are available. Some evidence fields may be deliberately withheld. '
                           'Supplied numerical values are rounded to eight significant digits; the evaluator uses original precision.'),
           'input':json.dumps(transcript(packet),allow_nan=False,separators=(',',':'))}
    path=out/'requests'/f'{stem(exp["seed"],arm,round)}.json'
    if path.exists():
        if read(path)!=value: raise ValueError('Request reconstruction mismatch: '+str(path))
    else: write(path,value)
    return path


def extract_response(envelope):
    response = envelope.get('response', {})
    if response.get('status') not in (None, 'completed'): raise ValueError('API response not completed')
    chunks = [c['text'] for item in response.get('output', []) if item.get('type') == 'message'
              for c in item.get('content', []) if c.get('type') == 'output_text']
    if not chunks: raise ValueError('no output_text in API response')
    value = json.loads(''.join(chunks))
    if not isinstance(value, dict) or set(value) != {'hypothesis','edits'} or not isinstance(value['hypothesis'], str):
        raise ValueError('expected exactly hypothesis:string and edits:array')
    return value


def process(out, create_requests=True):
    if (out/'config.json').exists() and read(out/'config.json') != CONFIG:
        raise ValueError('configuration mismatch')
    pending = []
    for _, exp in experiments(out):
        for arm in ARMS:
            history = []
            for round in range(1, CONFIG['rounds_by_arm'][arm]+1):
                name = stem(exp['seed'], arm, round)
                req = out/'requests'/f'{name}.json'
                result_path = out/'candidates'/f'{name}.json'
                response_path = req.with_suffix('.response.json')
                if req.exists() or create_requests: request(out, exp, arm, round, history)
                else: break
                if not response_path.exists():
                    pending.append(str(req)); break
                if 'response' not in read(response_path):
                    raise ValueError(f'Transport/API error is not a proposal: {response_path}')
                binding = {'request_sha256':lab.fingerprint(read(req)),
                           'experiment_sha256':lab.fingerprint(exp),
                           'config_sha256':lab.fingerprint(CONFIG)}
                if result_path.exists():
                    record = read(result_path)
                    if any(record.get(k) != v for k,v in binding.items()):
                        raise ValueError(f'Candidate input binding mismatch: {result_path}')
                    if record['response_sha256'] != lab.fingerprint(read(response_path)):
                        raise ValueError(f'Archived response changed: {response_path}')
                else:
                    record = {**binding, 'seed': exp['seed'], 'arm': arm, 'round': round,
                              'response_sha256': lab.fingerprint(read(response_path)), 'accepted': False}
                    try:
                        proposal = extract_response(read(response_path))
                        patch = {'edits': proposal['edits']}
                        candidate = lab.apply_patch(exp['source'], patch)
                        record.update({'proposal': proposal, 'patch': patch, 'cell': candidate,
                                       **gate(exp['source'], candidate, exp['validation']), 'valid': True})
                    except (ValueError, TypeError, KeyError, IndexError) as exc:
                        record.update({'valid': False, 'error': f'{type(exc).__name__}: {exc}'})
                    write(result_path, record)
                # Never expose candidate weights in feedback to behavior-only arm.
                history.append({k: v for k, v in record.items() if k in
                                ('round','proposal','valid','error','accepted','checks','validation_metrics','low_urgency_drift_mse')})
    return pending


def measurements(cell, exp, reference=None):
    reference = exp['source'] if reference is None else reference
    result = {}
    for split in ('train','validation','test','test_shift'):
        x = np.asarray(exp[split]['x'])
        low = x[:,6] <= 0
        metrics = lab.evaluate(cell,exp[split])
        metrics['unchanged_context_behavior_drift_mse'] = float(np.mean((lab.predict(cell,x[low])[:,:2]-lab.predict(reference,x[low])[:,:2])**2))
        metrics['frozen_core_equal'] = bool(np.array_equal(np.asarray(cell['w1'])[:4],np.asarray(reference['w1'])[:4]) and np.array_equal(np.asarray(cell['b1'])[:4],np.asarray(reference['b1'])[:4]))
        result[split] = metrics
    return result


def finish(out):
    pending = process(out)
    expected = len(experiments(out))*sum(CONFIG['rounds_by_arm'].values())
    if pending or len(list((out/'candidates').glob('*.json'))) != expected:
        raise ValueError('All teacher rounds must be processed before finish; pending: '+', '.join(pending))
    results = []
    for _, exp in experiments(out):
        source = exp['source']
        baseline = {'name':'no_edit','cell':source,'metrics':measurements(source,exp)}
        gradient = lab.gradient_diagnostic(source,exp['train'])
        evolution = lab.local_evolution(source,exp['validation'],proposals=2,seed=exp['seed']+9000)
        eligible = []
        for item in evolution['trace']:
            check = gate(source, lab.apply_patch(source,item['patch']),exp['validation'])
            item['gate'] = check
            if check['accepted']: eligible.append(item)
        evolution['patch'] = min(eligible,key=lambda item:item['gate']['validation_metrics'][CONFIG['selection_metric']])['patch'] if eligible else {'edits':[]}
        evolution['validation_loss'] = lab.evaluate(lab.apply_patch(source,evolution['patch']),exp['validation'])['loss']
        evolution['validation_movement_mse'] = lab.evaluate(lab.apply_patch(source,evolution['patch']),exp['validation'])['movement_mse']
        evolution['selection'] = 'same gate and movement_mse as teacher; two candidates'
        evo_cell = lab.apply_patch(source,evolution['patch'])
        controls = [baseline, {'name':'gradient_diagnostic','budget_matched':False,'cell':gradient,'metrics':measurements(gradient,exp)},
                    {'name':'local_evolution','trace':evolution,'cell':evo_cell,'metrics':measurements(evo_cell,exp)}]
        for arm in ARMS:
            records = [read(out/'candidates'/f'{stem(exp["seed"],arm,r)}.json') for r in range(1,CONFIG['rounds_by_arm'][arm]+1)]
            accepted = [r for r in records if r['accepted']]
            best = min(accepted,key=lambda r:r['validation_metrics'][CONFIG['selection_metric']]) if accepted else None
            patch = best['patch'] if best else {'edits':[]}
            edited = lab.apply_patch(source,patch)
            siblings = []
            for sibling in exp['siblings']:
                variants = {'no_edit':sibling}
                for alignment in ('aligned','raw'):
                    transferred = lab.transfer_patch(patch,source,sibling,aligned=alignment=='aligned')
                    variants[alignment] = lab.apply_patch(sibling,transferred)
                siblings.append({'id':sibling['id'],'variants':{k:{'cell':v,'metrics':measurements(v,exp,sibling)} for k,v in variants.items()}})
            randoms = []
            for draw in range(CONFIG['random_draws']):
                rp = lab.random_patch(exp['seed']*10000+draw,lab.patch_norm(patch),support=patch)
                rc = lab.apply_patch(source,rp)
                transfers = []
                for sibling in exp['siblings']:
                    transfers.append({alignment: measurements(lab.apply_patch(sibling,lab.transfer_patch(rp,source,sibling,aligned=alignment=='aligned')),exp,sibling)
                                      for alignment in ('aligned','raw')})
                randoms.append({'draw':draw,'patch':rp,'cell':rc,'metrics':measurements(rc,exp),'siblings':transfers})
            aligned_cells = [s['variants']['aligned']['cell'] for s in siblings]
            result = {'seed':exp['seed'],'arm':arm,'selected_round':best['round'] if best else None,
                      'selection':'validation only; no accepted candidate means no edit','patch':patch,
                      'round1': {k:v for k,v in records[0].items() if k != 'cell'},
                      'round1_metrics':measurements(records[0].get('cell',source),exp),
                      'source':{'cell':edited,'metrics':measurements(edited,exp)},'siblings':siblings,
                      'controls':controls,'random_distribution':{'posthoc_not_selected':True,'draws':randoms},
                      'exploratory_rollout':[{'seed':rs,'no_edit':lab.rollout([source]+exp['siblings'],seed=rs),
                                             'edited_aligned':lab.rollout([edited]+aligned_cells,seed=rs),
                                             'edited_raw':lab.rollout([edited]+[s['variants']['raw']['cell'] for s in siblings],seed=rs)} for rs in CONFIG['rollout_seeds']]}
            results.append(result)
    paired = []
    comparisons=[('weight_effect_hidden_present','weights_hidden','hidden_only'),
                 ('weight_effect_hidden_absent','weights_only','neither'),
                 ('activation_effect_weights_present','weights_hidden','weights_only'),
                 ('activation_effect_weights_absent','hidden_only','neither')]
    for _, exp in experiments(out):
        by_arm={r['arm']:r for r in results if r['seed']==exp['seed']}
        for split in ('test','test_shift'):
            baseline=lab.evaluate(exp['source'],exp[split])['active_movement_mse']
            for stage in ('round1','selected'):
                for label,exposed,withheld in comparisons:
                    def metric(arm):
                        r=by_arm[arm]
                        return r['round1_metrics'][split] if stage=='round1' else r['source']['metrics'][split]
                    a,b=metric(exposed),metric(withheld)
                    paired.append({'seed':exp['seed'],'split':split,'stage':stage,'contrast':label,
                                   'exposed_arm':exposed,'withheld_arm':withheld,
                                   'active_mse_exposed':a['active_movement_mse'],'active_mse_withheld':b['active_movement_mse'],
                                   'active_improvement_advantage_percentage_points':100*(b['active_movement_mse']-a['active_movement_mse'])/baseline,
                                   'low_urgency_drift_exposed':a['unchanged_context_behavior_drift_mse'],
                                   'low_urgency_drift_withheld':b['unchanged_context_behavior_drift_mse']})
    write(out/'results.json',{'config':CONFIG,'results':results,'factorial_contrasts':paired})
    hashes = {str(p.relative_to(out)):lab.fingerprint(read(p)) for p in sorted(out.rglob('*.json')) if p.name != 'manifest.json'}
    write(out/'manifest.json',{'config':CONFIG,'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,
                              'lab_version':lab.VERSION,'artifact_sha256':hashes,
                              'code_sha256':{p.name:__import__('hashlib').sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(lab.__file__))},
                              'replay':'python run_experiment.py replay --out '+str(out)})
    return results


def validate_replay(out):
    if not (out/'results.json').exists():
        raise ValueError('Replay requires existing results.json')
    if not (out/'manifest.json').exists():
        raise ValueError('Replay requires existing manifest.json')
    manifest = read(out/'manifest.json')
    if manifest['config'] != CONFIG:
        raise ValueError('Replay configuration mismatch')
    import hashlib
    for path in (Path(__file__),Path(lab.__file__)):
        if manifest['code_sha256'].get(path.name) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError('Replay code hash mismatch: '+path.name)
    for name, expected in manifest['artifact_sha256'].items():
        path = out/name
        if not path.exists() or lab.fingerprint(read(path)) != expected:
            raise ValueError('Replay artifact hash mismatch: '+name)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('prepare','advance','finish','replay'))
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--seeds',type=int,nargs='+',default=CONFIG['source_seeds'])
    args=parser.parse_args()
    out=args.out.resolve()
    if args.command=='prepare':
        if (out/'config.json').exists() and read(out/'config.json') != CONFIG: raise ValueError('configuration changed')
        write(out/'config.json',CONFIG)
        for seed in args.seeds:
            path=out/'experiments'/f'seed-{seed}.json'
            if not path.exists(): write(path,lab.generate_experiment(seed))
        print('\n'.join(process(out)))
    elif args.command=='advance': print('\n'.join(process(out)))
    elif args.command=='finish': finish(out); print(out/'results.json')
    else:
        # Recompute in an isolated directory; preserve every original artifact.
        import tempfile
        import shutil
        validate_replay(out)
        old = read(out/'results.json')
        with tempfile.TemporaryDirectory(prefix='astra-replay-') as tmp:
            replay_out = Path(tmp)
            for directory in ('experiments','requests'):
                shutil.copytree(out/directory,replay_out/directory)
            finish(replay_out)
            same = old is None or old==read(replay_out/'results.json')
        print(json.dumps({'deterministic_results_match':same,'results':str(out/'results.json')}))
        if not same: raise SystemExit(1)


if __name__=='__main__': main()
