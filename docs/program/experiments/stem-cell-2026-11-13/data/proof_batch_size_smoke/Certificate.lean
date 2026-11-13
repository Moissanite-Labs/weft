import Core
namespace StemCellConcrete
open StemCell
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
def policy : Policy := ⟨1, 1, 0, 0, 2, 2⟩
def inputs0 : List Stim := [⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩]
def rows0 : List Row := [⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩]
def inputs1 : List Stim := [⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩]
def rows1 : List Row := [⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩]
def inputs2 : List Stim := [⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩]
def rows2 : List Row := [⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩]
def inputs3 : List Stim := [⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩]
def rows3 : List Row := [⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩]
def inputs4 : List Stim := [⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩]
def rows4 : List Row := [⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩]
def inputs5 : List Stim := [⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩]
def rows5 : List Row := [⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩]
def inputs6 : List Stim := [⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩]
def rows6 : List Row := [⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩]
def inputs7 : List Stim := [⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩, ⟨0, false, 2, 1⟩, ⟨6, true, 2, 1⟩]
def rows7 : List Row := [⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩, ⟨3, -2, 1, 6⟩, ⟨1, 2, 3, 22⟩]
theorem certificate : (validGenome 2 2 policy = true) ∧
  (simulate policy (3) inputs0 = rows0) ∧
  (allSafe policy inputs0 rows0 = true) ∧
  (totalCost rows0 = (168:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows0.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs1 = rows1) ∧
  (allSafe policy inputs1 rows1 = true) ∧
  (totalCost rows1 = (168:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows1.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs2 = rows2) ∧
  (allSafe policy inputs2 rows2 = true) ∧
  (totalCost rows2 = (168:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows2.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs3 = rows3) ∧
  (allSafe policy inputs3 rows3 = true) ∧
  (totalCost rows3 = (168:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows3.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs4 = rows4) ∧
  (allSafe policy inputs4 rows4 = true) ∧
  (totalCost rows4 = (168:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows4.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs5 = rows5) ∧
  (allSafe policy inputs5 rows5 = true) ∧
  (totalCost rows5 = (168:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows5.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs6 = rows6) ∧
  (allSafe policy inputs6 rows6 = true) ∧
  (totalCost rows6 = (168:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows6.getLast?).map Row.after = some (3:Int)) ∧
  (simulate policy (3) inputs7 = rows7) ∧
  (allSafe policy inputs7 rows7 = true) ∧
  (totalCost rows7 = (168:Int)) ∧
  ((3:Int) = (3:Int)) ∧
  ((rows7.getLast?).map Row.after = some (3:Int)) := by decide
#check certificate
#print axioms certificate
end StemCellConcrete
