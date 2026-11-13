import Std

/- Closed-world integer fixed-feature readout. No candidate supplies Lean code. -/
namespace ProofCell

structure Vec3 where
  x : Int
  y : Int
  z : Int
  deriving DecidableEq, Repr

def add (a b : Vec3) : Vec3 := ⟨a.x + b.x, a.y + b.y, a.z + b.z⟩
def dot (a b : Vec3) : Int := a.x*b.x + a.y*b.y + a.z*b.z
def normSq (d : Vec3) : Int := d.x*d.x + d.y*d.y + d.z*d.z

def frozenOK (d : Vec3) (frozen : List Nat) : Prop :=
  ∀ i ∈ frozen, i < 3 ∧ (i = 0 → d.x = 0) ∧ (i = 1 → d.y = 0) ∧ (i = 2 → d.z = 0)

instance (d : Vec3) (f : List Nat) : Decidable (frozenOK d f) :=
  inferInstanceAs (Decidable (∀ i ∈ f, i < 3 ∧ (i = 0 → d.x = 0) ∧ (i = 1 → d.y = 0) ∧ (i = 2 → d.z = 0)))

def Allowed (delta : Vec3) (anchors : List Vec3) (frozen : List Nat) (radiusSq : Int) : Prop :=
  frozenOK delta frozen ∧ 0 ≤ radiusSq ∧ normSq delta ≤ radiusSq ∧
  ∀ a ∈ anchors, dot a delta = 0

instance (d : Vec3) (a : List Vec3) (f : List Nat) (r : Int) : Decidable (Allowed d a f r) :=
  inferInstanceAs (Decidable (frozenOK d f ∧ 0 ≤ r ∧ normSq d ≤ r ∧ ∀ v ∈ a, dot v d = 0))

def Guarantees (before delta : Vec3) (anchors : List Vec3) (frozen : List Nat) (radiusSq : Int) : Prop :=
  (∀ a ∈ anchors, dot a (add before delta) = dot a before) ∧
  frozenOK delta frozen ∧ normSq delta ≤ radiusSq

instance (b d : Vec3) (a : List Vec3) (f : List Nat) (r : Int) : Decidable (Guarantees b d a f r) :=
  inferInstanceAs (Decidable ((∀ v ∈ a, dot v (add b d) = dot v b) ∧ frozenOK d f ∧ normSq d ≤ r))

theorem dot_add (a b d : Vec3) : dot a (add b d) = dot a b + dot a d := by
  simp only [dot, add, Int.mul_add]
  ac_rfl

theorem allowed_guarantees (before delta : Vec3) (anchors : List Vec3) (frozen : List Nat) (radiusSq : Int)
    (h : Allowed delta anchors frozen radiusSq) : Guarantees before delta anchors frozen radiusSq := by
  rcases h with ⟨hf, _, hn, ha⟩
  refine ⟨?_, hf, hn⟩
  intro a membership
  rw [dot_add, ha a membership, Int.add_zero]

#print axioms allowed_guarantees
end ProofCell
