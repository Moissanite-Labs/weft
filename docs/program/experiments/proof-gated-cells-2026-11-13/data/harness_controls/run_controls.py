"""Offline controls: import reviewed harness, never invoke main or its API client."""
import importlib.util
import importlib.machinery
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
source=ROOT/'inputs/supplied-lean-harness.py.txt'
# Keep only compiler lookup/home and locale; no provider credentials are inherited.
home=str(Path.home())
os.environ.clear()
os.environ.update(HOME=home,PATH=home+'/.elan/bin:/usr/bin:/bin',LANG='C.UTF-8')
loader=importlib.machinery.SourceFileLoader('reviewed_supplied_harness',str(source))
spec=importlib.util.spec_from_loader(loader.name,loader)
module=importlib.util.module_from_spec(spec)
sys.modules[loader.name]=module
loader.exec_module(module)
raw_calls=[]
original_run=subprocess.run
def recording_run(*args,**kwargs):
 result=original_run(*args,**kwargs)
 def decoded(value):return value.decode('utf-8',errors='replace') if isinstance(value,bytes) else value
 raw_calls.append({'command':args[0] if args else kwargs.get('args'),'returncode':result.returncode,'stdout':decoded(result.stdout),'stderr':decoded(result.stderr)})
 return result
module.subprocess.run=recording_run
empty='import Std\n' 
scanner_candidate='import Std\n#eval IO.println "harmless review marker"\n'
(HERE/'Empty.lean').write_text(empty)
(HERE/'scanner_candidate.txt').write_text(scanner_candidate)
with tempfile.TemporaryDirectory(prefix='empty-proof-control-') as tmp:
 p=Path(tmp)
 (p/'lean-toolchain').write_text('leanprover/lean4:v4.35.0\n')
 lake='name = "Empty"\nversion = "0.1.0"\ndefaultTargets = ["Empty"]\n\n[[lean_lib]]\nname = "Empty"\n'
 (p/'lakefile.toml').write_text(lake)
 (HERE/'lakefile.toml.txt').write_text(lake)
 (p/'Empty.lean').write_text(empty)
 result=module.run_real_lake_check(p,p/'Empty.lean',False,60)
 report={'compiler_control':result,'contains_required_theorem':False,'candidate_source':'Empty.lean',
         'scanner_candidate':'scanner_candidate.txt','scanner_violations':module.scan_lean4_verified_bar(scanner_candidate),
         'scanner_candidate_executed':False,'api_calls':0,
         'scope':'Actual harness compiler path accepts a module without any required theorem; scanner permits harmless IO command text. The IO text was not executed.'}
 (HERE/'compiler_calls.json').write_text(json.dumps(raw_calls,indent=2)+'\n')
 (HERE/'results.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
