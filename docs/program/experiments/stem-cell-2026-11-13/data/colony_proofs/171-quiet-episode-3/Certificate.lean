import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, 1, 1, 1, 1⟩
def inputs0 : List Stim := [⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨-2, true, 1, 8⟩, ⟨-2, false, 1, 8⟩, ⟨-2, false, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨2, false, 1, 8⟩]
def rows0 : List Row := [⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, -1, 2, 24⟩, ⟨2, -1, 1, 17⟩, ⟨1, -1, 0, 12⟩, ⟨0, 0, 0, 1⟩, ⟨0, 0, 0, 1⟩, ⟨0, 0, 0, 1⟩, ⟨0, 0, 0, 1⟩, ⟨0, 0, 0, 1⟩, ⟨0, 0, 0, 1⟩, ⟨0, 1, 1, 57⟩, ⟨1, 1, 2, 44⟩, ⟨2, 1, 3, 33⟩, ⟨3, 0, 3, 1⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (206:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (3:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
