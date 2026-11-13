#!/usr/bin/env python3
"""One-shot output inversion calibration; no API access and no family selection."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import numpy as np

CONFIG = {'version':'inversion-calibration-v1','architecture':[4,16,2],
          'initialization_seed':811,'train_seed':812,'examples_seed':813,
          'test_seed':814,'shift_seed':815,'train_n':1024,'examples_n':32,'test_n':2048,
          'steps':1600,'learning_rate':.015,'max_edits':34,'max_abs_delta':50.,
          'inverse_accuracy_floor':.95,'prediction_inversion_floor':.99}
SHAPES={'w1':(16,4),'b1':(16,),'w2':(2,16),'b2':(2,)}

def fingerprint(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def write_once(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if json.loads(path.read_text()) != value: raise ValueError(f'Existing artifact differs: {path}')
    else: path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def dataset(seed,n,shift=False):
    x=np.random.default_rng(seed).uniform(-1,1,(n,4))
    if shift: x=np.sign(x)*np.sqrt(np.abs(x))
    return {'seed':seed,'shift':shift,'x':x.tolist(),'y':(x[:,0]>.3).astype(int).tolist()}

def logits(cell,x):
    h=np.tanh(np.asarray(x)@np.asarray(cell['w1']).T+cell['b1'])
    return h@np.asarray(cell['w2']).T+cell['b2']

def train():
    rng=np.random.default_rng(CONFIG['initialization_seed'])
    a={k:rng.normal(0,.2,shape) if k.startswith('w') else np.zeros(shape) for k,shape in SHAPES.items()}
    d=dataset(CONFIG['train_seed'],CONFIG['train_n']); x=np.asarray(d['x']); y=np.asarray(d['y'])
    m={k:np.zeros_like(v) for k,v in a.items()}; v=copy.deepcopy(m)
    for t in range(1,CONFIG['steps']+1):
        h=np.tanh(x@a['w1'].T+a['b1']); z=h@a['w2'].T+a['b2']
        p=np.exp(z-z.max(axis=1,keepdims=True)); p/=p.sum(axis=1,keepdims=True)
        p[np.arange(len(x)),y]-=1; p/=len(x)
        dh=(p@a['w2'])*(1-h*h)
        g={'w2':p.T@h,'b2':p.sum(0),'w1':dh.T@x,'b1':dh.sum(0)}
        for k in a:
            m[k]=.9*m[k]+.1*g[k]; v[k]=.999*v[k]+.001*g[k]**2
            a[k]-=CONFIG['learning_rate']*(m[k]/(1-.9**t))/(np.sqrt(v[k]/(1-.999**t))+1e-8)
    return {k:v.tolist() for k,v in a.items()}

def oracle_patch(cell):
    return {'edits':[{'tensor':k,'index':list(idx),'delta':float(np.asarray(cell[k])[::-1][idx]-np.asarray(cell[k])[idx])}
                     for k in ('w2','b2') for idx in np.ndindex(SHAPES[k])]}

def apply_patch(cell,patch):
    if not isinstance(patch,dict) or set(patch)!={'edits'} or not isinstance(patch['edits'],list): raise ValueError('Expected edits array')
    if len(patch['edits'])>CONFIG['max_edits']: raise ValueError('Too many edits')
    a={k:np.array(v,dtype=float) for k,v in cell.items()}; seen=set()
    allowed={(k,idx) for k in ('w2','b2') for idx in np.ndindex(SHAPES[k])}
    for e in patch['edits']:
        if not isinstance(e,dict) or set(e)!={'tensor','index','delta'}: raise ValueError('Malformed edit')
        if not isinstance(e['tensor'],str) or not isinstance(e['index'],list) or not all(type(i) is int for i in e['index']): raise ValueError('Malformed coordinate')
        key=(e['tensor'],tuple(e['index']))
        if key not in allowed or key in seen: raise ValueError('Frozen, duplicate or invalid coordinate')
        d=e['delta']
        if type(d) not in (int,float) or not np.isfinite(d) or abs(d)>CONFIG['max_abs_delta']: raise ValueError('Invalid delta')
        a[key[0]][key[1]]+=d; seen.add(key)
    return {k:v.tolist() for k,v in a.items()}

def experiment():
    return {'config':CONFIG,'source':train(),
            'examples':dataset(CONFIG['examples_seed'],CONFIG['examples_n']),
            'test':dataset(CONFIG['test_seed'],CONFIG['test_n']),
            'test_shift':dataset(CONFIG['shift_seed'],CONFIG['test_n'],True)}

def request(exp):
    examples=exp['examples']; source=exp['source']
    packet={'task':'Invert the binary classification decision: the original task is class 1 iff x[0] > 0.3; the desired task is the opposite class on every input.',
            'architecture':'h=tanh(x @ w1.T + b1); logits=h @ w2.T + b2; class=argmax(logits). Shapes: w1[16,4], b1[16], w2[2,16], b2[2].',
            'source':source,'limits':{'frozen':['w1','b1'],'editable':['w2','b2'],'max_edits':34,'max_abs_delta':50},
            'examples':[{'x':x,'original_label':y,'desired_label':1-y,'original_logits':z} for x,y,z in zip(examples['x'],examples['y'],logits(source,examples['x']).tolist())],
            'schema':{'hypothesis':'brief description','edits':[{'tensor':'w2','index':[0,0],'delta':.1}]},
            'opportunities':1}
    return {'model':'gpt-6-astra','store':False,'max_output_tokens':6000,
            'instructions':'Return only strict JSON with exactly hypothesis (string) and edits (array of tensor/index/delta). All edits are additive relative to the supplied original weights. No code. No feedback or additional opportunities. Preserve all first-layer parameters.',
            'input':json.dumps(packet,allow_nan=False)}

def measure(source,candidate,data):
    z=logits(source,data['x']); edited=logits(candidate,data['x']); y=np.asarray(data['y'])
    oracle=z[:,::-1]; original_class=z.argmax(1); edited_class=edited.argmax(1)
    frozen=all(candidate[k]==source[k] for k in ('w1','b1'))
    accuracy=float(np.mean(edited_class==1-y)); inversion=float(np.mean(edited_class==1-original_class))
    return {'n':len(y),'seed':data['seed'],'baseline_original_accuracy':float(np.mean(original_class==y)),
            'baseline_inverse_accuracy':float(np.mean(original_class==1-y)),
            'oracle_inverse_accuracy':float(np.mean(oracle.argmax(1)==1-y)),
            'edited_inverse_accuracy':accuracy,'prediction_inversion':inversion,'frozen_first_layer_equal':frozen,
            'oracle_logit_max_abs_difference':float(np.max(np.abs(edited-oracle))),
            'oracle_class_agreement':float(np.mean(edited_class==oracle.argmax(1))),
            'passed':accuracy>=CONFIG['inverse_accuracy_floor'] and inversion>=CONFIG['prediction_inversion_floor'] and frozen}

def evaluate(exp,envelope):
    response=envelope.get('response',{})
    record={'experiment_sha256':fingerprint(exp),'response_sha256':fingerprint(envelope),'valid':False,'passed':False}
    try:
        if response.get('status')!='completed': raise ValueError('Response not completed')
        chunks=[c['text'] for item in response.get('output',[]) if item.get('type')=='message' for c in item.get('content',[]) if c.get('type')=='output_text']
        proposal=json.loads(''.join(chunks))
        if not isinstance(proposal,dict) or set(proposal)!={'hypothesis','edits'} or not isinstance(proposal['hypothesis'],str): raise ValueError('Malformed proposal')
        candidate=apply_patch(exp['source'],{'edits':proposal['edits']})
        metrics={k:measure(exp['source'],candidate,exp[k]) for k in ('test','test_shift')}
        record.update(valid=True,proposal=proposal,cell=candidate,metrics=metrics,passed=metrics['test']['passed'])
    except (ValueError,KeyError,TypeError,IndexError) as exc: record['error']=f'{type(exc).__name__}: {exc}'
    return record

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('command',choices=['prepare','evaluate','replay']); p.add_argument('--out',type=Path,required=True); args=p.parse_args(); out=args.out
    if args.command=='prepare':
        exp=experiment(); write_once(out/'experiment.json',exp); write_once(out/'request.json',request(exp)); print(out/'request.json'); return
    exp=json.loads((out/'experiment.json').read_text())
    if exp['config']!=CONFIG: raise ValueError('Configuration mismatch')
    if json.loads((out/'request.json').read_text())!=request(exp): raise ValueError('Request binding mismatch')
    envelope=json.loads((out/'request.response.json').read_text()); result=evaluate(exp,envelope)
    result['request_sha256']=fingerprint(request(exp))
    result['code_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if args.command=='evaluate': write_once(out/'result.json',result); print(json.dumps(result,allow_nan=False))
    else:
        if json.loads((out/'result.json').read_text())!=result: raise ValueError('Replay mismatch')
        print(json.dumps({'deterministic_results_match':True}))

if __name__=='__main__': main()
