import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, 1, 0, 2, 2⟩
def inputs0 : List Stim := [⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩]
def rows0 : List Row := [⟨3, 2, 5, 33⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩]
def inputs1 : List Stim := [⟨2, true, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, false, 1, 8⟩, ⟨7, true, 1, 8⟩]
def rows1 : List Row := [⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 2, 5, 36⟩, ⟨5, 2, 7, 32⟩, ⟨7, 1, 8, 9⟩, ⟨8, 0, 8, 1⟩, ⟨8, 0, 8, 1⟩, ⟨8, 0, 8, 1⟩]
def inputs2 : List Stim := [⟨2, false, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, true, 1, 8⟩]
def rows2 : List Row := [⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 2, 5, 33⟩, ⟨5, 2, 7, 33⟩, ⟨7, 0, 7, 1⟩, ⟨7, -2, 5, 68⟩, ⟨5, -2, 3, 48⟩, ⟨3, -2, 1, 36⟩, ⟨1, 0, 1, 1⟩, ⟨1, 0, 1, 1⟩, ⟨1, 0, 1, 1⟩]
def inputs3 : List Stim := [⟨5, false, 1, 8⟩, ⟨5, false, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩]
def rows3 : List Row := [⟨3, 2, 5, 32⟩, ⟨5, 1, 6, 9⟩, ⟨6, 0, 6, 1⟩, ⟨6, -1, 5, 9⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 2, 7, 33⟩, ⟨7, 2, 9, 33⟩, ⟨9, 0, 9, 1⟩, ⟨9, 0, 9, 1⟩, ⟨9, 0, 9, 1⟩, ⟨9, 0, 9, 1⟩]
def inputs4 : List Stim := [⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, true, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨-2, false, 1, 8⟩, ⟨-2, true, 1, 8⟩, ⟨-2, true, 1, 8⟩]
def rows4 : List Row := [⟨3, -1, 2, 9⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, -2, 0, 36⟩, ⟨0, -1, -1, 9⟩, ⟨-1, 0, -1, 1⟩]
def inputs5 : List Stim := [⟨-2, true, 1, 8⟩, ⟨-2, true, 1, 8⟩, ⟨-2, false, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, false, 1, 8⟩]
def rows5 : List Row := [⟨3, -2, 1, 41⟩, ⟨1, -2, -1, 33⟩, ⟨-1, 0, -1, 1⟩, ⟨-1, 1, 0, 9⟩, ⟨0, 0, 0, 1⟩, ⟨0, 0, 0, 1⟩, ⟨0, 2, 2, 36⟩, ⟨2, 2, 4, 32⟩, ⟨4, 1, 5, 9⟩, ⟨5, 2, 7, 33⟩, ⟨7, 2, 9, 33⟩, ⟨9, 0, 9, 1⟩]
def inputs6 : List Stim := [⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩]
def rows6 : List Row := [⟨3, 2, 5, 33⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩, ⟨5, 0, 5, 1⟩]
def inputs7 : List Stim := [⟨-1, false, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨7, false, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, true, 1, 8⟩]
def rows7 : List Row := [⟨3, -2, 1, 36⟩, ⟨1, -1, 0, 9⟩, ⟨0, 0, 0, 1⟩, ⟨0, 2, 2, 57⟩, ⟨2, 2, 4, 41⟩, ⟨4, 2, 6, 33⟩, ⟨6, -2, 4, 36⟩, ⟨4, -1, 3, 9⟩, ⟨3, 0, 3, 1⟩, ⟨3, 2, 5, 41⟩, ⟨5, 2, 7, 33⟩, ⟨7, 2, 9, 33⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (44:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (5:Int)) ∧
  (simulate policy (3) inputs1 = rows1) ∧
  (allSafe policy inputs1 rows1 = true) ∧
  (totalCost rows1 = (86:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows1.getLast?).map Row.after = some (8:Int)) ∧
  (simulate policy (3) inputs2 = rows2) ∧
  (allSafe policy inputs2 rows2 = true) ∧
  (totalCost rows2 = (225:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows2.getLast?).map Row.after = some (1:Int)) ∧
  (simulate policy (3) inputs3 = rows3) ∧
  (allSafe policy inputs3 rows3 = true) ∧
  (totalCost rows3 = (123:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows3.getLast?).map Row.after = some (9:Int)) ∧
  (simulate policy (3) inputs4 = rows4) ∧
  (allSafe policy inputs4 rows4 = true) ∧
  (totalCost rows4 = (63:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows4.getLast?).map Row.after = some (-1:Int)) ∧
  (simulate policy (3) inputs5 = rows5) ∧
  (allSafe policy inputs5 rows5 = true) ∧
  (totalCost rows5 = (230:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows5.getLast?).map Row.after = some (9:Int)) ∧
  (simulate policy (3) inputs6 = rows6) ∧
  (allSafe policy inputs6 rows6 = true) ∧
  (totalCost rows6 = (44:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows6.getLast?).map Row.after = some (5:Int)) ∧
  (simulate policy (3) inputs7 = rows7) ∧
  (allSafe policy inputs7 rows7 = true) ∧
  (totalCost rows7 = (330:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows7.getLast?).map Row.after = some (9:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
