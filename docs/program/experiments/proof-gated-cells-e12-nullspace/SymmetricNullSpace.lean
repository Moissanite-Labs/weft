/-
  Proof-Gated Morphogenetic Cells — E12 Symmetric Null-Space Non-Interference
  ===========================================================================
  Companion formalization to:
    - PR #156 (`docs/program/experiments/proof-gated-cells-2026-11-13/Core.lean`)
    - PR #159 (`docs/program/experiments/e12-plasmid-nullspace-graft-2026-11-12/`)

  Pure Core Lean 4 (`leanprover/lean4:v4.35.0`, zero Mathlib dependencies, zero `sorry`).

  Formalizes the symmetric Jacobian null-space splice operator used in Experiment E12
  (`apply_nullspace_gate` in `e12_plasmid_grafting.py`):
      W_splice = W_keep + W_perp
  where `W_keep = W_host P_keep` has rows in `span(anchors)` and
  `W_perp = ΔW_plasmid (I - P_keep)` has rows in `span(anchors)^⊥`:

    1. `symmetric_splice_shifted_retention`:
       `matVec (matAdd W_keep W_perp) (linComb terms) = matVec W_keep (linComb terms)`
       for ANY shifted linear combination `linComb terms` of native anchors (`∀ p ∈ terms, p.2 ∈ anchors`).
    2. `symmetric_splice_clean_transfer`:
       `matVec (matAdd W_keep W_perp) s_perp = matVec W_perp s_perp`
       for ANY orthogonal transfer probe `s_perp` (`∀ a ∈ anchors, vdot a s_perp = 0`).
    3. `symmetric_splice_frob_pythagorean` & `matScale_preserves_nullspace`:
       `frobNormSq (matAdd W_keep W_perp) = frobNormSq W_keep + frobNormSq W_perp`,
       and scalar RMS damping `matScale alpha W_perp` preserves null-space orthogonality.
    4. `frozen_core_rows_preserved` & `allowedSplice_guarantees`:
       Decidable gate predicate `AllowedSplice` implying `SpliceGuarantees`, plus a
       kernel-checked `4x4` concrete `Plasm` splice certificate (`by decide`).
-/

namespace ProofCell.SymmetricNullSpace

abbrev Vec := List Int
abbrev Mat := List Vec

/-! ## 1. Total Zero-Padded Vector & Matrix Primitives -/

def vadd : Vec → Vec → Vec
  | [], ys => ys
  | xs, [] => xs
  | x :: xs, y :: ys => (x + y) :: vadd xs ys

theorem vadd_nil_left (ys : Vec) : vadd [] ys = ys := rfl

theorem vadd_nil_right (xs : Vec) : vadd xs [] = xs := by
  cases xs <;> rfl

theorem vadd_cons (x y : Int) (xs ys : Vec) :
    vadd (x :: xs) (y :: ys) = (x + y) :: vadd xs ys := rfl

def vscale (c : Int) : Vec → Vec
  | [] => []
  | x :: xs => (c * x) :: vscale c xs

theorem vscale_nil (c : Int) : vscale c [] = [] := rfl

theorem vscale_cons (c x : Int) (xs : Vec) :
    vscale c (x :: xs) = (c * x) :: vscale c xs := rfl

def vdot : Vec → Vec → Int
  | [], _ => 0
  | _, [] => 0
  | x :: xs, y :: ys => x * y + vdot xs ys

theorem vdot_nil_left (ys : Vec) : vdot [] ys = 0 := rfl

theorem vdot_nil_right (xs : Vec) : vdot xs [] = 0 := by
  cases xs <;> rfl

theorem vdot_cons (x y : Int) (xs ys : Vec) :
    vdot (x :: xs) (y :: ys) = x * y + vdot xs ys := rfl

def vnormSq (v : Vec) : Int := vdot v v

def linComb : List (Int × Vec) → Vec
  | [] => []
  | (c, a) :: rest => vadd (vscale c a) (linComb rest)

theorem linComb_nil : linComb [] = [] := rfl

theorem linComb_cons (c : Int) (a : Vec) (rest : List (Int × Vec)) :
    linComb ((c, a) :: rest) = vadd (vscale c a) (linComb rest) := rfl

def matVec : Mat → Vec → Vec
  | [], _ => []
  | r :: rs, s => vdot r s :: matVec rs s

theorem matVec_nil (s : Vec) : matVec [] s = [] := rfl

theorem matVec_cons (r : Vec) (rs : Mat) (s : Vec) :
    matVec (r :: rs) s = vdot r s :: matVec rs s := rfl

def matAdd : Mat → Mat → Mat
  | [], B => B
  | A, [] => A
  | rA :: rsA, rB :: rsB => vadd rA rB :: matAdd rsA rsB

theorem matAdd_nil_left (B : Mat) : matAdd [] B = B := rfl

theorem matAdd_nil_right (A : Mat) : matAdd A [] = A := by
  cases A <;> rfl

theorem matAdd_cons (rA rB : Vec) (rsA rsB : Mat) :
    matAdd (rA :: rsA) (rB :: rsB) = vadd rA rB :: matAdd rsA rsB := rfl

def matScale (alpha : Int) (W : Mat) : Mat :=
  W.map (vscale alpha)

def frobNormSq : Mat → Int
  | [] => 0
  | r :: rs => vnormSq r + frobNormSq rs

/-! ## 2. Bilinearity & Inner-Product Identities -/

theorem vadd_comm (u v : Vec) : vadd u v = vadd v u := by
  induction u generalizing v with
  | nil =>
    rw [vadd_nil_left, vadd_nil_right]
  | cons x xs ih =>
    cases v with
    | nil =>
      rw [vadd_nil_right, vadd_nil_left]
    | cons y ys =>
      have hhead : x + y = y + x := by omega
      have htail : vadd xs ys = vadd ys xs := ih ys
      calc
        vadd (x :: xs) (y :: ys) = (x + y) :: vadd xs ys := rfl
        _ = (y + x) :: vadd xs ys := congrArg (· :: vadd xs ys) hhead
        _ = (y + x) :: vadd ys xs := congrArg ((y + x) :: ·) htail

theorem matAdd_comm (A B : Mat) : matAdd A B = matAdd B A := by
  induction A generalizing B with
  | nil =>
    rw [matAdd_nil_left, matAdd_nil_right]
  | cons rA rsA ih =>
    cases B with
    | nil =>
      rw [matAdd_nil_right, matAdd_nil_left]
    | cons rB rsB =>
      have hhead : vadd rA rB = vadd rB rA := vadd_comm rA rB
      have htail : matAdd rsA rsB = matAdd rsB rsA := ih rsB
      calc
        matAdd (rA :: rsA) (rB :: rsB) = vadd rA rB :: matAdd rsA rsB := rfl
        _ = vadd rB rA :: matAdd rsA rsB := congrArg (· :: matAdd rsA rsB) hhead
        _ = vadd rB rA :: matAdd rsB rsA := congrArg (vadd rB rA :: ·) htail

theorem vdot_comm (u v : Vec) : vdot u v = vdot v u := by
  induction u generalizing v with
  | nil =>
    rw [vdot_nil_left, vdot_nil_right]
  | cons x xs ih =>
    cases v with
    | nil =>
      rw [vdot_nil_right, vdot_nil_left]
    | cons y ys =>
      have hmul : x * y = y * x := Int.mul_comm x y
      have htail : vdot xs ys = vdot ys xs := ih ys
      calc
        vdot (x :: xs) (y :: ys) = x * y + vdot xs ys := rfl
        _ = y * x + vdot xs ys := congrArg (· + vdot xs ys) hmul
        _ = y * x + vdot ys xs := congrArg (y * x + ·) htail

theorem vdot_vadd_right (w u v : Vec) :
    vdot w (vadd u v) = vdot w u + vdot w v := by
  induction w generalizing u v with
  | nil =>
    simp only [vdot_nil_left]
    omega
  | cons z zs ih =>
    cases u with
    | nil =>
      rw [vadd_nil_left, vdot_nil_right]
      omega
    | cons x xs =>
      cases v with
      | nil =>
        rw [vadd_nil_right, vdot_nil_right]
        omega
      | cons y ys =>
        have hdist : z * (x + y) = z * x + z * y := Int.mul_add z x y
        have htail : vdot zs (vadd xs ys) = vdot zs xs + vdot zs ys := ih xs ys
        calc
          vdot (z :: zs) (vadd (x :: xs) (y :: ys))
              = z * (x + y) + vdot zs (vadd xs ys) := rfl
          _ = (z * x + z * y) + (vdot zs xs + vdot zs ys) := by omega
          _ = (z * x + vdot zs xs) + (z * y + vdot zs ys) := by omega
          _ = vdot (z :: zs) (x :: xs) + vdot (z :: zs) (y :: ys) := rfl

theorem vdot_vadd_left (u v w : Vec) :
    vdot (vadd u v) w = vdot u w + vdot v w := by
  have h1 : vdot w u = vdot u w := vdot_comm w u
  have h2 : vdot w v = vdot v w := vdot_comm w v
  calc
    vdot (vadd u v) w = vdot w (vadd u v) := vdot_comm (vadd u v) w
    _ = vdot w u + vdot w v := vdot_vadd_right w u v
    _ = vdot u w + vdot v w := by omega

theorem vdot_vscale_right (w : Vec) (c : Int) (v : Vec) :
    vdot w (vscale c v) = c * vdot w v := by
  induction w generalizing v with
  | nil =>
    simp only [vdot_nil_left, Int.mul_zero]
  | cons z zs ih =>
    cases v with
    | nil =>
      simp only [vscale_nil, vdot_nil_right, Int.mul_zero]
    | cons y ys =>
      have hmul : z * (c * y) = c * (z * y) := by
        calc
          z * (c * y) = (z * c) * y := (Int.mul_assoc z c y).symm
          _ = (c * z) * y := congrArg (· * y) (Int.mul_comm z c)
          _ = c * (z * y) := Int.mul_assoc c z y
      have htail : vdot zs (vscale c ys) = c * vdot zs ys := ih ys
      have hdist : c * (z * y + vdot zs ys) = c * (z * y) + c * vdot zs ys :=
        Int.mul_add c (z * y) (vdot zs ys)
      calc
        vdot (z :: zs) (vscale c (y :: ys))
            = z * (c * y) + vdot zs (vscale c ys) := rfl
        _ = c * (z * y) + c * vdot zs ys := by omega
        _ = c * (z * y + vdot zs ys) := hdist.symm
        _ = c * vdot (z :: zs) (y :: ys) := rfl

theorem vdot_vscale_left (c : Int) (u w : Vec) :
    vdot (vscale c u) w = c * vdot u w := by
  calc
    vdot (vscale c u) w = vdot w (vscale c u) := vdot_comm (vscale c u) w
    _ = c * vdot w u := vdot_vscale_right w c u
    _ = c * vdot u w := congrArg (c * ·) (vdot_comm w u)

theorem vnormSq_vadd_orth (u v : Vec) (horth : vdot u v = 0) :
    vnormSq (vadd u v) = vnormSq u + vnormSq v := by
  have hvu : vdot v u = 0 := by
    rw [vdot_comm]
    exact horth
  simp only [vnormSq, vdot_vadd_left, vdot_vadd_right, horth, hvu]
  omega

/-! ## 3. Core Subspace Non-Interference & Orthogonal Decomposition Theorems -/

/-- Any row orthogonal to every native anchor annihilates arbitrary shifted linear combinations
    in `span(anchors)`, regardless of covariate-shift amplitude on the coefficients. -/
theorem vdot_linComb_eq_zero
    (r : Vec) (anchors : List Vec) (terms : List (Int × Vec))
    (horth : ∀ a ∈ anchors, vdot r a = 0)
    (hterms : ∀ p ∈ terms, p.2 ∈ anchors) :
    vdot r (linComb terms) = 0 := by
  induction terms with
  | nil =>
    exact vdot_nil_right r
  | cons hd tl ih =>
    cases hd with
    | mk c a =>
      have hhead : (c, a) ∈ (c, a) :: tl := List.mem_cons.mpr (Or.inl rfl)
      have ha : a ∈ anchors := hterms (c, a) hhead
      have hra : vdot r a = 0 := horth a ha
      have htl : ∀ p ∈ tl, p.2 ∈ anchors :=
        fun p hp => hterms p (List.mem_cons.mpr (Or.inr hp))
      have ihtl : vdot r (linComb tl) = 0 := ih htl
      have hscale : vdot r (vscale c a) = 0 := by
        calc
          vdot r (vscale c a) = c * vdot r a := vdot_vscale_right r c a
          _ = c * 0 := congrArg (c * ·) hra
          _ = 0 := Int.mul_zero c
      calc
        vdot r (linComb ((c, a) :: tl))
            = vdot r (vadd (vscale c a) (linComb tl)) := rfl
        _ = vdot r (vscale c a) + vdot r (linComb tl) :=
            vdot_vadd_right r (vscale c a) (linComb tl)
        _ = 0 := by omega

theorem matVec_add_annihilated_right (A B : Mat) (s : Vec)
    (hlen : A.length = B.length)
    (hann : ∀ r ∈ B, vdot r s = 0) :
    matVec (matAdd A B) s = matVec A s := by
  induction A generalizing B with
  | nil =>
    cases B with
    | nil => rfl
    | cons _ _ =>
      simp only [List.length_nil, List.length_cons] at hlen
      omega
  | cons rA rsA ih =>
    cases B with
    | nil =>
      simp only [List.length_cons, List.length_nil] at hlen
      omega
    | cons rB rsB =>
      have hlen' : rsA.length = rsB.length := by
        simp only [List.length_cons] at hlen
        omega
      have hrB_zero : vdot rB s = 0 :=
        hann rB (List.mem_cons.mpr (Or.inl rfl))
      have hann' : ∀ r ∈ rsB, vdot r s = 0 :=
        fun r hr => hann r (List.mem_cons.mpr (Or.inr hr))
      have hhead : vdot (vadd rA rB) s = vdot rA s := by
        have hadd : vdot (vadd rA rB) s = vdot rA s + vdot rB s :=
          vdot_vadd_left rA rB s
        omega
      have htail : matVec (matAdd rsA rsB) s = matVec rsA s :=
        ih rsB hlen' hann'
      calc
        matVec (matAdd (rA :: rsA) (rB :: rsB)) s
            = vdot (vadd rA rB) s :: matVec (matAdd rsA rsB) s := rfl
        _ = vdot rA s :: matVec (matAdd rsA rsB) s :=
            congrArg (· :: matVec (matAdd rsA rsB) s) hhead
        _ = vdot rA s :: matVec rsA s :=
            congrArg (vdot rA s :: ·) htail

/-- **Theorem 1 (E12 Distribution-Shifted Native Retention):**
    When every plasmid row in `W_perp` is orthogonal to `anchors`, splicing `W_perp` onto
    `W_keep` causes strictly zero output drift on ANY shifted linear combination `linComb terms`
    of `anchors`. -/
theorem symmetric_splice_shifted_retention
    (W_keep W_perp : Mat) (anchors : List Vec) (terms : List (Int × Vec))
    (hlen : W_keep.length = W_perp.length)
    (hperp : ∀ r ∈ W_perp, ∀ a ∈ anchors, vdot r a = 0)
    (hterms : ∀ p ∈ terms, p.2 ∈ anchors) :
    matVec (matAdd W_keep W_perp) (linComb terms) = matVec W_keep (linComb terms) :=
  matVec_add_annihilated_right W_keep W_perp (linComb terms) hlen
    (fun r hr => vdot_linComb_eq_zero r anchors terms (hperp r hr) hterms)

/-- Membership of row `r` in the linear span of `anchors`. -/
def RowInSpan (anchors : List Vec) (r : Vec) : Prop :=
  ∃ terms : List (Int × Vec), (∀ p ∈ terms, p.2 ∈ anchors) ∧ r = linComb terms

theorem rowInSpan_orth_to_null
    (anchors : List Vec) (r s_perp : Vec)
    (hspan : RowInSpan anchors r)
    (horth_s : ∀ a ∈ anchors, vdot a s_perp = 0) :
    vdot r s_perp = 0 := by
  let ⟨terms, hterms, hr⟩ := hspan
  have horth_s' : ∀ a ∈ anchors, vdot s_perp a = 0 := by
    intro a ha
    rw [vdot_comm]
    exact horth_s a ha
  calc
    vdot r s_perp = vdot s_perp r := vdot_comm r s_perp
    _ = vdot s_perp (linComb terms) := congrArg (vdot s_perp ·) hr
    _ = 0 := vdot_linComb_eq_zero s_perp anchors terms horth_s' hterms

/-- **Theorem 2 (E12 Clean Orthogonal Skill Transfer):**
    Projecting the host onto `span(anchors)` (`W_keep`) ensures `W_keep` exerts zero
    off-manifold interference on any orthogonal transfer channel `s_perp ∈ span(anchors)^⊥`. -/
theorem symmetric_splice_clean_transfer
    (W_keep W_perp : Mat) (anchors : List Vec) (s_perp : Vec)
    (hlen : W_keep.length = W_perp.length)
    (hspan : ∀ r ∈ W_keep, RowInSpan anchors r)
    (horth_s : ∀ a ∈ anchors, vdot a s_perp = 0) :
    matVec (matAdd W_keep W_perp) s_perp = matVec W_perp s_perp := by
  calc
    matVec (matAdd W_keep W_perp) s_perp
        = matVec (matAdd W_perp W_keep) s_perp :=
        congrArg (matVec · s_perp) (matAdd_comm W_keep W_perp)
    _ = matVec W_perp s_perp :=
        matVec_add_annihilated_right W_perp W_keep s_perp hlen.symm
          (fun r hr => rowInSpan_orth_to_null anchors r s_perp (hspan r hr) horth_s)

/-- Row-by-row orthogonality between two conformable matrices. -/
def RowsOrthPaired : Mat → Mat → Prop
  | [], [] => True
  | rA :: rsA, rB :: rsB => vdot rA rB = 0 ∧ RowsOrthPaired rsA rsB
  | _, _ => False

instance decRowsOrthPaired : (A B : Mat) → Decidable (RowsOrthPaired A B)
  | [], [] => isTrue trivial
  | [], _ :: _ => isFalse (fun h => h)
  | _ :: _, [] => isFalse (fun h => h)
  | rA :: rsA, rB :: rsB =>
    match inferInstanceAs (Decidable (vdot rA rB = 0)), decRowsOrthPaired rsA rsB with
    | isTrue h1, isTrue h2 => isTrue ⟨h1, h2⟩
    | isFalse h1, _ => isFalse (fun h => h1 h.1)
    | _, isFalse h2 => isFalse (fun h => h2 h.2)

theorem rowsInSpan_orthPaired_of_null
    (W_keep W_perp : Mat) (anchors : List Vec)
    (hlen : W_keep.length = W_perp.length)
    (hspan : ∀ r ∈ W_keep, RowInSpan anchors r)
    (hperp : ∀ r ∈ W_perp, ∀ a ∈ anchors, vdot r a = 0) :
    RowsOrthPaired W_keep W_perp := by
  induction W_keep generalizing W_perp with
  | nil =>
    cases W_perp with
    | nil => trivial
    | cons _ _ =>
      simp only [List.length_nil, List.length_cons] at hlen
      omega
  | cons rK rsK ih =>
    cases W_perp with
    | nil =>
      simp only [List.length_cons, List.length_nil] at hlen
      omega
    | cons rP rsP =>
      have hlen' : rsK.length = rsP.length := by
        simp only [List.length_cons] at hlen
        omega
      have hrK : RowInSpan anchors rK :=
        hspan rK (List.mem_cons.mpr (Or.inl rfl))
      have hrP : ∀ a ∈ anchors, vdot a rP = 0 := by
        intro a ha
        rw [vdot_comm]
        exact hperp rP (List.mem_cons.mpr (Or.inl rfl)) a ha
      have hdot : vdot rK rP = 0 :=
        rowInSpan_orth_to_null anchors rK rP hrK hrP
      have hspan' : ∀ r ∈ rsK, RowInSpan anchors r :=
        fun r hr => hspan r (List.mem_cons.mpr (Or.inr hr))
      have hperp' : ∀ r ∈ rsP, ∀ a ∈ anchors, vdot r a = 0 :=
        fun r hr => hperp r (List.mem_cons.mpr (Or.inr hr))
      exact ⟨hdot, ih rsP hlen' hspan' hperp'⟩

/-- **Theorem 3 (Pythagorean Frobenius Norm Decomposition & RMS Scaling Invariance):**
    Orthogonal subspace components decompose additively without cross-terms, and scalar
    RMS damping `matScale alpha W_perp` preserves null-space orthogonality. -/
theorem symmetric_splice_frob_pythagorean
    (W_keep W_perp : Mat)
    (horth : RowsOrthPaired W_keep W_perp) :
    frobNormSq (matAdd W_keep W_perp) = frobNormSq W_keep + frobNormSq W_perp := by
  induction W_keep generalizing W_perp with
  | nil =>
    cases W_perp with
    | nil => rfl
    | cons _ _ => cases horth
  | cons rK rsK ih =>
    cases W_perp with
    | nil => cases horth
    | cons rP rsP =>
      let ⟨hdot, hrest⟩ := horth
      have hhead : vnormSq (vadd rK rP) = vnormSq rK + vnormSq rP :=
        vnormSq_vadd_orth rK rP hdot
      have htail : frobNormSq (matAdd rsK rsP) = frobNormSq rsK + frobNormSq rsP :=
        ih rsP hrest
      calc
        frobNormSq (matAdd (rK :: rsK) (rP :: rsP))
            = vnormSq (vadd rK rP) + frobNormSq (matAdd rsK rsP) := rfl
        _ = (vnormSq rK + vnormSq rP) + (frobNormSq rsK + frobNormSq rsP) := by omega
        _ = (vnormSq rK + frobNormSq rsK) + (vnormSq rP + frobNormSq rsP) := by omega
        _ = frobNormSq (rK :: rsK) + frobNormSq (rP :: rsP) := rfl

theorem matScale_preserves_nullspace
    (alpha : Int) (W_perp : Mat) (anchors : List Vec)
    (hperp : ∀ r ∈ W_perp, ∀ a ∈ anchors, vdot r a = 0) :
    ∀ r_scaled ∈ matScale alpha W_perp, ∀ a ∈ anchors, vdot r_scaled a = 0 := by
  induction W_perp with
  | nil =>
    intro r_scaled hr
    cases hr
  | cons r rs ih =>
    intro r_scaled hr a ha
    have hmem : r_scaled = vscale alpha r ∨ r_scaled ∈ matScale alpha rs :=
      List.mem_cons.mp hr
    cases hmem with
    | inl heq =>
      have hra : vdot r a = 0 := hperp r (List.mem_cons.mpr (Or.inl rfl)) a ha
      calc
        vdot r_scaled a = vdot (vscale alpha r) a := congrArg (vdot · a) heq
        _ = alpha * vdot r a := vdot_vscale_left alpha r a
        _ = alpha * 0 := congrArg (alpha * ·) hra
        _ = 0 := Int.mul_zero alpha
    | inr htail =>
      have hperp' : ∀ r' ∈ rs, ∀ a' ∈ anchors, vdot r' a' = 0 :=
        fun r' hr' => hperp r' (List.mem_cons.mpr (Or.inr hr'))
      exact ih hperp' r_scaled htail a ha

/-! ## 4. Frozen Lineage Core & Proof-Gated Splice Contract (PR #156 Extension) -/

def coreRows : Nat → Mat → Mat
  | 0, _ => []
  | _, [] => []
  | k + 1, r :: rs => r :: coreRows k rs

def CoreFrozen : Nat → Mat → Mat → Prop
  | 0, _, _ => True
  | _ + 1, [], [] => True
  | _ + 1, [], _ :: _ => False
  | _ + 1, _ :: _, [] => True
  | k + 1, rK :: rsK, rP :: rsP =>
      (rP.length ≤ rK.length ∧ ∀ y ∈ rP, y = 0) ∧ CoreFrozen k rsK rsP

instance decCoreFrozen : (k : Nat) → (A B : Mat) → Decidable (CoreFrozen k A B)
  | 0, _, _ => isTrue trivial
  | _ + 1, [], [] => isTrue trivial
  | _ + 1, [], _ :: _ => isFalse (fun h => h)
  | _ + 1, _ :: _, [] => isTrue trivial
  | k + 1, rK :: rsK, rP :: rsP =>
    match inferInstanceAs (Decidable (rP.length ≤ rK.length ∧ ∀ y ∈ rP, y = 0)),
          decCoreFrozen k rsK rsP with
    | isTrue h1, isTrue h2 => isTrue ⟨h1, h2⟩
    | isFalse h1, _ => isFalse (fun h => h1 h.1)
    | _, isFalse h2 => isFalse (fun h => h2 h.2)

theorem vadd_zero_row_right (u r : Vec)
    (hlen : r.length ≤ u.length)
    (hzero : ∀ y ∈ r, y = 0) :
    vadd u r = u := by
  induction r generalizing u with
  | nil =>
    exact vadd_nil_right u
  | cons y ys ih =>
    cases u with
    | nil =>
      simp only [List.length_cons, List.length_nil] at hlen
      omega
    | cons x xs =>
      have hlen' : ys.length ≤ xs.length := by
        simp only [List.length_cons] at hlen
        omega
      have hy : y = 0 := hzero y (List.mem_cons.mpr (Or.inl rfl))
      have hys : ∀ z ∈ ys, z = 0 :=
        fun z hz => hzero z (List.mem_cons.mpr (Or.inr hz))
      have hhead : x + y = x := by omega
      have htail : vadd xs ys = xs := ih xs hlen' hys
      calc
        vadd (x :: xs) (y :: ys) = (x + y) :: vadd xs ys := rfl
        _ = x :: vadd xs ys := congrArg (· :: vadd xs ys) hhead
        _ = x :: xs := congrArg (x :: ·) htail

/-- **Theorem 4 (Frozen Core / Watermark Row Preservation):**
    Zeroing the top `k` rows of `W_perp` leaves the organism's top `k` lineage watermark rows
    bitwise identical after plasmid splicing. -/
theorem frozen_core_rows_preserved (k : Nat) (W_keep W_perp : Mat)
    (hfrozen : CoreFrozen k W_keep W_perp) :
    coreRows k (matAdd W_keep W_perp) = coreRows k W_keep := by
  induction k generalizing W_keep W_perp with
  | zero => rfl
  | succ k' ih =>
    cases W_keep with
    | nil =>
      cases W_perp with
      | nil => rfl
      | cons _ _ => cases hfrozen
    | cons rK rsK =>
      cases W_perp with
      | nil => rfl
      | cons rP rsP =>
        let ⟨⟨hlenP, hzeroP⟩, hrest⟩ := hfrozen
        have hhead : vadd rK rP = rK := vadd_zero_row_right rK rP hlenP hzeroP
        have htail : coreRows k' (matAdd rsK rsP) = coreRows k' rsK := ih rsK rsP hrest
        calc
          coreRows (k' + 1) (matAdd (rK :: rsK) (rP :: rsP))
              = vadd rK rP :: coreRows k' (matAdd rsK rsP) := rfl
          _ = rK :: coreRows k' (matAdd rsK rsP) :=
              congrArg (· :: coreRows k' (matAdd rsK rsP)) hhead
          _ = rK :: coreRows k' rsK :=
              congrArg (rK :: ·) htail

theorem map_linComb_in_span
    (anchors : List Vec) (keepWitness : List (List (Int × Vec)))
    (hwit : ∀ terms ∈ keepWitness, ∀ p ∈ terms, p.2 ∈ anchors) :
    ∀ r ∈ keepWitness.map linComb, RowInSpan anchors r := by
  induction keepWitness with
  | nil =>
    intro r hr
    cases hr
  | cons t ts ih =>
    intro r hr
    have hmem : r = linComb t ∨ r ∈ ts.map linComb := List.mem_cons.mp hr
    cases hmem with
    | inl heq =>
      have ht : ∀ p ∈ t, p.2 ∈ anchors :=
        hwit t (List.mem_cons.mpr (Or.inl rfl))
      exact ⟨t, ht, heq⟩
    | inr htail =>
      have hwit' : ∀ terms ∈ ts, ∀ p ∈ terms, p.2 ∈ anchors :=
        fun terms hterms => hwit terms (List.mem_cons.mpr (Or.inr hterms))
      exact ih hwit' r htail

/-- Decidable runtime/compile-time gate predicate generalizing `ProofCell.Allowed` (PR #156)
    from a single 3D vector edit to an arbitrary `m x n` symmetric plasmid splice. -/
def AllowedSplice
    (W_keep W_perp : Mat)
    (anchors : List Vec)
    (keepWitness : List (List (Int × Vec)))
    (coreCount : Nat)
    (frobBudgetSq : Int) : Prop :=
  W_keep.length = W_perp.length ∧
  W_keep = keepWitness.map linComb ∧
  (∀ terms ∈ keepWitness, ∀ p ∈ terms, p.2 ∈ anchors) ∧
  (∀ r ∈ W_perp, ∀ a ∈ anchors, vdot r a = 0) ∧
  CoreFrozen coreCount W_keep W_perp ∧
  0 ≤ frobBudgetSq ∧
  frobNormSq W_keep + frobNormSq W_perp ≤ frobBudgetSq

instance instDecidableAllowedSplice
    (W_keep W_perp : Mat)
    (anchors : List Vec)
    (keepWitness : List (List (Int × Vec)))
    (coreCount : Nat)
    (frobBudgetSq : Int) :
    Decidable (AllowedSplice W_keep W_perp anchors keepWitness coreCount frobBudgetSq) :=
  inferInstanceAs (Decidable
    (W_keep.length = W_perp.length ∧
     W_keep = keepWitness.map linComb ∧
     (∀ terms ∈ keepWitness, ∀ p ∈ terms, p.2 ∈ anchors) ∧
     (∀ r ∈ W_perp, ∀ a ∈ anchors, vdot r a = 0) ∧
     CoreFrozen coreCount W_keep W_perp ∧
     0 ≤ frobBudgetSq ∧
     frobNormSq W_keep + frobNormSq W_perp ≤ frobBudgetSq))

/-- Post-splice invariant bundle guaranteed for any action passing `AllowedSplice`. -/
def SpliceGuarantees
    (W_keep W_perp : Mat)
    (anchors : List Vec)
    (coreCount : Nat)
    (frobBudgetSq : Int) : Prop :=
  (∀ terms : List (Int × Vec), (∀ p ∈ terms, p.2 ∈ anchors) →
    matVec (matAdd W_keep W_perp) (linComb terms) = matVec W_keep (linComb terms)) ∧
  (∀ s_perp : Vec, (∀ a ∈ anchors, vdot a s_perp = 0) →
    matVec (matAdd W_keep W_perp) s_perp = matVec W_perp s_perp) ∧
  (frobNormSq (matAdd W_keep W_perp) = frobNormSq W_keep + frobNormSq W_perp ∧
    frobNormSq (matAdd W_keep W_perp) ≤ frobBudgetSq) ∧
  coreRows coreCount (matAdd W_keep W_perp) = coreRows coreCount W_keep

/-- **Master Soundness Theorem (`AllowedSplice -> SpliceGuarantees`):**
    Any finite witness passing the decidable `AllowedSplice` check satisfies universal
    shifted-retention invariance, interference-free orthogonal skill transfer, exact
    Pythagorean Frobenius norm budgeting, and bitwise frozen-core preservation. -/
theorem allowedSplice_guarantees
    (W_keep W_perp : Mat)
    (anchors : List Vec)
    (keepWitness : List (List (Int × Vec)))
    (coreCount : Nat)
    (frobBudgetSq : Int)
    (h : AllowedSplice W_keep W_perp anchors keepWitness coreCount frobBudgetSq) :
    SpliceGuarantees W_keep W_perp anchors coreCount frobBudgetSq := by
  let ⟨hlen, hwmap, hwit, hperp, hfrozen, _, hbudget⟩ := h
  have hspan_map : ∀ r ∈ keepWitness.map linComb, RowInSpan anchors r :=
    map_linComb_in_span anchors keepWitness hwit
  have hspan : ∀ r ∈ W_keep, RowInSpan anchors r := by
    intro r hr
    rw [hwmap] at hr
    exact hspan_map r hr
  have horth_paired : RowsOrthPaired W_keep W_perp :=
    rowsInSpan_orthPaired_of_null W_keep W_perp anchors hlen hspan hperp
  have hfrob : frobNormSq (matAdd W_keep W_perp) = frobNormSq W_keep + frobNormSq W_perp :=
    symmetric_splice_frob_pythagorean W_keep W_perp horth_paired
  have hfrob_le : frobNormSq (matAdd W_keep W_perp) ≤ frobBudgetSq := by
    omega
  refine ⟨?_, ?_, ⟨hfrob, hfrob_le⟩, ?_⟩
  · intro terms hterms
    exact symmetric_splice_shifted_retention W_keep W_perp anchors terms hlen hperp hterms
  · intro s_perp horth_s
    exact symmetric_splice_clean_transfer W_keep W_perp anchors s_perp hlen hspan horth_s
  · exact frozen_core_rows_preserved coreCount W_keep W_perp hfrozen

/-! ## 5. Concrete 4x4 Morphogenetic Splice Certificate (`by decide`) -/

section ConcreteCertificate

def certAnchor1 : Vec := [1, 1, 0, 0]
def certAnchor2 : Vec := [0, 0, 1, -1]
def certAnchors : List Vec := [certAnchor1, certAnchor2]

def certKeepWitness : List (List (Int × Vec)) :=
  [ [(2, certAnchor1), (1, certAnchor2)],
    [(3, certAnchor1), (-2, certAnchor2)],
    [(-1, certAnchor1), (4, certAnchor2)],
    [(2, certAnchor1), (2, certAnchor2)] ]

def certWKeep : Mat :=
  [ [2, 2, 1, -1],
    [3, 3, -2, 2],
    [-1, -1, 4, -4],
    [2, 2, 2, -2] ]

def certWPerp : Mat :=
  [ [0, 0, 0, 0],
    [2, -2, 1, 1],
    [-1, 1, 3, 3],
    [1, -1, -2, -2] ]

set_option maxRecDepth 100000
set_option maxHeartbeats 2000000

theorem e12_concrete_certificate :
    AllowedSplice certWKeep certWPerp certAnchors certKeepWitness 1 130 ∧
    frobNormSq certWKeep = 86 ∧
    frobNormSq certWPerp = 40 ∧
    frobNormSq (matAdd certWKeep certWPerp) = 126 ∧
    matVec (matAdd certWKeep certWPerp) (linComb [(7, certAnchor1), (-5, certAnchor2)]) =
      [18, 62, -54, 8] ∧
    matVec (matAdd certWKeep certWPerp) [3, -3, 2, 2] =
      matVec certWPerp [3, -3, 2, 2] := by
  decide

theorem e12_concrete_guarantees :
    SpliceGuarantees certWKeep certWPerp certAnchors 1 130 :=
  allowedSplice_guarantees certWKeep certWPerp certAnchors certKeepWitness 1 130
    e12_concrete_certificate.1

end ConcreteCertificate

#print axioms symmetric_splice_shifted_retention
#print axioms symmetric_splice_clean_transfer
#print axioms symmetric_splice_frob_pythagorean
#print axioms allowedSplice_guarantees
#print axioms e12_concrete_certificate

end ProofCell.SymmetricNullSpace
