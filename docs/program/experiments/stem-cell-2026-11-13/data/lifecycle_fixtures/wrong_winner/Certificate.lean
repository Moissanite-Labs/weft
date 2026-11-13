import Core
namespace StemLifecycle
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policies : List Policy := [⟨1, 1, 0, 0, 2, 2⟩, ⟨1, 2, 0, 1, 1, 2⟩]
def costs : List Int := [20, 10]
def eligible : List Bool := [true, true]
def winner : Nat := 0
def chosen : Policy := ⟨1, 1, 0, 0, 2, 2⟩
theorem certificate : (policies.length ≤ 5) ∧
 ((policies.drop winner).head? = some chosen) ∧
 ((eligible.drop winner).head? = some true) ∧
 ((costs.drop winner).head? = some (20:Int)) ∧
 (((eligible.drop 0).head? = some true) → ((20:Int) < (20:Int) ∨ ((20:Int) = (20:Int) ∧ winner ≤ 0))) ∧
 (((eligible.drop 1).head? = some true) → ((20:Int) < (10:Int) ∨ ((20:Int) = (10:Int) ∧ winner ≤ 1))) := by decide
#check certificate
#print axioms certificate
end StemLifecycle
