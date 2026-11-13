import Core
namespace StemLifecycle
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policies : List Policy := [⟨1, 1, 0, 0, 2, 2⟩, ⟨3, 4, 1, 0, 2, 2⟩, ⟨1, 2, 1, 0, 2, 2⟩, ⟨1, 2, 0, 0, 2, 2⟩, ⟨1, 1, 0, 1, 2, 2⟩]
def costs : List Int := [498, 592, 614, 578, 552]
def eligible : List Bool := [true, true, true, true, true]
def winner : Nat := 0
def chosen : Policy := ⟨1, 1, 0, 0, 2, 2⟩
theorem certificate : (policies.length ≤ 5) ∧
 ((policies.drop winner).head? = some chosen) ∧
 ((eligible.drop winner).head? = some true) ∧
 ((costs.drop winner).head? = some (498:Int)) ∧
 (((eligible.drop 0).head? = some true) → ((498:Int) < (498:Int) ∨ ((498:Int) = (498:Int) ∧ winner ≤ 0))) ∧
 (((eligible.drop 1).head? = some true) → ((498:Int) < (592:Int) ∨ ((498:Int) = (592:Int) ∧ winner ≤ 1))) ∧
 (((eligible.drop 2).head? = some true) → ((498:Int) < (614:Int) ∨ ((498:Int) = (614:Int) ∧ winner ≤ 2))) ∧
 (((eligible.drop 3).head? = some true) → ((498:Int) < (578:Int) ∨ ((498:Int) = (578:Int) ∧ winner ≤ 3))) ∧
 (((eligible.drop 4).head? = some true) → ((498:Int) < (552:Int) ∨ ((498:Int) = (552:Int) ∧ winner ≤ 4))) := by decide
#check certificate
#print axioms certificate
end StemLifecycle
