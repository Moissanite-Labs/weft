import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, 0, 0, 2, 2⟩
def inputs0 : List Stim := [⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨6, true, 4, 1⟩, ⟨6, false, 4, 1⟩, ⟨6, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨3, false, 4, 1⟩, ⟨3, true, 4, 1⟩, ⟨3, true, 4, 1⟩, ⟨6, false, 4, 1⟩]
def rows0 : List Row := [⟨3, 1, 4, 1⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 2, 6, 4⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, -2, 4, 4⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, -1, 3, 1⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 2, 5, 8⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (18:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (5:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
