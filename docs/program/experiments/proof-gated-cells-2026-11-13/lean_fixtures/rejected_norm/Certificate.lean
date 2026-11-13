import Core
namespace ProofCellConcrete
open ProofCell
set_option maxRecDepth 100000
set_option maxHeartbeats 2000000
theorem certificate : ((⟨6,-2,5⟩ : Vec3) = add ⟨3,1,5⟩ ⟨3,-3,0⟩) ∧ ¬ (Allowed ⟨3,-3,0⟩ [⟨1,1,0⟩,⟨0,0,1⟩] [2] (8:Int)) := by decide
#check certificate
#print axioms certificate
end ProofCellConcrete
