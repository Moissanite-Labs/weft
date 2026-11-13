import Core
namespace StemLifecycle
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def declaredRoot : Policy := ⟨1, 1, 0, 0, 2, 2⟩
def quiet : Policy := ⟨1, 1, 1, 1, 1, 1⟩
def urgent : Policy := ⟨1, 1, 0, 0, 2, 2⟩
def quietBenefit : Int := 297
def urgentBenefit : Int := 0
def expectedBranches : List Nat := if quietBenefit > 0 then (if urgentBenefit > 0 then (if quietBenefit ≥ urgentBenefit then [0,1,1,2] else [0,1,2,2]) else [0,1,1,1]) else (if urgentBenefit > 0 then [0,2,2,2] else [0])
def actualBranches : List Nat := [0, 1, 1, 1]
def actualPolicies : List Policy := [⟨1, 1, 0, 0, 2, 2⟩, ⟨1, 1, 1, 1, 1, 1⟩, ⟨1, 1, 1, 1, 1, 1⟩, ⟨1, 1, 1, 1, 1, 1⟩]
def expectedPolicies : List Policy := expectedBranches.map (fun b => if b = 0 then declaredRoot else if b = 1 then quiet else urgent)
theorem certificate : (declaredRoot = (⟨1,1,0,0,2,2⟩ : Policy)) ∧
 (actualBranches = expectedBranches) ∧
 (actualPolicies = expectedPolicies) ∧
 (actualPolicies.length ≤ 4) ∧
 (actualPolicies.head? = some declaredRoot) := by decide
#check certificate
#print axioms certificate
end StemLifecycle
