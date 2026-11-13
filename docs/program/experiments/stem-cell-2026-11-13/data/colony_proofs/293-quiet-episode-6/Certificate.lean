import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, -1, 1, 1, 1⟩
def inputs0 : List Stim := [⟨6, true, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, false, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, true, 1, 8⟩, ⟨-2, false, 1, 8⟩]
def rows0 : List Row := [⟨3, 1, 4, 12⟩, ⟨4, 0, 4, 4⟩, ⟨4, 0, 4, 4⟩, ⟨4, 0, 4, 1⟩, ⟨4, 0, 4, 1⟩, ⟨4, 0, 4, 1⟩, ⟨4, 0, 4, 1⟩, ⟨4, 0, 4, 1⟩, ⟨4, 0, 4, 1⟩, ⟨4, -1, 3, 17⟩, ⟨3, -1, 2, 12⟩, ⟨2, -1, 1, 9⟩, ⟨1, 0, 1, 0⟩, ⟨1, 0, 1, 0⟩, ⟨1, 0, 1, 0⟩, ⟨1, -1, 0, 12⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (76:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (0:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
