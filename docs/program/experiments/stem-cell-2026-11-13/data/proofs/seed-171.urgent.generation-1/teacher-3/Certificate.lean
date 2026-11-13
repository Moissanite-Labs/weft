import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, 1, 0, 2, 2⟩
def inputs0 : List Stim := [⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩]
def rows0 : List Row := [⟨3, 2, 5, 8⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩]
def inputs1 : List Stim := [⟨2, true, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, false, 4, 1⟩, ⟨7, true, 4, 1⟩]
def rows1 : List Row := [⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 2, 5, 20⟩, ⟨5, 2, 7, 4⟩, ⟨7, 1, 8, 5⟩, ⟨8, 0, 8, 4⟩, ⟨8, 0, 8, 4⟩, ⟨8, 0, 8, 4⟩]
def inputs2 : List Stim := [⟨2, false, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨6, true, 4, 1⟩, ⟨6, true, 4, 1⟩, ⟨6, true, 4, 1⟩, ⟨-1, false, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨0, false, 4, 1⟩, ⟨0, true, 4, 1⟩, ⟨0, true, 4, 1⟩]
def rows2 : List Row := [⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 2, 5, 8⟩, ⟨5, 2, 7, 8⟩, ⟨7, 0, 7, 4⟩, ⟨7, -2, 5, 148⟩, ⟨5, -2, 3, 68⟩, ⟨3, -2, 1, 20⟩, ⟨1, 0, 1, 4⟩, ⟨1, 0, 1, 4⟩, ⟨1, 0, 1, 4⟩]
def inputs3 : List Stim := [⟨5, false, 4, 1⟩, ⟨5, false, 4, 1⟩, ⟨5, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, true, 4, 1⟩]
def rows3 : List Row := [⟨3, 2, 5, 4⟩, ⟨5, 1, 6, 5⟩, ⟨6, 0, 6, 4⟩, ⟨6, -1, 5, 5⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 2, 7, 8⟩, ⟨7, 2, 9, 8⟩, ⟨9, 0, 9, 4⟩, ⟨9, 0, 9, 4⟩, ⟨9, 0, 9, 4⟩, ⟨9, 0, 9, 4⟩]
def inputs4 : List Stim := [⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, true, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨-2, false, 4, 1⟩, ⟨-2, true, 4, 1⟩, ⟨-2, true, 4, 1⟩]
def rows4 : List Row := [⟨3, -1, 2, 5⟩, ⟨2, 0, 2, 4⟩, ⟨2, 0, 2, 4⟩, ⟨2, 0, 2, 4⟩, ⟨2, 0, 2, 4⟩, ⟨2, 0, 2, 4⟩, ⟨2, 0, 2, 4⟩, ⟨2, 0, 2, 4⟩, ⟨2, 0, 2, 4⟩, ⟨2, -2, 0, 20⟩, ⟨0, -1, -1, 5⟩, ⟨-1, 0, -1, 4⟩]
def inputs5 : List Stim := [⟨-2, true, 4, 1⟩, ⟨-2, true, 4, 1⟩, ⟨-2, false, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, false, 4, 1⟩]
def rows5 : List Row := [⟨3, -2, 1, 40⟩, ⟨1, -2, -1, 8⟩, ⟨-1, 0, -1, 4⟩, ⟨-1, 1, 0, 5⟩, ⟨0, 0, 0, 4⟩, ⟨0, 0, 0, 4⟩, ⟨0, 2, 2, 20⟩, ⟨2, 2, 4, 4⟩, ⟨4, 1, 5, 5⟩, ⟨5, 2, 7, 8⟩, ⟨7, 2, 9, 8⟩, ⟨9, 0, 9, 4⟩]
def inputs6 : List Stim := [⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩]
def rows6 : List Row := [⟨3, 2, 5, 8⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩]
def inputs7 : List Stim := [⟨-1, false, 4, 1⟩, ⟨-1, false, 4, 1⟩, ⟨-1, false, 4, 1⟩, ⟨7, false, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, true, 4, 1⟩]
def rows7 : List Row := [⟨3, -2, 1, 20⟩, ⟨1, -1, 0, 5⟩, ⟨0, 0, 0, 4⟩, ⟨0, 2, 2, 104⟩, ⟨2, 2, 4, 40⟩, ⟨4, 2, 6, 8⟩, ⟨6, -2, 4, 20⟩, ⟨4, -1, 3, 5⟩, ⟨3, 0, 3, 4⟩, ⟨3, 2, 5, 40⟩, ⟨5, 2, 7, 8⟩, ⟨7, 2, 9, 8⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (52:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (5:Int)) ∧
  (simulate policy (3) inputs1 = rows1) ∧
  (allSafe policy inputs1 rows1 = true) ∧
  (totalCost rows1 = (65:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows1.getLast?).map Row.after = some (8:Int)) ∧
  (simulate policy (3) inputs2 = rows2) ∧
  (allSafe policy inputs2 rows2 = true) ∧
  (totalCost rows2 = (280:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows2.getLast?).map Row.after = some (1:Int)) ∧
  (simulate policy (3) inputs3 = rows3) ∧
  (allSafe policy inputs3 rows3 = true) ∧
  (totalCost rows3 = (58:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows3.getLast?).map Row.after = some (9:Int)) ∧
  (simulate policy (3) inputs4 = rows4) ∧
  (allSafe policy inputs4 rows4 = true) ∧
  (totalCost rows4 = (66:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows4.getLast?).map Row.after = some (-1:Int)) ∧
  (simulate policy (3) inputs5 = rows5) ∧
  (allSafe policy inputs5 rows5 = true) ∧
  (totalCost rows5 = (114:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows5.getLast?).map Row.after = some (9:Int)) ∧
  (simulate policy (3) inputs6 = rows6) ∧
  (allSafe policy inputs6 rows6 = true) ∧
  (totalCost rows6 = (52:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows6.getLast?).map Row.after = some (5:Int)) ∧
  (simulate policy (3) inputs7 = rows7) ∧
  (allSafe policy inputs7 rows7 = true) ∧
  (totalCost rows7 = (266:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows7.getLast?).map Row.after = some (9:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
