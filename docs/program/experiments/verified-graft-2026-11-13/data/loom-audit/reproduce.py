"""Bounded offline audit; copies the supplied bundle only into disposable scratch."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,default=HERE.parent.parent/'inputs/loom-pr');a=p.parse_args()
source=a.bundle.resolve();archived=(source/'package.json.txt').exists() and not (source/'package.json').exists()
def relative(path):
 name=str(path.relative_to(source))
 return name[:-4] if archived and name.endswith('.txt') else name
hashes={relative(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(source.rglob('*')) if path.is_file()}
node=shutil.which('node')
if not node:raise RuntimeError('Node is not installed; no installation attempted')
version=subprocess.check_output([node,'--version'],text=True).strip()
env={k:v for k,v in os.environ.items() if k in ('PATH','LANG','LC_ALL')};env['NO_COLOR']='1'
commands=[]
with tempfile.TemporaryDirectory(prefix='loom-audit-') as tmp:
 root=Path(tmp)
 for path in source.rglob('*'):
  if path.is_file():
   dest=root/'bundle'/relative(path);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes())
 shutil.copyfile(HERE/'probes.mjs',root/'probes.mjs')
 tests=sorted(str(path.relative_to(root)) for path in (root/'bundle/weft/runtime/aywa').glob('test_*.mjs'))
 for label,argv in [('suite',[node,'--test',*tests]),('probes',[node,'probes.mjs'])]:
  before={str(path.relative_to(root)) for path in root.rglob('*')}
  started=time.monotonic();result=subprocess.run(argv,cwd=root,env=env,capture_output=True,text=True,timeout=60)
  (HERE/(label+'.stdout.txt')).write_text(result.stdout.replace(str(root),'<scratch>'))
  (HERE/(label+'.stderr.txt')).write_text(result.stderr.replace(str(root),'<scratch>'))
  created=sorted(str(path.relative_to(root)) for path in root.rglob('*') if str(path.relative_to(root)) not in before)
  commands.append({'label':label,'command':['node',*argv[1:]],'node_version':version,'exit_code':result.returncode,
                   'elapsed_seconds':time.monotonic()-started,'created_artifacts':created})
  if label=='probes' and result.returncode==0:(HERE/'probes.json').write_text(json.dumps(json.loads(result.stdout),indent=2)+'\n')
report={'node_version':version,'supplied_sha256':hashes,'commands':commands,
        'safety_scope':'Reviewed package, tests and imported JS before execution. Test imports are local or Node builtins; one test reads the local conformance JSON. No install, npm lifecycle execution, browser, paid API, network command or production integration was performed.',
        'limitations':'No browser/WebGPU execution, general confluence proof, large-scale benchmark or arbitrary-task forgetting guarantee is established.'}
(HERE/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'node_version':version,'commands':commands},indent=2))
