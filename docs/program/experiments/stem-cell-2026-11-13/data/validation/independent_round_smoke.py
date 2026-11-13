import hashlib,json,shutil,tempfile,time
from pathlib import Path
import colony as c
import run_experiment as r
base=Path(__file__).resolve()
archive=Path('data/validation/independent_round_smoke')
with tempfile.TemporaryDirectory(prefix='stem-independent-round-') as directory:
 out=Path(directory);r.write(out/'config.json',c.CONFIG)
 for seed in c.CONFIG['seeds']:r.write(out/'experiments'/f'seed-{seed}.json',c.experiment(seed))
 pending=r.process(out,'normal');path=Path(pending[0]);request=r.read(path)
 wire=request|{'store':False,'service_tier':'default'};payload=json.dumps(wire,ensure_ascii=False).encode()
 path.with_suffix('.wire.json').write_bytes(payload+b'\n')
 children=[c.ROOT,c.FIXED,c.ROOT|{'gain_num':0},c.ROOT|{'bias':1}]
 proposal={'hypothesis':'Synthetic offline integration control, not an Astra response.','children':[{'label':str(i),'genome':g} for i,g in enumerate(children)]}
 envelope={'synthetic_offline_control':True,'request_file':path.name,'request_sha256':hashlib.sha256(payload).hexdigest(),'response':{'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(proposal)}]}]}}
 r.write(path.with_suffix('.response.json'),envelope)
 start=time.monotonic();remaining=r.process(out,'normal');elapsed=time.monotonic()-start
 selections=list((out/'selections').glob('*.json'));assert len(selections)==1
 record=r.read(selections[0]);assert len(record['children'])==4
 assert all(x['proof']['verification']['kernel_checked'] and x['proof']['verification']['axioms']==[] for x in record['children'])
 assert record['teacher_selection_proof']['accepted'] and record['random_selection_proof']['accepted']
 # Reconsume saved selection without changing it, checking deterministic continuation.
 before=c.fingerprint(record);r.process(out,'normal');assert c.fingerprint(r.read(selections[0]))==before
 shutil.copytree(out,archive,dirs_exist_ok=True)
 summary={'scope':'One synthetic four-child round through real Lean gates, not a paid model experiment. Temporary artifact root; archived separately under validation.', 'elapsed_seconds':elapsed,'teacher_candidates':4,'teacher_valid':sum(x['valid'] for x in record['children']),'selected_index':record['selected_index'],'selected_genome':record['selected_genome'],'selected_validation_cost':record['selected_validation']['total_cost'],'parent_validation_cost':record['unchanged_parent']['validation']['total_cost'],'selection_certificates_empty_axioms':all(record[k]['axioms']==[] for k in ('teacher_selection_proof','random_selection_proof')),'selection_reuse_identical':True,'remaining_requests':len(remaining),'paid_calls':0}
 r.write(archive/'summary.json',summary);print(json.dumps(summary,indent=2))
