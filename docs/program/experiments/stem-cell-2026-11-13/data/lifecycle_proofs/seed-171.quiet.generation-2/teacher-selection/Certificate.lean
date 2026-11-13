import Core
namespace StemLifecycle
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policies : List Policy := [⟨1, 1, 0, 1, 1, 1⟩, ⟨1, 1, 0, 1, 0, 1⟩, ⟨1, 1, 0, 2, 0, 1⟩, ⟨1, 1, 1, 1, 1, 1⟩, ⟨1, 1, -1, 1, 1, 1⟩]
def costs : List Int := [409, 458, 436, 401, 467]
def eligible : List Bool := [true, true, true, true, true]
def winner : Nat := 3
def chosen : Policy := ⟨1, 1, 1, 1, 1, 1⟩
theorem certificate : (policies.length ≤ 5) ∧
 ((policies.drop winner).head? = some chosen) ∧
 ((eligible.drop winner).head? = some true) ∧
 ((costs.drop winner).head? = some (401:Int)) ∧
 (((eligible.drop 0).head? = some true) → ((401:Int) < (409:Int) ∨ ((401:Int) = (409:Int) ∧ winner ≤ 0))) ∧
 (((eligible.drop 1).head? = some true) → ((401:Int) < (458:Int) ∨ ((401:Int) = (458:Int) ∧ winner ≤ 1))) ∧
 (((eligible.drop 2).head? = some true) → ((401:Int) < (436:Int) ∨ ((401:Int) = (436:Int) ∧ winner ≤ 2))) ∧
 (((eligible.drop 3).head? = some true) → ((401:Int) < (401:Int) ∨ ((401:Int) = (401:Int) ∧ winner ≤ 3))) ∧
 (((eligible.drop 4).head? = some true) → ((401:Int) < (467:Int) ∨ ((401:Int) = (467:Int) ∧ winner ≤ 4))) := by decide
#check certificate
#print axioms certificate
end StemLifecycle
