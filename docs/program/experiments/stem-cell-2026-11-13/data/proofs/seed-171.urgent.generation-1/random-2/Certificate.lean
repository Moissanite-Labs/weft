import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, -2, 2, 2, 2⟩
def inputs0 : List Stim := [⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩]
def rows0 : List Row := [⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩]
def inputs1 : List Stim := [⟨2, true, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, false, 4, 1⟩, ⟨7, true, 4, 1⟩]
def rows1 : List Row := [⟨3, -2, 1, 8⟩, ⟨1, 0, 1, 4⟩, ⟨1, 0, 1, 4⟩, ⟨1, 0, 1, 4⟩, ⟨1, 0, 1, 4⟩, ⟨1, 0, 1, 4⟩, ⟨1, 2, 3, 68⟩, ⟨3, 0, 3, 64⟩, ⟨3, 0, 3, 64⟩, ⟨3, 0, 3, 64⟩, ⟨3, 0, 3, 64⟩, ⟨3, 0, 3, 64⟩]
def inputs2 : List Stim := [⟨2, false, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨6, true, 4, 1⟩, ⟨6, true, 4, 1⟩, ⟨6, true, 4, 1⟩, ⟨-1, false, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨0, false, 4, 1⟩, ⟨0, true, 4, 1⟩, ⟨0, true, 4, 1⟩]
def rows2 : List Row := [⟨3, -2, 1, 8⟩, ⟨1, 0, 1, 4⟩, ⟨1, 0, 1, 4⟩, ⟨1, 2, 3, 40⟩, ⟨3, 0, 3, 36⟩, ⟨3, 0, 3, 36⟩, ⟨3, -2, 1, 20⟩, ⟨1, -2, -1, 4⟩, ⟨-1, 0, -1, 0⟩, ⟨-1, 0, -1, 4⟩, ⟨-1, 0, -1, 4⟩, ⟨-1, 0, -1, 4⟩]
def inputs3 : List Stim := [⟨5, false, 4, 1⟩, ⟨5, false, 4, 1⟩, ⟨5, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, true, 4, 1⟩]
def rows3 : List Row := [⟨3, 0, 3, 16⟩, ⟨3, 0, 3, 16⟩, ⟨3, 0, 3, 16⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 2, 5, 40⟩, ⟨5, 0, 5, 36⟩, ⟨5, 0, 5, 36⟩, ⟨5, 0, 5, 36⟩, ⟨5, 0, 5, 36⟩, ⟨5, 0, 5, 36⟩]
def inputs4 : List Stim := [⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, true, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨1, false, 4, 1⟩, ⟨-2, false, 4, 1⟩, ⟨-2, true, 4, 1⟩, ⟨-2, true, 4, 1⟩]
def rows4 : List Row := [⟨3, -2, 1, 4⟩, ⟨1, 0, 1, 0⟩, ⟨1, 0, 1, 0⟩, ⟨1, 0, 1, 0⟩, ⟨1, 0, 1, 0⟩, ⟨1, 0, 1, 0⟩, ⟨1, 0, 1, 0⟩, ⟨1, 0, 1, 0⟩, ⟨1, 0, 1, 0⟩, ⟨1, -2, -1, 8⟩, ⟨-1, -2, -3, 8⟩, ⟨-3, 0, -3, 4⟩]
def inputs5 : List Stim := [⟨-2, true, 4, 1⟩, ⟨-2, true, 4, 1⟩, ⟨-2, false, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨-1, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, true, 4, 1⟩, ⟨8, false, 4, 1⟩]
def rows5 : List Row := [⟨3, -2, 1, 40⟩, ⟨1, -2, -1, 8⟩, ⟨-1, -2, -3, 8⟩, ⟨-3, 0, -3, 16⟩, ⟨-3, 0, -3, 16⟩, ⟨-3, 0, -3, 16⟩, ⟨-3, 2, -1, 104⟩, ⟨-1, 2, 1, 40⟩, ⟨1, 0, 1, 36⟩, ⟨1, 2, 3, 104⟩, ⟨3, 2, 5, 40⟩, ⟨5, 0, 5, 36⟩]
def inputs6 : List Stim := [⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, true, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩, ⟨4, false, 4, 1⟩]
def rows6 : List Row := [⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩]
def inputs7 : List Stim := [⟨-1, false, 4, 1⟩, ⟨-1, false, 4, 1⟩, ⟨-1, false, 4, 1⟩, ⟨7, false, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨7, true, 4, 1⟩, ⟨2, false, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨2, true, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, false, 4, 1⟩, ⟨8, true, 4, 1⟩]
def rows7 : List Row := [⟨3, -2, 1, 20⟩, ⟨1, -2, -1, 4⟩, ⟨-1, 0, -1, 0⟩, ⟨-1, 2, 1, 148⟩, ⟨1, 2, 3, 68⟩, ⟨3, 0, 3, 64⟩, ⟨3, -2, 1, 8⟩, ⟨1, 0, 1, 4⟩, ⟨1, 0, 1, 4⟩, ⟨1, 2, 3, 104⟩, ⟨3, 2, 5, 40⟩, ⟨5, 0, 5, 36⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (48:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs1 = rows1) ∧
  (allSafe policy inputs1 rows1 = true) ∧
  (totalCost rows1 = (416:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows1.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs2 = rows2) ∧
  (allSafe policy inputs2 rows2 = true) ∧
  (totalCost rows2 = (164:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows2.getLast?).map Row.after = some (-1:Int)) ∧
  (simulate policy (3) inputs3 = rows3) ∧
  (allSafe policy inputs3 rows3 = true) ∧
  (totalCost rows3 = (280:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows3.getLast?).map Row.after = some (5:Int)) ∧
  (simulate policy (3) inputs4 = rows4) ∧
  (allSafe policy inputs4 rows4 = true) ∧
  (totalCost rows4 = (24:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows4.getLast?).map Row.after = some (-3:Int)) ∧
  (simulate policy (3) inputs5 = rows5) ∧
  (allSafe policy inputs5 rows5 = true) ∧
  (totalCost rows5 = (464:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows5.getLast?).map Row.after = some (5:Int)) ∧
  (simulate policy (3) inputs6 = rows6) ∧
  (allSafe policy inputs6 rows6 = true) ∧
  (totalCost rows6 = (48:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows6.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs7 = rows7) ∧
  (allSafe policy inputs7 rows7 = true) ∧
  (totalCost rows7 = (500:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows7.getLast?).map Row.after = some (5:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
