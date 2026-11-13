import Core
namespace StemLifecycle
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policies : List Policy := [⟨1, 1, 0, 0, 2, 2⟩, ⟨2, 4, 0, 1, 0, 1⟩, ⟨4, 1, 1, 3, 2, 1⟩, ⟨3, 4, -1, 3, 1, 0⟩, ⟨4, 2, 2, 3, 1, 2⟩]
def costs : List Int := [437, 1553, 1414, 2261, 1922]
def eligible : List Bool := [true, true, true, true, true]
def winner : Nat := 0
def chosen : Policy := ⟨1, 1, 0, 0, 2, 2⟩
theorem certificate : (policies.length ≤ 5) ∧
 ((policies.drop winner).head? = some chosen) ∧
 ((eligible.drop winner).head? = some true) ∧
 ((costs.drop winner).head? = some (437:Int)) ∧
 (((eligible.drop 0).head? = some true) → ((437:Int) < (437:Int) ∨ ((437:Int) = (437:Int) ∧ winner ≤ 0))) ∧
 (((eligible.drop 1).head? = some true) → ((437:Int) < (1553:Int) ∨ ((437:Int) = (1553:Int) ∧ winner ≤ 1))) ∧
 (((eligible.drop 2).head? = some true) → ((437:Int) < (1414:Int) ∨ ((437:Int) = (1414:Int) ∧ winner ≤ 2))) ∧
 (((eligible.drop 3).head? = some true) → ((437:Int) < (2261:Int) ∨ ((437:Int) = (2261:Int) ∧ winner ≤ 3))) ∧
 (((eligible.drop 4).head? = some true) → ((437:Int) < (1922:Int) ∨ ((437:Int) = (1922:Int) ∧ winner ≤ 4))) := by decide
#check certificate
#print axioms certificate
end StemLifecycle
