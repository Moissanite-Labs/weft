#!/usr/bin/env python3
"""Offline pinned E11 command and input-feature-rank audit; no benchmark replacement."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np

HERE=Path(__file__).resolve().parent
PIN='2b004a7cc0ba305f6a337c8bf2bb3c540d7d7aa3'
SOURCE=HERE/'supplied-ic_morphogenesis.py.txt'
RESULT=HERE/'supplied-RESULTS-E11.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for path,expected in [(SOURCE,'336ee84a99a0832e27cc4c973edf36ecb7a01d5b'),(RESULT,'3989d5e1e672b2829d99115e0dc1cefe15e64652')]:
  content=path.read_bytes()
  actual=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
  if actual!=expected:raise ValueError('Pinned Git blob mismatch: '+path.name)
 out=HERE/'data';out.mkdir(exist_ok=True)
 environment={'PATH':os.environ.get('PATH','/usr/local/bin:/usr/bin:/bin'),'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'}
 commands=[]
 for label,args in [('unit',['--unit']),('default',[])]:
  with tempfile.TemporaryDirectory(prefix='e11-offline-review-') as tmp:
   scratch=Path(tmp);script=scratch/'ic_morphogenesis.py';script.write_bytes(SOURCE.read_bytes())
   before={str(p.relative_to(scratch)) for p in scratch.rglob('*')}
   proc=subprocess.run([sys.executable,'-B',script.name]+args,cwd=scratch,env=environment,capture_output=True,text=True,timeout=60)
   created=sorted(str(p.relative_to(scratch)) for p in scratch.rglob('*') if str(p.relative_to(scratch)) not in before)
   (out/f'{label}.stdout.txt').write_text(proc.stdout)
   (out/f'{label}.stderr.txt').write_text(proc.stderr)
   commands.append({'command':['python3','ic_morphogenesis.py']+args,'returncode':proc.returncode,
                    'created_artifacts':created,'stdout_file':f'{label}.stdout.txt','stderr_file':f'{label}.stderr.txt',
                    'observation':'Runs unit-test main only; no evolution/ES/statistical runner is called.'})
 ranks=[]
 for n in (64,256,512):
  angle=np.linspace(-np.pi,np.pi,n,endpoint=False)
  basis=np.column_stack((np.cos(angle),np.sin(angle),np.cos(2*angle),np.sin(2*angle)))
  # Evaluator s = goalx*cos(theta)+goaly*sin(theta)+.25*cos(2theta-.25t), divided by sqrt(N).
  rng=np.random.default_rng(155+n);columns=[];coefs=[]
  for t in range(24):
   goal=rng.normal(size=2);phase=.25*t
   coefs.append([goal[0],goal[1],.25*np.cos(phase),.25*np.sin(phase)])
   columns.append((goal[0]*np.cos(angle)+goal[1]*np.sin(angle)+.25*np.cos(2*angle-phase))/np.sqrt(n))
  generated=np.column_stack(columns);coefs=np.asarray(coefs).T/np.sqrt(n)
  s=np.linalg.svd(basis,compute_uv=False)
  residual=float(np.max(np.abs(generated-basis@coefs)))
  ranks.append({'dimension':n,'basis_shape':list(basis.shape),'basis_numeric_rank':int(np.linalg.matrix_rank(basis)),
                'basis_singular_values':s.tolist(),'sample_input_shape':list(generated.shape),
                'sample_input_numeric_rank':int(np.linalg.matrix_rank(generated)),
                'reconstruction_max_abs_error':residual,'analytic_rank_upper_bound':4})
  np.savez(out/f'input-basis-{n}.npz',basis=basis,coefficients=coefs,generated_inputs=generated)
 report={'pr':155,'pinned_commit':PIN,'github_blob_shas':{'ic_morphogenesis.py':'336ee84a99a0832e27cc4c973edf36ecb7a01d5b','RESULTS-E11.md':'3989d5e1e672b2829d99115e0dc1cefe15e64652'},'source_sha256':sha(SOURCE),'results_text_sha256':sha(RESULT),
         'commands':commands,'feature_rank':ranks,'numpy_version':np.__version__,
         'scope':'Offline reproducibility review. Command tests plus small N-by-4 linear algebra only; no evolution, training, paid API or full benchmark replacement.',
         'conclusion':'The two documented commands do not reproduce reported per-seed statistics. Evaluator inputs occupy at most four spatial harmonics, not a full-rank N-dimensional input family.'}
 (out/'reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'commands':commands,'ranks':ranks},indent=2))
if __name__=='__main__':main()
