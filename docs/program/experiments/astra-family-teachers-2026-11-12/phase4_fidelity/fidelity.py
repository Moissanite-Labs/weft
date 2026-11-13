#!/usr/bin/env python3
"""Exact-scored numeric readout/mechanical editing probes, no API client."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import numpy as np

VERSION='fidelity-v1'
BASE=Path(__file__).resolve().parent.parent

def write(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(x,separators=(',',':'),allow_nan=False)+'\n')
def read(p):return json.loads(p.read_text())
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def forward(c,x):return np.tanh(np.asarray(x)@np.asarray(c['w1']).T+c['b1'])@np.asarray(c['w2']).T+c['b2']
def permute(c,seed=9001):
 result=copy.deepcopy(c); p=np.random.default_rng(seed).permutation(len(c['b1']))
 result['w1']=np.asarray(c['w1'])[p].tolist();result['b1']=np.asarray(c['b1'])[p].tolist();result['w2']=np.asarray(c['w2'])[:,p].tolist()
 return result,p.tolist()
def top_sets(matrix):
 norms=np.linalg.norm(matrix,axis=1); threshold=np.sort(norms)[-3]
 return {'required':np.flatnonzero(norms>threshold+1e-12).tolist(),'allowed':np.flatnonzero(norms>=threshold-1e-12).tolist(),'norms':norms.tolist()}
def correct_top(answer,oracle):
 return isinstance(answer,list) and len(answer)==3 and all(type(x) is int for x in answer) and len(set(answer))==3 and set(oracle['required'])<=set(answer)<=set(oracle['allowed'])

def readout(size,precision,seed):
 rng=np.random.default_rng(seed); m=np.zeros((size,size)); rows=rng.choice(size,3,replace=False)
 # Strong sparse rows test readout, rather than hiding a near-tie as a model error.
 for rank,row in enumerate(rows):
  cols=rng.choice(size,8,replace=False);m[row,cols]=rng.normal(0,1,8)*(rank+2)
 decimals={'raw':6,'round2':2,'round5':5}[precision]
 shown=np.round(m,decimals);shown[shown==0]=0
 # Use integer zero literals to keep dense serialization compact.
 records=[{'row':i,'values':[0 if v==0 else float(v) for v in values]} for i,values in enumerate(shown)]
 oracle=top_sets(shown)
 return {'task':'Return strict JSON {"rows":[three zero-based row labels]} identifying the three largest Euclidean row norms. Order does not matter; if tied at the cutoff any tied row is valid.',
         'shape':[size,size],'matrix_rows':records}, {'kind':'A','size':size,'precision':precision,'seed':seed,'planted_rows':rows.tolist(),'original':m.tolist(),'shown':shown.tolist(),'oracle':oracle,'unrounded_oracle':top_sets(m),'quantization_changes_answer':set(oracle['allowed'])!=set(top_sets(m)['allowed'])}

def prepare(out,calibration,organism):
 if list((out/'requests').glob('*.response.json')):raise ValueError('Cannot regenerate after responses')
 protocol={'version':VERSION,'budget':22,'A':{'calls':12,'sizes':[64,256],'precisions':{'raw':6,'round2':2,'round5':5},'seeds':[1103,1129],'score':'top3 on displayed rounded values; cutoff ties allowed','scope':'Sparse planted readout ceiling; not general dense weight understanding'},
 'B':{'calls':6,'operations':['signflip','zerorow','scalerow'],'score':'full specified row equals oracle atol1e-6; pure mechanical editing distinct from frozen-core policy intervention'},
 'C':{'calls':2,'score':'fresh-input agreement with returned dominant-input threshold rule; no unique semantics claim'},
 'D':{'calls':2,'score':'planted equivalent boolean plus numerical forward check'},'model':'gpt-6-astra','store':False,'selection':'all fixed probes; no candidate selection','C_D_inputs_seed':7731,'C_D_n':2048}
 # Protocol artifact precedes request generation.
 write(out/'PROTOCOL.json',protocol)
 classifier=read(calibration)['source']; organism_cell=read(organism)['source']
 sibling,order=permute(classifier)
 x=np.random.default_rng(7731).uniform(-1,1,(2048,4)); logits=forward(classifier,x)
 write(out/'checkpoints.json',{'classifier':classifier,'classifier_permuted':sibling,'permutation':order,'organism':organism_cell,'fresh_inputs':x.tolist()})
 probes=[]
 for size in (64,256):
  for precision in ('raw','round2','round5'):
   for seed in (1103,1129):
    packet,oracle=readout(size,precision,seed)
    probes.append((f'A-{size}-{precision}-{seed}',packet,oracle,1000))
 for name,cell in (('classifier',classifier),('organism',organism_cell)):
  for operation in ('signflip','zerorow','scalerow'):
   row=2;tensor='w1'; before=np.asarray(cell[tensor][row]); factor={'signflip':-1.,'zerorow':0.,'scalerow':1.25}[operation]
   after=before*factor;edited=copy.deepcopy(cell);edited[tensor][row]=after.tolist()
   packet={'task':'Pure mechanical copying/editing, not a policy-improvement task. Return strict JSON {"edited_row":[all numeric row values]}. Apply exactly the specified operation to the specified zero-based row. No other transformation.',
           'weights':cell,'operation':operation,'tensor':tensor,'row':row,'scale_factor':factor,'atol':1e-6}
   oracle={'kind':'B','model':name,'operation':operation,'tensor':tensor,'row':row,'factor':factor,'before':cell,'after':edited,'expected_row':after.tolist(),'atol':1e-6}
   probes.append((f'B-{name}-{operation}',packet,oracle,6000))
 architecture='h=tanh(x @ w1.T+b1); logits=h @ w2.T+b2; class=argmax(logits); inputs are four unnamed numeric coordinates; classes are 0 and 1.'
 for name,cell in (('original',classifier),('permuted',sibling)):
  packet={'task':'Infer the dominant input coordinate and a threshold classifier from weights alone. Return strict JSON {"dominant_input_index":integer,"threshold":number,"class_above":0 or 1,"class_below":0 or 1}. This asks about numerical input-output behavior, not real-world meaning. No examples or labels supplied.', 'architecture':architecture,'weights':cell}
  probes.append((f'C-{name}',packet,{'kind':'C','fresh_inputs':x.tolist(),'network_classes':np.argmax(forward(cell,x),axis=1).tolist(),'model':name},6000))
 changed=copy.deepcopy(classifier);changed['b2'][0]+=8
 for name,other in (('permuted',sibling),('changed',changed)):
  difference=float(np.max(np.abs(logits-forward(other,x))))
  packet={'task':'Determine whether these two networks compute the same logits for every input, allowing floating-point tolerance 1e-9. Return strict JSON {"equivalent":true or false}.', 'architecture':architecture,'network_a':classifier,'network_b':other}
  probes.append((f'D-{name}',packet,{'kind':'D','equivalent':name=='permuted','forward_max_abs_difference':difference,'forward_class_agreement':float(np.mean(np.argmax(logits,1)==np.argmax(forward(other,x),1))),'a':classifier,'b':other,'fresh_inputs':x.tolist()},6000))
 assert len(probes)==22
 for name,packet,oracle,tokens in probes:
  request={'model':'gpt-6-astra','store':False,'max_output_tokens':tokens,'instructions':'Return only the requested strict JSON object. No markdown, prose, commentary or code. Use zero-based indices.','input':json.dumps(packet,separators=(',',':'))}
  write(out/'requests'/f'{name}.json',request)
  write(out/'oracles'/f'{name}.json',oracle)
 files={str(p.relative_to(out)):digest(read(p)) for directory in ('requests','oracles') for p in sorted((out/directory).glob('*.json'))}
 files.update({name:digest(read(out/name)) for name in ('PROTOCOL.json','checkpoints.json')})
 write(out/'manifest.json',{'version':VERSION,'artifacts':files,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sources':{'calibration':digest(read(calibration)),'organism':digest(read(organism))}})
 sizes=[p.stat().st_size for p in (out/'requests').glob('*.json')]
 print(json.dumps({'requests':len(probes),'min_request_bytes':min(sizes),'max_request_bytes':max(sizes),'total_request_bytes':sum(sizes)}))

def extract(envelope):
 response=envelope.get('response',{})
 if response.get('status') not in (None,'completed'):raise ValueError('response not completed')
 parts=[c['text'] for item in response.get('output',[]) if item.get('type')=='message' for c in item.get('content',[]) if c.get('type')=='output_text']
 if not parts:raise ValueError('missing output_text')
 value=json.loads(''.join(parts))
 if not isinstance(value,dict):raise ValueError('Expected JSON object')
 return value

def score(answer,oracle):
 kind=oracle['kind']
 if kind=='A':
  if set(answer)!={'rows'}:raise ValueError('Wrong schema')
  return {'correct':correct_top(answer['rows'],oracle['oracle']),'quantization_changes_answer':oracle['quantization_changes_answer']}
 if kind=='B':
  if set(answer)!={'edited_row'}:raise ValueError('Wrong schema')
  row=answer['edited_row']
  if not isinstance(row,list) or not all(type(v) in (int,float) and np.isfinite(v) for v in row):raise ValueError('non-numeric edited row')
  expected=np.asarray(oracle['expected_row']); actual=np.asarray(row)
  if actual.shape!=expected.shape:return {'correct':False,'shape_mismatch':True}
  delta=float(np.max(np.abs(actual-expected)))
  return {'correct':delta<=oracle['atol'],'max_abs_error':delta}
 if kind=='C':
  if set(answer)!={'dominant_input_index','threshold','class_above','class_below'}:raise ValueError('Wrong schema')
  index=answer['dominant_input_index'];threshold=answer['threshold']
  if type(index) is not int or index not in range(4) or type(threshold) not in (int,float) or not np.isfinite(threshold):raise ValueError('invalid rule')
  if type(answer['class_above']) is not int or type(answer['class_below']) is not int or answer['class_above'] not in (0,1) or answer['class_below'] not in (0,1):raise ValueError('invalid classes')
  predicted=np.where(np.asarray(oracle['fresh_inputs'])[:,index]>threshold,answer['class_above'],answer['class_below'])
  return {'agreement':float(np.mean(predicted==oracle['network_classes'])),'rule':answer,'scope':'Approximate one-coordinate numerical rule, not unique semantics'}
 if kind=='D':
  if set(answer)!={'equivalent'} or type(answer['equivalent']) is not bool:raise ValueError('Wrong schema')
  return {'correct':answer['equivalent']==oracle['equivalent'],'ground_truth':oracle['equivalent'],'forward_max_abs_difference':oracle['forward_max_abs_difference'],'forward_class_agreement':oracle['forward_class_agreement']}
 raise ValueError('unknown kind')

def evaluate(out,replay=False):
 manifest=read(out/'manifest.json')
 if manifest['code_sha256']!=hashlib.sha256(Path(__file__).read_bytes()).hexdigest():raise ValueError('Code changed')
 for name,expected in manifest['artifacts'].items():
  if digest(read(out/name))!=expected:raise ValueError('Artifact changed '+name)
 results=[];pending=[]
 for oracle_path in sorted((out/'oracles').glob('*.json')):
  name=oracle_path.stem; response=out/'requests'/f'{name}.response.json'; oracle=read(oracle_path)
  if not response.exists():pending.append(name);continue
  row={'probe':name,'kind':oracle['kind'],'response_sha256':digest(read(response))}
  try:answer=extract(read(response)); row.update({'valid':True,'answer':answer,**score(answer,oracle)})
  except (ValueError,TypeError,KeyError,IndexError) as exc:row.update({'valid':False,'error':str(exc)})
  results.append(row)
 report={'version':VERSION,'results':results,'pending':pending,'completed':len(results),'expected':22,
         'interpretation':'Exact probes establish readout/mechanical fidelity only; sparse strong-signal A is a ceiling test. C supports numerical functional inference, not unique semantics. No statistical significance claim.'}
 if replay:
  if not (out/'results.json').exists():raise ValueError('Replay requires existing results')
  if read(out/'results.json')!=report:raise ValueError('Replay result mismatch')
 else:write(out/'results.json',report)
 print(json.dumps({'completed':len(results),'pending':len(pending),'replay':replay}))
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','evaluate','replay']);p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'data');p.add_argument('--calibration',type=Path,default=BASE/'data/calibration/experiment.json');p.add_argument('--organism',type=Path,default=BASE/'data/experiments/seed-17.json');a=p.parse_args()
 if a.command=='prepare':prepare(a.out,a.calibration,a.organism)
 else:evaluate(a.out,a.command=='replay')
if __name__=='__main__':main()
