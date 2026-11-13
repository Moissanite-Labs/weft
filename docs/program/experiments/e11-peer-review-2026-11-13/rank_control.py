"""Diagnostic of the pinned published evaluator; not reproduction of reported evolution."""
import ast
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np

source=Path(sys.argv[1])
text=source.read_text()
tree=ast.parse(text)
function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='evaluate_ciliary_plasm')
namespace={'np':np,'math':math}
exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),'exec'),namespace)
evaluate=namespace['evaluate_ciliary_plasm']
rows=[]
for dim in (64,256,512):
 theta=np.linspace(-math.pi,math.pi,dim,endpoint=False)
 basis=np.column_stack((np.cos(theta),np.sin(theta),np.cos(2*theta),np.sin(2*theta)))
 q,_=np.linalg.qr(basis)
 rng=np.random.default_rng(417+dim)
 matrices=[rng.normal(size=(dim,dim))*.2/math.sqrt(dim) for _ in range(2)]
 if dim==64:
  np.savez_compressed(Path(__file__).with_name('data')/'projection_inputs_64.npz',w_a=matrices[0],w_b=matrices[1],basis=basis)
 reduced=[]
 for w in matrices:
  out=w.copy();out[dim//4:]=(w[dim//4:]@q)@q.T;reduced.append(out)
 before=evaluate(*matrices,seed=417)
 after=evaluate(*reduced,seed=417)
 rows.append({'dimension':dim,'matrix_rng_seed':417+dim,'evaluation_seed':417,'input_basis_rank':int(np.linalg.matrix_rank(basis)),
              'plastic_operator_rank_upper_bound_after_projection':4,
              'original_return':before,'projected_return':after,'absolute_return_difference':abs(before-after),
              'max_basis_response_difference':max(float(np.max(np.abs(a[dim//4:]@basis-b[dim//4:]@basis))) for a,b in zip(matrices,reduced))})
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'numpy_version':np.__version__,
        'scope':'Synthetic matrices; diagnostic of input-span limitation, not reproduction of E11 reported runs. Frozen core rows unchanged.', 'rows':rows}
print(json.dumps(report,indent=2))
