import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, 0, 0, 2, 2⟩
def inputs0 : List Stim := [⟨8, true, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨6, false, 4, 1⟩, ⟨6, false, 4, 1⟩, ⟨6, true, 4, 1⟩, ⟨6, false, 4, 1⟩, ⟨6, true, 4, 1⟩, ⟨6, false, 4, 1⟩, ⟨6, false, 4, 1⟩, ⟨6, false, 4, 1⟩, ⟨6, false, 4, 1⟩, ⟨-2, false, 4, 1⟩, ⟨-2, true, 4, 1⟩, ⟨-2, false, 4, 1⟩, ⟨8, true, 4, 1⟩]
def rows0 : List Row := [⟨3, 2, 5, 40⟩, ⟨5, 2, 7, 8⟩, ⟨7, 1, 8, 1⟩, ⟨8, -2, 6, 4⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, -2, 4, 148⟩, ⟨4, -2, 2, 68⟩, ⟨2, -2, 0, 20⟩, ⟨0, 2, 2, 148⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (437:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (2:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
