import Core
namespace VerifiedGraftConcrete
open VerifiedGraft
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def host : Mat := ⟨⟨0,0,0,0,0,0⟩,⟨0,0,0,0,0,0⟩⟩
def delta : Mat := ⟨⟨0,0,0,1,1,1⟩,⟨0,0,0,0,0,0⟩⟩
def basis : List Vec := [⟨1,0,0,0,0,0⟩,⟨0,1,0,0,0,0⟩,⟨0,0,1,0,0,0⟩,⟨0,0,0,1,0,0⟩,⟨0,0,0,0,1,0⟩,⟨0,0,0,0,0,1⟩]
def native : List Vec := [⟨1,0,0,0,0,0⟩,⟨0,1,0,0,0,0⟩,⟨0,0,1,0,0,0⟩]
def claimedRoot : Mat := ⟨⟨0,0,0,0,0,0⟩,⟨0,0,0,0,0,0⟩⟩
def claimedSpecialist : Option Mat := some ⟨⟨0,0,0,1,1,1⟩,⟨0,0,0,0,0,0⟩⟩
theorem checked_basis : ∀ v ∈ basis, SameOn host claimedRoot v := by decide
theorem registered_span_retention (terms : List (Int × Vec)) (membership : ∀ term ∈ terms, term.2 ∈ basis) : SameOn host claimedRoot (combine terms) := span_retention host claimedRoot terms (fun term member => checked_basis term.2 (membership term member))
theorem certificate : (allowed host delta basis true 1 = true) ∧
 (basisValid native 3 = true) ∧
 (covers basis native = true) ∧
 (rootAfter host delta 1 = claimedRoot) ∧
 (specialistAfter host delta 1 = claimedSpecialist) ∧
 (transferUsesSpecialist 1 = true) ∧
 (nativeUsesSpecialist 1 = false) ∧
 (cellCount 1 = 2) ∧
 (∀ v ∈ basis, SameOn host claimedRoot v) := by decide
#check certificate
#print axioms certificate
end VerifiedGraftConcrete
