#!/usr/bin/env python3
"""Local finite-anchor linear algebra diagnostic; no API or training workload."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import time
import numpy as np

CONFIG={'version':'geometry-diagnostic-v1','input_dim':3,'hidden':24,'keep_n':8,'probe_n':10,
        'fresh_n':256,'data_seed':91001,'source_seed':91003,'independent_seed':91009,
        'permutation_seed':91011,'target_seed':91013,'rcond':1e-12,'finite_epsilon':1.0,'epsilon_sweep':[.01,.1,.5,1.],'rank_tolerance_sweep':[1e-8,1e-10,1e-12],
        'scope':'Diagnostic, not confirmatory teacher experiment; linear solves count as fits.'}

def write(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def read(p):return json.loads(p.read_text())
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def network(seed):
 rng=np.random.default_rng(seed)
 return {'w':rng.normal(0,.8,(CONFIG['hidden'],CONFIG['input_dim'])).tolist(),
         'b':rng.normal(0,.3,CONFIG['hidden']).tolist(),
         'readout':rng.normal(0,.2,CONFIG['hidden']+1).tolist()}
def features(net,x):
 h=np.tanh(np.asarray(x)@np.asarray(net['w']).T+net['b'])
 return np.column_stack((h,np.ones(len(h))))
def svd_space(a,rcond=CONFIG['rcond']):
 _,s,vh=np.linalg.svd(a,full_matrices=True)
 cutoff=rcond*s[0] if len(s) else 0.
 rank=int(np.sum(s>cutoff))
 return vh[rank:].T,{'rank':rank,'nullity':a.shape[1]-rank,'singular_values':s.tolist(),'cutoff':float(cutoff)}
def solve(keep,probe,target):
 z,info=svd_space(keep); reduced=probe@z
 coeff=np.linalg.pinv(reduced,rcond=CONFIG['rcond'])@target
 delta=z@coeff
 _,fit_info=svd_space(reduced)
 return delta,{'keep':info,'probe_on_keep_nullspace':fit_info,'fit_count':1,
               'delta_l2':float(np.linalg.norm(delta)),'keep_max_abs_delta':float(np.max(np.abs(keep@delta))),
               'probe_target_rmse':float(np.sqrt(np.mean((probe@delta-target)**2)))}
def nonlinear_counterexample():
 t=float(np.tanh(1));s=1-t*t;direction=np.array([-s,t]);theta=np.array([1.,1.]);jacobian=np.array([t,s])
 eps=CONFIG['finite_epsilon'];edited=theta+eps*direction
 baseline=float(theta[0]*np.tanh(theta[1]));changed=float(edited[0]*np.tanh(edited[1]))
 return {'function':'f(a,b)=a*tanh(b), anchor input fixed at 1','theta':theta.tolist(),
         'jacobian':jacobian.tolist(),'direction':direction.tolist(),'J_times_direction':float(jacobian@direction),
         'epsilon':eps,'edited_theta':edited.tolist(),'baseline':baseline,'edited':changed,
         'finite_drift':changed-baseline,'epsilon_sweep':[{'epsilon':e,'finite_drift':float((theta+e*direction)[0]*np.tanh((theta+e*direction)[1])-baseline),'drift_divided_by_epsilon_squared':float(((theta+e*direction)[0]*np.tanh((theta+e*direction)[1])-baseline)/e**2)} for e in CONFIG['epsilon_sweep']],'lesson':'A Jacobian-null direction gives zero first-order change, not exact nonlinear finite-edit preservation.'}
def build():
 rng=np.random.default_rng(CONFIG['data_seed']);d=CONFIG['input_dim']
 data={'keep':rng.uniform(-1,1,(CONFIG['keep_n'],d)).tolist(),
       'probe':rng.uniform(-1,1,(CONFIG['probe_n'],d)).tolist(),
       'fresh_iid':rng.uniform(-1,1,(CONFIG['fresh_n'],d)).tolist(),
       'fresh_shifted':rng.uniform(1,3,(CONFIG['fresh_n'],d)).tolist()}
 target=np.random.default_rng(CONFIG['target_seed']).normal(0,.1,CONFIG['probe_n'])
 data['probe_delta_targets']=target.tolist()
 source=network(CONFIG['source_seed']);independent=network(CONFIG['independent_seed'])
 p=np.random.default_rng(CONFIG['permutation_seed']).permutation(CONFIG['hidden'])
 fullp=np.r_[p,CONFIG['hidden']]
 permuted={'w':np.asarray(source['w'])[p].tolist(),'b':np.asarray(source['b'])[p].tolist(),
           'readout':np.asarray(source['readout'])[fullp].tolist()}
 models={'source':source,'permuted':permuted,'independent':independent}
 donor_delta,donor_fit=solve(features(source,data['keep']),features(source,data['probe']),target)
 variants=[];fits={'source':donor_fit};deltas={'source_local':donor_delta.tolist()}
 for name,net in models.items():
  hkeep=features(net,data['keep']);hprobe=features(net,data['probe'])
  if name=='source':local=donor_delta
  else:
   local,fit=solve(hkeep,hprobe,target);fits[name]=fit
  possibilities={'local_solve':local}
  if name!='source':possibilities['raw_copy']=donor_delta
  if name=='permuted':possibilities['known_permutation_copy']=donor_delta[fullp]
  for mode,delta in possibilities.items():
   measurements={}
   for split in ('keep','probe','fresh_iid','fresh_shifted'):
    change=features(net,data[split])@delta
    measurements[split]={'delta_rmse':float(np.sqrt(np.mean(change**2))),'delta_max_abs':float(np.max(np.abs(change))),
                         'per_anchor_delta':change.tolist()}
    if split=='probe':measurements[split]['target_rmse']=float(np.sqrt(np.mean((change-target)**2)))
   key=name+'_'+mode;deltas[key]=delta.tolist()
   variants.append({'model':name,'method':mode,'delta_l2':float(np.linalg.norm(delta)),'metrics':measurements})
 equivalence={split:float(np.max(np.abs(features(source,data[split])@source['readout']-features(permuted,data[split])@permuted['readout']))) for split in ('keep','probe','fresh_iid','fresh_shifted')}
 equivariance_delta=float(np.max(np.abs(np.asarray(deltas['permuted_local_solve'])-donor_delta[fullp])))
 # Explicitly expose rank exhaustion: enough generic keep anchors leave no editable readout nullspace.
 saturated=rng.uniform(-1,1,(40,d));sat_h=features(source,saturated)
 sat_delta,sat_fit=solve(sat_h,features(source,data['probe']),target)
 payload={'config':CONFIG,'data':data,'models':models,'hidden_permutation':p.tolist(),'augmented_feature_permutation':fullp.tolist(),
          'deltas':deltas,'readout_checkpoints':{row['model']+'_'+row['method']:{'before':models[row['model']]['readout'],
          'after':(np.asarray(models[row['model']]['readout'])+np.asarray(deltas[row['model']+'_'+row['method']])).tolist()} for row in variants},
          'saturated_keep_inputs':saturated.tolist(),'saturated_delta':sat_delta.tolist()}
 report={'config':CONFIG,'nonlinear_counterexample':nonlinear_counterexample(),'fits':fits,
         'variants':variants,'permuted_baseline_max_abs_difference':equivalence,
         'permutation_equivariance_delta_max_abs':equivariance_delta,'rank_exhaustion':sat_fit,
         'total_linear_fit_count':4,'rank_tolerance_sweep':{str(t):{'source_keep':svd_space(features(source,data['keep']),t)[1],'saturated_keep':svd_space(sat_h,t)[1]} for t in CONFIG['rank_tolerance_sweep']},
         'limits':['Exact linear readout preservation applies only to registered keep anchors with frozen features.',
                   'Permutation equivariance uses identical features reordered; independently seeded features require a new local fit.',
                   'Probe targets are fitted data; recipient solves are fits, not evidence of unassisted transfer.',
                   'Fresh IID and shifted points are diagnostics where preservation is not constrained.',
                   'SVD/pseudoinverse tolerance affects numerical rank. No teacher experiment, API call or pretrained-model claim.']}
 return payload,report

def markdown(report):
 c=report['nonlinear_counterexample'];lines=['# Finite-anchor geometry diagnostic','',
 'This local calculation tests mathematical limits suggested by a peer synthesis. It is separate from the teacher experiments. All data and networks are fresh synthetic draws. No API or trained-model workload is involved. Linear solves are counted as fits.','',
 f"For f(a,b)=a tanh(b), the analytic Jacobian times the proposed direction is {c['J_times_direction']:.3g}; an epsilon={c['epsilon']} edit changes the output by {c['finite_drift']:.6g}. Thus zero first-order change does not imply exact finite nonlinear preservation.",'',
 'For a frozen feature matrix H_keep, SVD gives an orthonormal nullspace basis Z. The fit is delta = Z pinv(H_probe Z) target. This enforces H_keep delta = 0 numerically on the registered anchors. It makes no corresponding promise for new observations. Readout bias is an additional constant feature.','',
 'Rank uses singular values greater than rcond times the largest singular value, with rcond=1e-12. The same cutoff controls the Moore–Penrose pseudoinverse. Minimum-norm solutions are compared after known feature permutation.','',
 '| Model | Method | Keep maximum drift | Probe target RMSE | Fresh IID drift RMSE | Shifted drift RMSE |','|---|---|---:|---:|---:|---:|']
 for row in report['variants']:
  m=row['metrics'];lines.append(f"| {row['model']} | {row['method']} | {m['keep']['delta_max_abs']:.6g} | {m['probe']['target_rmse']:.6g} | {m['fresh_iid']['delta_rmse']:.6g} | {m['fresh_shifted']['delta_rmse']:.6g} |")
 lines+=['','The raw-copy and known-permutation-copy controls have identical Euclidean delta norms because permutation is orthogonal. Local fits are separately measured and need not share that norm; no common trust-region bound is claimed. No teacher is involved.','', '| Epsilon | Finite nonlinear drift | Drift / epsilon² |','|---:|---:|---:|']
 for row in c['epsilon_sweep']:lines.append(f"| {row['epsilon']} | {row['finite_drift']:.6g} | {row['drift_divided_by_epsilon_squared']:.6g} |")
 lines+=['','| Model | Keep rank | Keep nullity | Reduced probe rank | Fit count |','|---|---:|---:|---:|---:|']
 for name,f in report['fits'].items():lines.append(f"| {name} | {f['keep']['rank']} | {f['keep']['nullity']} | {f['probe_on_keep_nullspace']['rank']} | {f['fit_count']} |")
 lines+=['',f"Permutation equivariance: maximum delta discrepancy {report['permutation_equivariance_delta_max_abs']:.6g}.",
         f"With 40 generic keep anchors, readout nullity is {report['rank_exhaustion']['keep']['nullity']} and target fit RMSE is {report['rank_exhaustion']['probe_target_rmse']:.6g}. More retention constraints can remove all editable capacity: no useful nonzero exact-preserving edit exists within this fixed-feature readout class.",'',
         'There are four linear fits: donor, permuted recipient, independently seeded recipient, and the rank-exhaustion check. A feature permutation has an exact coordinate correspondence. A new feature map does not inherit that guarantee. The tables expose the recipient fit and unconstrained drift rather than treating them as a certificate of general capability preservation.','']
 return '\n'.join(lines)
def run(out,replay=False):
 start=time.monotonic();payload,report=build()
 if replay:
  manifest=read(out/'manifest.json')
  if manifest['code_sha256']!=hashlib.sha256(Path(__file__).read_bytes()).hexdigest():raise ValueError('Code changed')
  for name,x in [('artifacts.json',payload),('results.json',report)]:
   if read(out/name)!=x or manifest['sha256'][name]!=digest(x):raise ValueError('Replay mismatch '+name)
 else:
  write(out/'artifacts.json',payload);write(out/'results.json',report)
  (out/'RESULTS.md').write_text(markdown(report))
  write(out/'manifest.json',{'sha256':{'artifacts.json':digest(payload),'results.json':digest(report)},
       'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'python':platform.python_version(),'numpy':np.__version__,
       'elapsed_seconds':time.monotonic()-start,'command':'python3 geometry.py run --out data','replay':'python3 geometry.py replay --out data'})
 print(json.dumps({'replay':replay,'linear_fits':4,'elapsed_seconds':time.monotonic()-start}))
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['run','replay']);p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'data');a=p.parse_args();run(a.out,a.command=='replay')
