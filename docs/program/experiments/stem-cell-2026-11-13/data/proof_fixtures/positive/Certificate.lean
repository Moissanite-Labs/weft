import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 2, 0, 0, 1, 2⟩
def inputs0 : List Stim := [⟨0, true, 2, 1⟩, ⟨7, false, 1, 2⟩]
def rows0 : List Row := [⟨3, -1, 2, 9⟩, ⟨2, 1, 3, 18⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (27:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (3:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
