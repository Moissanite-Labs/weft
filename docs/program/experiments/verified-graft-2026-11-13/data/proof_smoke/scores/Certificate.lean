import Core
namespace VerifiedGraftConcrete
open VerifiedGraft
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def target : Mat := ⟨⟨0,0,0,1,1,1⟩,⟨0,0,0,1,-1,0⟩⟩
def actual0 : Mat := ⟨⟨0,0,0,1,1,1⟩,⟨0,0,0,1,-1,0⟩⟩
def inputs0 : List Vec := [⟨1,0,0,0,0,0⟩,⟨0,1,0,0,0,0⟩,⟨0,0,1,0,0,0⟩,⟨0,0,0,1,0,0⟩,⟨0,0,0,0,1,0⟩,⟨0,0,0,0,0,1⟩]
theorem certificate : (totalError actual0 target inputs0 = (0:Int)) := by decide
#check certificate
#print axioms certificate
end VerifiedGraftConcrete
