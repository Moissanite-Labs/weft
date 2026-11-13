import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, 0, 0, 2, 2⟩
def inputs0 : List Stim := [⟨0, false, 4, 1⟩, ⟨0, false, 4, 1⟩, ⟨0, false, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨-1, false, 4, 1⟩, ⟨5, false, 4, 1⟩, ⟨5, true, 4, 1⟩, ⟨5, true, 4, 1⟩, ⟨5, true, 4, 1⟩, ⟨5, false, 4, 1⟩, ⟨5, false, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨3, true, 4, 1⟩]
def rows0 : List Row := [⟨3, -2, 1, 8⟩, ⟨1, -1, 0, 1⟩, ⟨0, 0, 0, 0⟩, ⟨0, -1, -1, 1⟩, ⟨-1, 0, -1, 0⟩, ⟨-1, 0, -1, 0⟩, ⟨-1, 2, 1, 68⟩, ⟨1, 2, 3, 20⟩, ⟨3, 2, 5, 4⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, -2, 3, 68⟩, ⟨3, -2, 1, 20⟩, ⟨1, -2, -1, 4⟩, ⟨-1, 2, 1, 20⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (214:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (1:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
