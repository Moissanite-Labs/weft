import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 2, 0, 1, 1, 2⟩
def inputs0 : List Stim := [⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩]
def rows0 : List Row := [⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩]
def inputs1 : List Stim := [⟨2, true, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, false, 1, 8⟩, ⟨7, true, 1, 8⟩]
def rows1 : List Row := [⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 2, 5, 36⟩, ⟨5, 1, 6, 9⟩, ⟨6, 0, 6, 1⟩, ⟨6, 0, 6, 1⟩, ⟨6, 0, 6, 1⟩, ⟨6, 0, 6, 1⟩]
def inputs2 : List Stim := [⟨2, false, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, true, 1, 8⟩]
def rows2 : List Row := [⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 1, 4, 12⟩, ⟨4, 1, 5, 9⟩, ⟨5, 0, 5, 1⟩, ⟨5, -1, 4, 33⟩, ⟨4, -2, 2, 41⟩, ⟨2, -1, 1, 12⟩, ⟨1, 0, 1, 1⟩, ⟨1, 0, 1, 1⟩, ⟨1, 0, 1, 1⟩]
def inputs3 : List Stim := [⟨5, false, 1, 8⟩, ⟨5, false, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩]
def rows3 : List Row := [⟨3, 1, 4, 9⟩, ⟨4, 0, 4, 1⟩, ⟨4, 0, 4, 1⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 0, 4, 0⟩, ⟨4, 1, 5, 17⟩, ⟨5, 1, 6, 12⟩, ⟨6, 1, 7, 9⟩, ⟨7, 0, 7, 1⟩, ⟨7, 0, 7, 1⟩, ⟨7, 0, 7, 1⟩]
def inputs4 : List Stim := [⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, true, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨-2, false, 1, 8⟩, ⟨-2, true, 1, 8⟩, ⟨-2, true, 1, 8⟩]
def rows4 : List Row := [⟨3, -1, 2, 9⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, 0, 2, 1⟩, ⟨2, -1, 1, 17⟩, ⟨1, -1, 0, 12⟩, ⟨0, -1, -1, 9⟩]
def inputs5 : List Stim := [⟨-2, true, 1, 8⟩, ⟨-2, true, 1, 8⟩, ⟨-2, false, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, false, 1, 8⟩]
def rows5 : List Row := [⟨3, -2, 1, 41⟩, ⟨1, -1, 0, 12⟩, ⟨0, -1, -1, 9⟩, ⟨-1, 0, -1, 0⟩, ⟨-1, 0, -1, 0⟩, ⟨-1, 0, -1, 0⟩, ⟨-1, 2, 1, 41⟩, ⟨1, 1, 2, 12⟩, ⟨2, 1, 3, 9⟩, ⟨3, 2, 5, 41⟩, ⟨5, 1, 6, 12⟩, ⟨6, 1, 7, 9⟩]
def inputs6 : List Stim := [⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩]
def rows6 : List Row := [⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩]
def inputs7 : List Stim := [⟨-1, false, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨7, false, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, true, 1, 8⟩]
def rows7 : List Row := [⟨3, -1, 2, 17⟩, ⟨2, -1, 1, 12⟩, ⟨1, -1, 0, 9⟩, ⟨0, 1, 1, 44⟩, ⟨1, 2, 3, 48⟩, ⟨3, 2, 5, 36⟩, ⟨5, -1, 4, 12⟩, ⟨4, -1, 3, 9⟩, ⟨3, 0, 3, 1⟩, ⟨3, 1, 4, 24⟩, ⟨4, 1, 5, 17⟩, ⟨5, 1, 6, 12⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (12:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs1 = rows1) ∧
  (allSafe policy inputs1 rows1 = true) ∧
  (totalCost rows1 = (55:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows1.getLast?).map Row.after = some (6:Int)) ∧
  (simulate policy (3) inputs2 = rows2) ∧
  (allSafe policy inputs2 rows2 = true) ∧
  (totalCost rows2 = (114:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows2.getLast?).map Row.after = some (1:Int)) ∧
  (simulate policy (3) inputs3 = rows3) ∧
  (allSafe policy inputs3 rows3 = true) ∧
  (totalCost rows3 = (52:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows3.getLast?).map Row.after = some (7:Int)) ∧
  (simulate policy (3) inputs4 = rows4) ∧
  (allSafe policy inputs4 rows4 = true) ∧
  (totalCost rows4 = (55:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows4.getLast?).map Row.after = some (-1:Int)) ∧
  (simulate policy (3) inputs5 = rows5) ∧
  (allSafe policy inputs5 rows5 = true) ∧
  (totalCost rows5 = (186:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows5.getLast?).map Row.after = some (7:Int)) ∧
  (simulate policy (3) inputs6 = rows6) ∧
  (allSafe policy inputs6 rows6 = true) ∧
  (totalCost rows6 = (12:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows6.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs7 = rows7) ∧
  (allSafe policy inputs7 rows7 = true) ∧
  (totalCost rows7 = (241:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows7.getLast?).map Row.after = some (6:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
