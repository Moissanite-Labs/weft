import Std

/- Data-only exact integer deployment semantics. No external effects are modeled. -/
namespace VerifiedGraft

structure Vec where
  a : Int
  b : Int
  c : Int
  d : Int
  e : Int
  f : Int
  deriving DecidableEq, Repr

structure Mat where
  first : Vec
  second : Vec
  deriving DecidableEq, Repr

def zero : Vec := ⟨0,0,0,0,0,0⟩
def add (x y : Vec) : Vec := ⟨x.a+y.a,x.b+y.b,x.c+y.c,x.d+y.d,x.e+y.e,x.f+y.f⟩
def scale (k : Int) (x : Vec) : Vec := ⟨k*x.a,k*x.b,k*x.c,k*x.d,k*x.e,k*x.f⟩
def dot (x y : Vec) : Int := x.a*y.a+x.b*y.b+x.c*y.c+x.d*y.d+x.e*y.e+x.f*y.f
def matAdd (x y : Mat) : Mat := ⟨add x.first y.first,add x.second y.second⟩
def apply (w : Mat) (x : Vec) : Int × Int := (dot w.first x,dot w.second x)
def normSq (w : Mat) : Int := dot w.first w.first + dot w.second w.second

def SameOn (before after : Mat) (v : Vec) : Prop := apply before v = apply after v
instance (b a : Mat) (v : Vec) : Decidable (SameOn b a v) := inferInstanceAs (Decidable (apply b v = apply a v))

def preserves (b a : Mat) (basis : List Vec) : Bool := basis.all (fun v => decide (SameOn b a v))

/- Integer span: every finite integer-weighted combination of registered vectors. -/
def combine : List (Int × Vec) → Vec
  | [] => zero
  | term :: rest => add (scale term.1 term.2) (combine rest)

theorem dot_add (row x y : Vec) : dot row (add x y) = dot row x + dot row y := by
  simp only [dot,add,Int.mul_add]
  ac_rfl

theorem dot_scale (row : Vec) (k : Int) (x : Vec) : dot row (scale k x) = k * dot row x := by
  simp only [dot,scale,Int.mul_add]
  ac_rfl

theorem span_retention (before after : Mat) (terms : List (Int × Vec))
    (h : ∀ term ∈ terms, SameOn before after term.2) : SameOn before after (combine terms) := by
  induction terms with
  | nil => simp only [SameOn,apply,combine,zero,dot,Int.mul_zero,Int.add_zero]
  | cons term rest ih =>
    have ht := h term (List.mem_cons_self)
    have hr : ∀ t ∈ rest, SameOn before after t.2 := fun t member => h t (List.mem_cons_of_mem term member)
    have tail := ih hr
    have h0 := congrArg Prod.fst ht
    have h1 := congrArg Prod.snd ht
    have t0 := congrArg Prod.fst tail
    have t1 := congrArg Prod.snd tail
    change dot before.first term.2 = dot after.first term.2 at h0
    change dot before.second term.2 = dot after.second term.2 at h1
    change dot before.first (combine rest) = dot after.first (combine rest) at t0
    change dot before.second (combine rest) = dot after.second (combine rest) at t1
    change (dot before.first (add (scale term.1 term.2) (combine rest)), dot before.second (add (scale term.1 term.2) (combine rest))) = (dot after.first (add (scale term.1 term.2) (combine rest)), dot after.second (add (scale term.1 term.2) (combine rest)))
    rw [dot_add,dot_add,dot_scale,dot_scale,h0,h1,t0,t1]
    rw [dot_add,dot_add,dot_scale,dot_scale]

theorem conflict_witness (host target candidate : Mat) (v : Vec)
    (different : apply host v ≠ apply target v)
    (preserved : apply candidate v = apply host v) : apply candidate v ≠ apply target v := by
  intro transferred
  exact different (preserved.symm.trans transferred)

def entries (v : Vec) : List Int := [v.a,v.b,v.c,v.d,v.e,v.f]
def absolute (v : Vec) : Vec := ⟨Int.ofNat v.a.natAbs,Int.ofNat v.b.natAbs,Int.ofNat v.c.natAbs,Int.ofNat v.d.natAbs,Int.ofNat v.e.natAbs,Int.ofNat v.f.natAbs⟩
def basisValid (basis : List Vec) (count : Nat) : Bool :=
  decide (basis.length = count) && basis.all (fun v => decide (((entries v).map Int.natAbs).sum = 1)) &&
  decide ((basis.map absolute).Nodup)
def bounded (w : Mat) (bound : Int) : Bool :=
  (entries w.first ++ entries w.second).all (fun n => decide (-bound ≤ n ∧ n ≤ bound))
def covers (basis native : List Vec) : Bool := native.all (fun v => basis.any (fun w => decide (absolute v = absolute w)))

/- Modes: 0=graft, 1=fork, 2=abstain. Case: false=compatible, true=saturated. -/
def allowed (host delta : Mat) (basis : List Vec) (saturated : Bool) (mode : Nat) : Bool :=
  bounded host 2 && bounded delta 4 && basisValid basis (if saturated then 6 else 3) && decide (normSq delta ≤ 192) &&
  if mode = 0 then preserves host (matAdd host delta) basis
  else if mode = 1 then saturated && decide (delta ≠ ⟨zero,zero⟩)
  else if mode = 2 then decide (delta = ⟨zero,zero⟩)
  else false

def rootAfter (host delta : Mat) (mode : Nat) : Mat := if mode = 0 then matAdd host delta else host
def specialistAfter (host delta : Mat) (mode : Nat) : Option Mat := if mode = 1 then some (matAdd host delta) else none
def transferUsesSpecialist (mode : Nat) : Bool := mode = 1
def nativeUsesSpecialist (_mode : Nat) : Bool := false
def cellCount (mode : Nat) : Nat := if mode = 1 then 2 else 1

def improves (parentA newA parentB newB : Int) : Bool :=
  decide (newA < parentA) && decide (10*newA ≤ 9*parentA) &&
  decide (newB < parentB) && decide (10*newB ≤ 9*parentB)

def squaredError (actual desired : Int × Int) : Int :=
  let a := actual.1-desired.1
  let b := actual.2-desired.2
  a*a+b*b

def totalError (actual desired : Mat) (inputs : List Vec) : Int :=
  (inputs.map (fun v => squaredError (apply actual v) (apply desired v))).sum

#print axioms span_retention
#print axioms conflict_witness
end VerifiedGraft
