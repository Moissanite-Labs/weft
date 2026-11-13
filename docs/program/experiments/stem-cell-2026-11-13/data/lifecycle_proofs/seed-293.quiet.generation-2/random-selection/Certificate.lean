import Core
namespace StemLifecycle
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policies : List Policy := [⟨1, 1, 0, 1, 1, 1⟩, ⟨1, 4, 1, 1, 0, 1⟩, ⟨2, 1, -1, 1, 1, 0⟩, ⟨1, 4, 0, 3, 1, 0⟩, ⟨0, 3, -1, 1, 1, 0⟩]
def costs : List Int := [466, 554, 628, 635, 645]
def eligible : List Bool := [true, true, true, true, true]
def winner : Nat := 0
def chosen : Policy := ⟨1, 1, 0, 1, 1, 1⟩
theorem certificate : (policies.length ≤ 5) ∧
 ((policies.drop winner).head? = some chosen) ∧
 ((eligible.drop winner).head? = some true) ∧
 ((costs.drop winner).head? = some (466:Int)) ∧
 (((eligible.drop 0).head? = some true) → ((466:Int) < (466:Int) ∨ ((466:Int) = (466:Int) ∧ winner ≤ 0))) ∧
 (((eligible.drop 1).head? = some true) → ((466:Int) < (554:Int) ∨ ((466:Int) = (554:Int) ∧ winner ≤ 1))) ∧
 (((eligible.drop 2).head? = some true) → ((466:Int) < (628:Int) ∨ ((466:Int) = (628:Int) ∧ winner ≤ 2))) ∧
 (((eligible.drop 3).head? = some true) → ((466:Int) < (635:Int) ∨ ((466:Int) = (635:Int) ∧ winner ≤ 3))) ∧
 (((eligible.drop 4).head? = some true) → ((466:Int) < (645:Int) ∨ ((466:Int) = (645:Int) ∧ winner ≤ 4))) := by decide
#check certificate
#print axioms certificate
end StemLifecycle
