import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, 0, 0, 2, 2⟩
def inputs0 : List Stim := [⟨8, false, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨5, false, 4, 1⟩, ⟨5, true, 4, 1⟩, ⟨5, false, 4, 1⟩, ⟨5, true, 4, 1⟩, ⟨5, false, 4, 1⟩, ⟨5, false, 4, 1⟩, ⟨-1, false, 4, 1⟩, ⟨-1, false, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨6, true, 4, 1⟩]
def rows0 : List Row := [⟨3, 2, 5, 40⟩, ⟨5, 2, 7, 8⟩, ⟨7, 1, 8, 1⟩, ⟨8, -2, 6, 8⟩, ⟨6, -1, 5, 1⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, -2, 3, 68⟩, ⟨3, -2, 1, 20⟩, ⟨1, -2, -1, 4⟩, ⟨-1, 2, 1, 40⟩, ⟨1, 2, 3, 8⟩, ⟨3, 1, 4, 1⟩, ⟨4, 2, 6, 4⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (203:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (6:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
