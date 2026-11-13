import Core
namespace StemLifecycle
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policies : List Policy := [⟨1, 1, 0, 0, 2, 2⟩, ⟨3, 1, 0, 2, 0, 0⟩, ⟨3, 4, 1, 3, 2, 2⟩, ⟨0, 1, 0, 1, 1, 0⟩, ⟨2, 3, -2, 3, 0, 1⟩]
def costs : List Int := [706, 645, 625, 645, 685]
def eligible : List Bool := [true, true, true, true, true]
def winner : Nat := 2
def chosen : Policy := ⟨3, 4, 1, 3, 2, 2⟩
theorem certificate : (policies.length ≤ 5) ∧
 ((policies.drop winner).head? = some chosen) ∧
 ((eligible.drop winner).head? = some true) ∧
 ((costs.drop winner).head? = some (625:Int)) ∧
 (((eligible.drop 0).head? = some true) → ((625:Int) < (706:Int) ∨ ((625:Int) = (706:Int) ∧ winner ≤ 0))) ∧
 (((eligible.drop 1).head? = some true) → ((625:Int) < (645:Int) ∨ ((625:Int) = (645:Int) ∧ winner ≤ 1))) ∧
 (((eligible.drop 2).head? = some true) → ((625:Int) < (625:Int) ∨ ((625:Int) = (625:Int) ∧ winner ≤ 2))) ∧
 (((eligible.drop 3).head? = some true) → ((625:Int) < (645:Int) ∨ ((625:Int) = (645:Int) ∧ winner ≤ 3))) ∧
 (((eligible.drop 4).head? = some true) → ((625:Int) < (685:Int) ∨ ((625:Int) = (685:Int) ∧ winner ≤ 4))) := by decide
#check certificate
#print axioms certificate
end StemLifecycle
