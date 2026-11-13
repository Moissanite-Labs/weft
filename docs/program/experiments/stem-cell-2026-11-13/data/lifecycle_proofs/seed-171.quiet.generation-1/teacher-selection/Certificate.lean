import Core
namespace StemLifecycle
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policies : List Policy := [⟨1, 1, 0, 0, 2, 2⟩, ⟨1, 1, 0, 0, 1, 1⟩, ⟨1, 1, 0, 1, 1, 1⟩, ⟨1, 1, 0, 2, 1, 1⟩, ⟨1, 3, 0, 2, 1, 2⟩]
def costs : List Int := [698, 463, 409, 416, 419]
def eligible : List Bool := [true, true, true, true, true]
def winner : Nat := 2
def chosen : Policy := ⟨1, 1, 0, 1, 1, 1⟩
theorem certificate : (policies.length ≤ 5) ∧
 ((policies.drop winner).head? = some chosen) ∧
 ((eligible.drop winner).head? = some true) ∧
 ((costs.drop winner).head? = some (409:Int)) ∧
 (((eligible.drop 0).head? = some true) → ((409:Int) < (698:Int) ∨ ((409:Int) = (698:Int) ∧ winner ≤ 0))) ∧
 (((eligible.drop 1).head? = some true) → ((409:Int) < (463:Int) ∨ ((409:Int) = (463:Int) ∧ winner ≤ 1))) ∧
 (((eligible.drop 2).head? = some true) → ((409:Int) < (409:Int) ∨ ((409:Int) = (409:Int) ∧ winner ≤ 2))) ∧
 (((eligible.drop 3).head? = some true) → ((409:Int) < (416:Int) ∨ ((409:Int) = (416:Int) ∧ winner ≤ 3))) ∧
 (((eligible.drop 4).head? = some true) → ((409:Int) < (419:Int) ∨ ((409:Int) = (419:Int) ∧ winner ≤ 4))) := by decide
#check certificate
#print axioms certificate
end StemLifecycle
