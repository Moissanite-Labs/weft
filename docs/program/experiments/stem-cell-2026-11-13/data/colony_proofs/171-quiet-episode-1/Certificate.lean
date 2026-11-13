import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, 1, 1, 1, 1⟩
def inputs0 : List Stim := [⟨8, true, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨-2, false, 1, 8⟩, ⟨-2, true, 1, 8⟩, ⟨-2, false, 1, 8⟩, ⟨8, true, 1, 8⟩]
def rows0 : List Row := [⟨3, 1, 4, 24⟩, ⟨4, 1, 5, 17⟩, ⟨5, 1, 6, 12⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, -1, 5, 57⟩, ⟨5, -1, 4, 44⟩, ⟨4, -1, 3, 33⟩, ⟨3, 1, 4, 24⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (211:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (4:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
