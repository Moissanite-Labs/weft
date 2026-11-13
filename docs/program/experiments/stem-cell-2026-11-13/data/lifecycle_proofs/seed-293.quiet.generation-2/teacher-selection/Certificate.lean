import Core
namespace StemLifecycle
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policies : List Policy := [⟨1, 1, 0, 1, 1, 1⟩, ⟨1, 1, -1, 1, 1, 1⟩, ⟨1, 1, 1, 1, 1, 1⟩, ⟨1, 1, 0, 1, 0, 1⟩, ⟨1, 1, 0, 0, 0, 1⟩]
def costs : List Int := [466, 438, 559, 520, 555]
def eligible : List Bool := [true, true, true, true, true]
def winner : Nat := 1
def chosen : Policy := ⟨1, 1, -1, 1, 1, 1⟩
theorem certificate : (policies.length ≤ 5) ∧
 ((policies.drop winner).head? = some chosen) ∧
 ((eligible.drop winner).head? = some true) ∧
 ((costs.drop winner).head? = some (438:Int)) ∧
 (((eligible.drop 0).head? = some true) → ((438:Int) < (466:Int) ∨ ((438:Int) = (466:Int) ∧ winner ≤ 0))) ∧
 (((eligible.drop 1).head? = some true) → ((438:Int) < (438:Int) ∨ ((438:Int) = (438:Int) ∧ winner ≤ 1))) ∧
 (((eligible.drop 2).head? = some true) → ((438:Int) < (559:Int) ∨ ((438:Int) = (559:Int) ∧ winner ≤ 2))) ∧
 (((eligible.drop 3).head? = some true) → ((438:Int) < (520:Int) ∨ ((438:Int) = (520:Int) ∧ winner ≤ 3))) ∧
 (((eligible.drop 4).head? = some true) → ((438:Int) < (555:Int) ∨ ((438:Int) = (555:Int) ∧ winner ≤ 4))) := by decide
#check certificate
#print axioms certificate
end StemLifecycle
