import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, 0, 0, 2, 2⟩
def inputs0 : List Stim := [⟨8, true, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨1, true, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, false, 4, 1⟩, ⟨3, true, 4, 1⟩]
def rows0 : List Row := [⟨3, 2, 5, 40⟩, ⟨5, 2, 7, 8⟩, ⟨7, 1, 8, 1⟩, ⟨8, 0, 8, 0⟩, ⟨8, 0, 8, 0⟩, ⟨8, 0, 8, 0⟩, ⟨8, -2, 6, 104⟩, ⟨6, -2, 4, 40⟩, ⟨4, -2, 2, 8⟩, ⟨2, 2, 4, 40⟩, ⟨4, 2, 6, 8⟩, ⟨6, 1, 7, 1⟩, ⟨7, 0, 7, 0⟩, ⟨7, 0, 7, 0⟩, ⟨7, 0, 7, 0⟩, ⟨7, -2, 5, 20⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (270:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (5:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
