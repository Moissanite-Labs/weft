import Core
namespace StemLifecycle
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policies : List Policy := [⟨1, 1, 0, 0, 2, 2⟩, ⟨1, 1, 0, 1, 1, 1⟩, ⟨1, 2, 0, 0, 2, 2⟩, ⟨1, 1, 0, 2, 1, 1⟩, ⟨1, 1, 0, 0, 1, 1⟩]
def costs : List Int := [706, 466, 551, 484, 528]
def eligible : List Bool := [true, true, true, true, true]
def winner : Nat := 1
def chosen : Policy := ⟨1, 1, 0, 1, 1, 1⟩
theorem certificate : (policies.length ≤ 5) ∧
 ((policies.drop winner).head? = some chosen) ∧
 ((eligible.drop winner).head? = some true) ∧
 ((costs.drop winner).head? = some (466:Int)) ∧
 (((eligible.drop 0).head? = some true) → ((466:Int) < (706:Int) ∨ ((466:Int) = (706:Int) ∧ winner ≤ 0))) ∧
 (((eligible.drop 1).head? = some true) → ((466:Int) < (466:Int) ∨ ((466:Int) = (466:Int) ∧ winner ≤ 1))) ∧
 (((eligible.drop 2).head? = some true) → ((466:Int) < (551:Int) ∨ ((466:Int) = (551:Int) ∧ winner ≤ 2))) ∧
 (((eligible.drop 3).head? = some true) → ((466:Int) < (484:Int) ∨ ((466:Int) = (484:Int) ∧ winner ≤ 3))) ∧
 (((eligible.drop 4).head? = some true) → ((466:Int) < (528:Int) ∨ ((466:Int) = (528:Int) ∧ winner ≤ 4))) := by decide
#check certificate
#print axioms certificate
end StemLifecycle
