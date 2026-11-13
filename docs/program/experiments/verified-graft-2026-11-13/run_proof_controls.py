"""Offline real-Lean controls; no inference clients or credentials."""
from pathlib import Path
import json
from proof_gate import verify_deployment,verify_scores,verify_conflict,verify_adoption

BASE=Path(__file__).resolve().parent/'data/proof_controls'
ZERO=[[0]*6 for _ in range(2)]
BASIS=[[int(i==j) for j in range(6)] for i in range(6)]
TARGET=[[0,0,0,1,1,1],[0]*6]
OVERFIT=[[0,0,0,1,1,-2],[0]*6]
def main():
 visible={'host_weights':ZERO,'capacity_case':'compatible','protected_basis':BASIS[:3],'native_basis':BASIS[:3]}
 records={}
 records['compatible_graft']=verify_deployment(visible,{'mode':'graft','delta':TARGET},BASE/'compatible_graft')
 saturated=visible|{'capacity_case':'saturated','protected_basis':BASIS}
 records['saturated_graft_rejected']=verify_deployment(saturated,{'mode':'graft','delta':TARGET},BASE/'saturated_graft_rejected')
 records['saturated_fork']=verify_deployment(saturated,{'mode':'fork','delta':TARGET},BASE/'saturated_fork')
 records['capacity_witness']=verify_conflict(ZERO,TARGET,BASIS[3],BASE/'capacity_witness')
 records['overfitter_deployment']=verify_deployment(visible,{'mode':'graft','delta':OVERFIT},BASE/'overfitter_deployment')
 batches={'A':{'inputs':BASIS[3:5],'sse':0,'task':'new'},'B':{'inputs':[BASIS[5],[-x for x in BASIS[5]]],'sse':18,'task':'new'}}
 records['overfitter_scores']=verify_scores(records['overfitter_deployment']['deployment'],TARGET,batches,BASE/'overfitter_scores')
 records['confirmation_rejection']=verify_adoption(2,0,2,18,False,BASE/'confirmation_rejection')
 records['forged_adoption']=verify_adoption(2,0,2,18,True,BASE/'forged_adoption')
 summary={name:{'accepted':value['accepted'],'kernel_checked':value['kernel_checked'],'axioms':value['axioms']} for name,value in records.items()}
 assert all(value['accepted']==(name not in ('saturated_graft_rejected','forged_adoption')) for name,value in records.items())
 (BASE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
