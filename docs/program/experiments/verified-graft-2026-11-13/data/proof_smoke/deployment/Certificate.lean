import Core
namespace VerifiedGraftConcrete
open VerifiedGraft
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def host : Mat := ⟨⟨0,0,0,0,0,0⟩,⟨0,0,0,0,0,0⟩⟩
def delta : Mat := ⟨⟨0,0,0,1,1,1⟩,⟨0,0,0,1,-1,0⟩⟩
def basis : List Vec := [⟨1,0,0,0,0,0⟩,⟨0,1,0,0,0,0⟩,⟨0,0,1,0,0,0⟩]
def native : List Vec := [⟨1,0,0,0,0,0⟩,⟨0,1,0,0,0,0⟩,⟨0,0,1,0,0,0⟩]
def claimedRoot : Mat := ⟨⟨0,0,0,1,1,1⟩,⟨0,0,0,1,-1,0⟩⟩
def claimedSpecialist : Option Mat := none
theorem certificate : (allowed host delta basis false 0 = true) ∧
 (basisValid native 3 = true) ∧
 (covers basis native = true) ∧
 (rootAfter host delta 0 = claimedRoot) ∧
 (specialistAfter host delta 0 = claimedSpecialist) ∧
 (transferUsesSpecialist 0 = false) ∧
 (nativeUsesSpecialist 0 = false) ∧
 (cellCount 0 = 1) ∧
 (∀ v ∈ basis, SameOn host claimedRoot v) := by decide
#check certificate
#print axioms certificate
end VerifiedGraftConcrete
