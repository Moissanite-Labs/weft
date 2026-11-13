import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, -1, 1, 1, 1⟩
def inputs0 : List Stim := [⟨8, false, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨5, false, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, false, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, false, 1, 8⟩, ⟨5, false, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨6, true, 1, 8⟩]
def rows0 : List Row := [⟨3, 1, 4, 24⟩, ⟨4, 1, 5, 17⟩, ⟨5, 1, 6, 12⟩, ⟨6, -1, 5, 8⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, -1, 4, 33⟩, ⟨4, -1, 3, 24⟩, ⟨3, -1, 2, 17⟩, ⟨2, 0, 2, 4⟩, ⟨2, 0, 2, 4⟩, ⟨2, 0, 2, 4⟩, ⟨2, 1, 3, 17⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (164:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (3:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
