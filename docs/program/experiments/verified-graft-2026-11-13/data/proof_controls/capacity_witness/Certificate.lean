import Core
namespace VerifiedGraftConcrete
open VerifiedGraft
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def host : Mat := ⟨⟨0,0,0,0,0,0⟩,⟨0,0,0,0,0,0⟩⟩
def target : Mat := ⟨⟨0,0,0,1,1,1⟩,⟨0,0,0,0,0,0⟩⟩
def witness : Vec := ⟨0,0,0,1,0,0⟩
theorem universal_conflict (candidate : Mat) (preserved : apply candidate witness = apply host witness) : apply candidate witness ≠ apply target witness := conflict_witness host target candidate witness (by decide) preserved
theorem certificate : (apply host witness ≠ apply target witness) := by decide
#check certificate
#print axioms certificate
end VerifiedGraftConcrete
