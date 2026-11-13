import Std

/- Closed integer policy interpreter; clients provide data, never Lean source. -/
namespace StemCell

structure Policy where
  gainNum : Nat
  gainDen : Nat
  bias : Int
  deadband : Nat
  capLow : Nat
  capHigh : Nat
  deriving DecidableEq, Repr

structure Stim where
  target : Int
  urgent : Bool
  errorWeight : Int
  actionWeight : Int
  deriving DecidableEq, Repr

structure Row where
  before : Int
  action : Int
  after : Int
  cost : Int
  deriving DecidableEq, Repr

def validGenome (parentLow parentHigh : Nat) (p : Policy) : Bool :=
  parentLow ≤ 2 && parentHigh ≤ 2 && p.gainNum ≤ 4 &&
  1 ≤ p.gainDen && p.gainDen ≤ 4 && -2 ≤ p.bias && p.bias ≤ 2 &&
  p.deadband ≤ 3 && p.capLow ≤ parentLow && p.capHigh ≤ parentHigh

def cap (p : Policy) (s : Stim) : Int :=
  if s.urgent then Int.ofNat p.capHigh else Int.ofNat p.capLow

/- Sign-magnitude floor: negative errors round toward zero, not toward -∞. -/
def action (p : Policy) (x : Int) (s : Stim) : Int :=
  let error := s.target - x + p.bias
  let magnitude := Int.ofNat ((p.gainNum * error.natAbs) / p.gainDen)
  let raw := if error.natAbs ≤ p.deadband then 0 else
    if error < 0 then -magnitude else magnitude
  max (-(cap p s)) (min (cap p s) raw)

def transition (p : Policy) (x : Int) (s : Stim) : Row :=
  let k := action p x s
  let after := x + k
  let error := s.target - after
  ⟨x, k, after, s.errorWeight * error * error + s.actionWeight * k * k⟩

def simulate (p : Policy) (x : Int) : List Stim → List Row
  | [] => []
  | s :: ss => let r := transition p x s; r :: simulate p r.after ss

/- State is exactly (x,4-x,5), action exactly (k,-k,0).
   Explicit checks cover continuity, both root anchors, frozen third coordinate,
   local squared norm and immutable root squared norm. -/
def state (x : Int) : Int × Int × Int := (x, 4-x, 5)
def rowSafe (p : Policy) (s : Stim) (r : Row) : Bool :=
  decide (r.after = r.before + r.action) &&
  decide ((state r.after).1 + (state r.after).2.1 = (state r.before).1 + (state r.before).2.1) &&
  decide ((state r.after).2.2 = (state r.before).2.2) &&
  decide ((state r.after).2.2 = 5) &&
  decide (2*r.action*r.action ≤ 2*(cap p s)*(cap p s)) &&
  decide (2*r.action*r.action ≤ 8)

noncomputable def allSafe (p : Policy) (ss : List Stim) : List Row → Bool :=
  List.rec (fun rs => rs.isEmpty)
    (fun s _ recur rs => match rs with
      | [] => false
      | r :: rest => rowSafe p s r && recur rest) ss

def totalCost (rs : List Row) : Int := (rs.map Row.cost).sum

end StemCell
