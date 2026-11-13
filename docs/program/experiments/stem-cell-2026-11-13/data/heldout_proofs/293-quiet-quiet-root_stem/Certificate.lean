import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, 0, 0, 2, 2⟩
def inputs0 : List Stim := [⟨3, true, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨7, false, 1, 8⟩, ⟨7, false, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨5, false, 1, 8⟩]
def rows0 : List Row := [⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 2, 5, 36⟩, ⟨5, 2, 7, 32⟩, ⟨7, 0, 7, 0⟩, ⟨7, 0, 7, 0⟩, ⟨7, 0, 7, 0⟩, ⟨7, 0, 7, 0⟩, ⟨7, -2, 5, 36⟩, ⟨5, -2, 3, 32⟩, ⟨3, 0, 3, 0⟩, ⟨3, 2, 5, 32⟩]
def inputs1 : List Stim := [⟨6, false, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨3, false, 1, 8⟩]
def rows1 : List Row := [⟨3, 2, 5, 33⟩, ⟨5, 1, 6, 8⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 0, 6, 0⟩, ⟨6, 2, 8, 32⟩, ⟨8, 0, 8, 0⟩, ⟨8, 0, 8, 0⟩, ⟨8, 0, 8, 0⟩, ⟨8, 0, 8, 0⟩, ⟨8, 0, 8, 0⟩, ⟨8, -2, 6, 41⟩, ⟨6, -2, 4, 33⟩, ⟨4, -1, 3, 8⟩, ⟨3, 0, 3, 0⟩]
def inputs2 : List Stim := [⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨8, true, 1, 8⟩]
def rows2 : List Row := [⟨3, -2, 1, 32⟩, ⟨1, 0, 1, 0⟩, ⟨1, 0, 1, 0⟩, ⟨1, 1, 2, 8⟩, ⟨2, 0, 2, 0⟩, ⟨2, 0, 2, 0⟩, ⟨2, 1, 3, 8⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 2, 5, 41⟩, ⟨5, 2, 7, 33⟩, ⟨7, 1, 8, 8⟩, ⟨8, -2, 6, 36⟩, ⟨6, -2, 4, 32⟩, ⟨4, 0, 4, 0⟩, ⟨4, 2, 6, 36⟩]
def inputs3 : List Stim := [⟨2, false, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, false, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨1, true, 1, 8⟩]
def rows3 : List Row := [⟨3, -1, 2, 8⟩, ⟨2, 0, 2, 0⟩, ⟨2, 0, 2, 0⟩, ⟨2, 2, 4, 33⟩, ⟨4, 1, 5, 8⟩, ⟨5, 0, 5, 0⟩, ⟨5, -2, 3, 48⟩, ⟨3, -2, 1, 36⟩, ⟨1, -2, -1, 32⟩, ⟨-1, 2, 1, 57⟩, ⟨1, 2, 3, 41⟩, ⟨3, 2, 5, 33⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, -2, 3, 36⟩]
def inputs4 : List Stim := [⟨8, false, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨5, false, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, false, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, false, 1, 8⟩, ⟨5, false, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨6, true, 1, 8⟩]
def rows4 : List Row := [⟨3, 2, 5, 41⟩, ⟨5, 2, 7, 33⟩, ⟨7, 1, 8, 8⟩, ⟨8, -2, 6, 33⟩, ⟨6, -1, 5, 8⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, -2, 3, 48⟩, ⟨3, -2, 1, 36⟩, ⟨1, -2, -1, 32⟩, ⟨-1, 2, 1, 41⟩, ⟨1, 2, 3, 33⟩, ⟨3, 1, 4, 8⟩, ⟨4, 2, 6, 32⟩]
def inputs5 : List Stim := [⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨1, true, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, false, 1, 8⟩, ⟨3, true, 1, 8⟩]
def rows5 : List Row := [⟨3, 2, 5, 41⟩, ⟨5, 2, 7, 33⟩, ⟨7, 1, 8, 8⟩, ⟨8, 0, 8, 0⟩, ⟨8, 0, 8, 0⟩, ⟨8, 0, 8, 0⟩, ⟨8, -2, 6, 57⟩, ⟨6, -2, 4, 41⟩, ⟨4, -2, 2, 33⟩, ⟨2, 2, 4, 41⟩, ⟨4, 2, 6, 33⟩, ⟨6, 1, 7, 8⟩, ⟨7, 0, 7, 0⟩, ⟨7, 0, 7, 0⟩, ⟨7, 0, 7, 0⟩, ⟨7, -2, 5, 36⟩]
def inputs6 : List Stim := [⟨6, true, 1, 8⟩, ⟨6, false, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, false, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, true, 1, 8⟩, ⟨-2, false, 1, 8⟩]
def rows6 : List Row := [⟨3, 2, 5, 33⟩, ⟨5, 1, 6, 8⟩, ⟨6, 0, 6, 0⟩, ⟨6, -1, 5, 8⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, 0, 5, 0⟩, ⟨5, -2, 3, 41⟩, ⟨3, -2, 1, 33⟩, ⟨1, -1, 0, 8⟩, ⟨0, 1, 1, 8⟩, ⟨1, 0, 1, 0⟩, ⟨1, 0, 1, 0⟩, ⟨1, -2, -1, 33⟩]
def inputs7 : List Stim := [⟨3, true, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨3, true, 1, 8⟩]
def rows7 : List Row := [⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, -2, 1, 33⟩, ⟨1, -1, 0, 8⟩, ⟨0, 0, 0, 0⟩, ⟨0, 0, 0, 0⟩, ⟨0, 0, 0, 0⟩, ⟨0, 0, 0, 0⟩, ⟨0, -1, -1, 8⟩, ⟨-1, 0, -1, 0⟩, ⟨-1, 0, -1, 0⟩, ⟨-1, 2, 1, 36⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (168:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (5:Int)) ∧
  (simulate policy (3) inputs1 = rows1) ∧
  (allSafe policy inputs1 rows1 = true) ∧
  (totalCost rows1 = (155:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows1.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs2 = rows2) ∧
  (allSafe policy inputs2 rows2 = true) ∧
  (totalCost rows2 = (234:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows2.getLast?).map Row.after = some (6:Int)) ∧
  (simulate policy (3) inputs3 = rows3) ∧
  (allSafe policy inputs3 rows3 = true) ∧
  (totalCost rows3 = (332:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows3.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs4 = rows4) ∧
  (allSafe policy inputs4 rows4 = true) ∧
  (totalCost rows4 = (353:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows4.getLast?).map Row.after = some (6:Int)) ∧
  (simulate policy (3) inputs5 = rows5) ∧
  (allSafe policy inputs5 rows5 = true) ∧
  (totalCost rows5 = (331:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows5.getLast?).map Row.after = some (5:Int)) ∧
  (simulate policy (3) inputs6 = rows6) ∧
  (allSafe policy inputs6 rows6 = true) ∧
  (totalCost rows6 = (172:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows6.getLast?).map Row.after = some (-1:Int)) ∧
  (simulate policy (3) inputs7 = rows7) ∧
  (allSafe policy inputs7 rows7 = true) ∧
  (totalCost rows7 = (85:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows7.getLast?).map Row.after = some (1:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
