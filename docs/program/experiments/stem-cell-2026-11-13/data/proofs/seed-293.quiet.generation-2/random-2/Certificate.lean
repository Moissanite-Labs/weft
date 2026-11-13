import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 4, 0, 3, 1, 0⟩
def inputs0 : List Stim := [⟨2, false, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, true, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, false, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, true, 1, 8⟩, ⟨-1, true, 1, 8⟩]
def rows0 : List Row := [⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, -1, 2, 17⟩, ⟨2, 0, 2, 9⟩, ⟨2, 0, 2, 9⟩, ⟨2, 0, 2, 9⟩, ⟨2, 0, 2, 9⟩, ⟨2, 0, 2, 9⟩]
def inputs1 : List Stim := [⟨1, false, 1, 8⟩, ⟨1, true, 1, 8⟩, ⟨1, true, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, true, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, true, 1, 8⟩]
def rows1 : List Row := [⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 9⟩, ⟨3, 0, 3, 9⟩, ⟨3, 0, 3, 9⟩, ⟨3, 0, 3, 9⟩, ⟨3, 0, 3, 9⟩, ⟨3, 0, 3, 9⟩]
def inputs2 : List Stim := [⟨5, false, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨5, true, 1, 8⟩, ⟨7, false, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, false, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨2, false, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, false, 1, 8⟩]
def rows2 : List Row := [⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 1, 4, 17⟩, ⟨4, 0, 4, 9⟩, ⟨4, 0, 4, 9⟩, ⟨4, 0, 4, 4⟩, ⟨4, 0, 4, 4⟩, ⟨4, 0, 4, 4⟩, ⟨4, 0, 4, 1⟩, ⟨4, 0, 4, 1⟩, ⟨4, 0, 4, 1⟩]
def inputs3 : List Stim := [⟨3, false, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨4, false, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨3, false, 1, 8⟩]
def rows3 : List Row := [⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 1⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩, ⟨3, 0, 3, 0⟩]
def inputs4 : List Stim := [⟨7, false, 1, 8⟩, ⟨7, false, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, false, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨7, false, 1, 8⟩, ⟨7, true, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, false, 1, 8⟩]
def rows4 : List Row := [⟨3, 1, 4, 17⟩, ⟨4, 0, 4, 9⟩, ⟨4, 0, 4, 9⟩, ⟨4, 0, 4, 9⟩, ⟨4, 0, 4, 9⟩, ⟨4, 0, 4, 9⟩, ⟨4, 0, 4, 9⟩, ⟨4, 0, 4, 9⟩, ⟨4, 0, 4, 9⟩, ⟨4, 0, 4, 16⟩, ⟨4, 0, 4, 16⟩, ⟨4, -1, 3, 17⟩]
def inputs5 : List Stim := [⟨-2, false, 1, 8⟩, ⟨-2, true, 1, 8⟩, ⟨-2, false, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨6, true, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, false, 1, 8⟩]
def rows5 : List Row := [⟨3, -1, 2, 24⟩, ⟨2, 0, 2, 16⟩, ⟨2, -1, 1, 17⟩, ⟨1, 0, 1, 1⟩, ⟨1, 0, 1, 1⟩, ⟨1, 0, 1, 1⟩, ⟨1, 0, 1, 25⟩, ⟨1, 0, 1, 25⟩, ⟨1, 0, 1, 25⟩, ⟨1, 1, 2, 44⟩, ⟨2, 1, 3, 33⟩, ⟨3, 1, 4, 24⟩]
def inputs6 : List Stim := [⟨8, false, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, true, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨8, false, 1, 8⟩, ⟨3, true, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨3, false, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, true, 1, 8⟩]
def rows6 : List Row := [⟨3, 1, 4, 24⟩, ⟨4, 0, 4, 16⟩, ⟨4, 0, 4, 16⟩, ⟨4, 1, 5, 17⟩, ⟨5, 0, 5, 9⟩, ⟨5, 0, 5, 9⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 4⟩, ⟨5, 0, 5, 25⟩, ⟨5, -1, 4, 24⟩, ⟨4, 0, 4, 16⟩]
def inputs7 : List Stim := [⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨1, false, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, true, 1, 8⟩, ⟨0, false, 1, 8⟩, ⟨0, true, 1, 8⟩]
def rows7 : List Row := [⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 4⟩, ⟨3, 0, 3, 9⟩, ⟨3, 0, 3, 9⟩, ⟨3, 0, 3, 9⟩, ⟨3, 0, 3, 9⟩, ⟨3, 0, 3, 9⟩, ⟨3, 0, 3, 9⟩, ⟨3, 0, 3, 9⟩, ⟨3, 0, 3, 9⟩, ⟨3, 0, 3, 9⟩]
theorem certificate : (validGenome 1 1 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (68:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (2:Int)) ∧
  (simulate policy (3) inputs1 = rows1) ∧
  (allSafe policy inputs1 rows1 = true) ∧
  (totalCost rows1 = (78:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows1.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs2 = rows2) ∧
  (allSafe policy inputs2 rows2 = true) ∧
  (totalCost rows2 = (62:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows2.getLast?).map Row.after = some (4:Int)) ∧
  (simulate policy (3) inputs3 = rows3) ∧
  (allSafe policy inputs3 rows3 = true) ∧
  (totalCost rows3 = (3:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows3.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs4 = rows4) ∧
  (allSafe policy inputs4 rows4 = true) ∧
  (totalCost rows4 = (138:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows4.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs5 = rows5) ∧
  (allSafe policy inputs5 rows5 = true) ∧
  (totalCost rows5 = (236:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows5.getLast?).map Row.after = some (4:Int)) ∧
  (simulate policy (3) inputs6 = rows6) ∧
  (allSafe policy inputs6 rows6 = true) ∧
  (totalCost rows6 = (168:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows6.getLast?).map Row.after = some (4:Int)) ∧
  (simulate policy (3) inputs7 = rows7) ∧
  (allSafe policy inputs7 rows7 = true) ∧
  (totalCost rows7 = (93:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows7.getLast?).map Row.after = some (3:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
