import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨3, 4, 1, 0, 2, 2⟩
def inputs0 : List Stim := [⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩]
def rows0 : List Row := [⟨3, 1, 4, 1⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩]
def inputs1 : List Stim := [⟨2, true, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, false, 4, 1⟩, ⟨7, true, 4, 1⟩]
def rows1 : List Row := [⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 2, 5, 20⟩, ⟨5, 2, 7, 4⟩, ⟨7, 0, 7, 0⟩, ⟨7, 0, 7, 0⟩, ⟨7, 0, 7, 0⟩, ⟨7, 0, 7, 0⟩]
def inputs2 : List Stim := [⟨2, false, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨6, true, 4, 1⟩, ⟨6, true, 4, 1⟩, ⟨6, true, 4, 1⟩, ⟨-1, false, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨0, false, 4, 1⟩, ⟨0, true, 4, 1⟩, ⟨0, true, 4, 1⟩]
def rows2 : List Row := [⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 2, 5, 8⟩, ⟨5, 1, 6, 1⟩, ⟨6, 0, 6, 0⟩, ⟨6, -2, 4, 104⟩, ⟨4, -2, 2, 40⟩, ⟨2, -1, 1, 17⟩, ⟨1, 0, 1, 4⟩, ⟨1, 0, 1, 4⟩, ⟨1, 0, 1, 4⟩]
def inputs3 : List Stim := [⟨5, false, 4, 1⟩, ⟨5, false, 4, 1⟩, ⟨5, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, true, 4, 1⟩]
def rows3 : List Row := [⟨3, 2, 5, 4⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 2, 7, 8⟩, ⟨7, 1, 8, 1⟩, ⟨8, 0, 8, 0⟩, ⟨8, 0, 8, 0⟩, ⟨8, 0, 8, 0⟩, ⟨8, 0, 8, 0⟩]
def inputs4 : List Stim := [⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, true, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨-2, false, 4, 1⟩, ⟨-2, true, 4, 1⟩, ⟨-2, true, 4, 1⟩]
def rows4 : List Row := [⟨3, 0, 3, 16⟩, ⟨3, 0, 3, 16⟩, ⟨3, 0, 3, 16⟩, ⟨3, 0, 3, 16⟩, ⟨3, 0, 3, 16⟩, ⟨3, 0, 3, 16⟩, ⟨3, 0, 3, 16⟩, ⟨3, 0, 3, 16⟩, ⟨3, 0, 3, 16⟩, ⟨3, -2, 1, 40⟩, ⟨1, -1, 0, 17⟩, ⟨0, 0, 0, 16⟩]
def inputs5 : List Stim := [⟨-2, true, 4, 1⟩, ⟨-2, true, 4, 1⟩, ⟨-2, false, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, false, 4, 1⟩]
def rows5 : List Row := [⟨3, -2, 1, 40⟩, ⟨1, -1, 0, 17⟩, ⟨0, 0, 0, 16⟩, ⟨0, 0, 0, 4⟩, ⟨0, 0, 0, 4⟩, ⟨0, 0, 0, 4⟩, ⟨0, 2, 2, 20⟩, ⟨2, 2, 4, 4⟩, ⟨4, 0, 4, 0⟩, ⟨4, 2, 6, 20⟩, ⟨6, 2, 8, 4⟩, ⟨8, 0, 8, 0⟩]
def inputs6 : List Stim := [⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩]
def rows6 : List Row := [⟨3, 1, 4, 1⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩]
def inputs7 : List Stim := [⟨-1, false, 4, 1⟩, ⟨-1, false, 4, 1⟩, ⟨-1, false, 4, 1⟩, ⟨7, false, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, true, 4, 1⟩]
def rows7 : List Row := [⟨3, -2, 1, 20⟩, ⟨1, 0, 1, 16⟩, ⟨1, 0, 1, 16⟩, ⟨1, 2, 3, 68⟩, ⟨3, 2, 5, 20⟩, ⟨5, 2, 7, 4⟩, ⟨7, -2, 5, 40⟩, ⟨5, -1, 4, 17⟩, ⟨4, 0, 4, 16⟩, ⟨4, 2, 6, 20⟩, ⟨6, 2, 8, 4⟩, ⟨8, 0, 8, 0⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (1:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (4:Int)) ∧
  (simulate policy (3) inputs1 = rows1) ∧
  (allSafe policy inputs1 rows1 = true) ∧
  (totalCost rows1 = (48:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows1.getLast?).map Row.after = some (7:Int)) ∧
  (simulate policy (3) inputs2 = rows2) ∧
  (allSafe policy inputs2 rows2 = true) ∧
  (totalCost rows2 = (194:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows2.getLast?).map Row.after = some (1:Int)) ∧
  (simulate policy (3) inputs3 = rows3) ∧
  (allSafe policy inputs3 rows3 = true) ∧
  (totalCost rows3 = (25:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows3.getLast?).map Row.after = some (8:Int)) ∧
  (simulate policy (3) inputs4 = rows4) ∧
  (allSafe policy inputs4 rows4 = true) ∧
  (totalCost rows4 = (217:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows4.getLast?).map Row.after = some (0:Int)) ∧
  (simulate policy (3) inputs5 = rows5) ∧
  (allSafe policy inputs5 rows5 = true) ∧
  (totalCost rows5 = (133:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows5.getLast?).map Row.after = some (8:Int)) ∧
  (simulate policy (3) inputs6 = rows6) ∧
  (allSafe policy inputs6 rows6 = true) ∧
  (totalCost rows6 = (1:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows6.getLast?).map Row.after = some (4:Int)) ∧
  (simulate policy (3) inputs7 = rows7) ∧
  (allSafe policy inputs7 rows7 = true) ∧
  (totalCost rows7 = (241:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows7.getLast?).map Row.after = some (8:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
