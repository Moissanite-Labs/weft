import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, 1, 1, 1, 1⟩
def inputs0 : List Stim := [⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨6, false, 1, 8⟩]
def rows0 : List Row := [⟨3, 1, 4, 8⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 1, 5, 9⟩, ⟨5, 1, 6, 8⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 4⟩, ⟨6, 0, 6, 4⟩, ⟨6, 0, 6, 4⟩, ⟨6, -1, 5, 12⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 1, 6, 8⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (65:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (6:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
