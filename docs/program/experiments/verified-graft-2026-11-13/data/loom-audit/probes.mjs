import assert from 'node:assert/strict';
import {projectOrthogonalComplement,gramSchmidtColumns} from './bundle/site/assets/js/aywa-continuum-plasm.js';
import {verifyWeightUpdateSafety} from './bundle/site/assets/js/aywa-invariant-v2.js';
const norm = x => Math.sqrt(x.reduce((a,b)=>a+b*b,0));
const left = (M,u) => [u[0]*M[0]+u[1]*M[2],u[0]*M[1]+u[1]*M[3]];
const right = (M,v) => [M[0]*v[0]+M[1]*v[1],M[2]*v[0]+M[3]*v[1]];
const M = [1,2,3,4], e1=[1,0], e2=[0,1];
const protectedDelta=Array.from(projectOrthogonalComplement(M,2,[e1],[e1]));
assert.deepEqual(protectedDelta,[0,0,0,4]);
const protectedCase={matrix:M,u:[e1],v:[e1],projected_delta:protectedDelta,
  protected_input_output_change:right(protectedDelta,e1),unprotected_input_output_change:right(protectedDelta,e2),
  protected_output_projection_change:left(protectedDelta,e1),scope:'Preserves the specified left/right subspaces; other input-output behavior may change.'};
const correlated=[e1,[Math.SQRT1_2,Math.SQRT1_2]];
const nonorth=Array.from(projectOrthogonalComplement(M,2,correlated,[]));
const normalized=gramSchmidtColumns(correlated,2);
const orthogonalized=Array.from(projectOrthogonalComplement(M,2,normalized,[]));
const residuals=correlated.map(u=>norm(left(nonorth,u)));
assert.ok(residuals[0]>1);
assert.ok(norm(orthogonalized)<1e-12);
const projectionCase={unit_norm_but_nonorthogonal_columns:correlated,input_matrix:M,projected_delta:nonorth,
  residual_left_projection_norms:residuals,after_explicit_gram_schmidt_delta:orthogonalized,
  after_explicit_gram_schmidt_norm:norm(orthogonalized),scope:'Public projector assumes orthonormal columns. Internal normal construction uses Gram-Schmidt; this is a precondition boundary, not evidence that every internal call fails.'};
const baseline=new Float64Array([2**32]), candidate=new Float64Array([2**32+128]);
const unlocked=verifyWeightUpdateSafety(baseline,candidate,120,10,1);
const locked=verifyWeightUpdateSafety(baseline,candidate,120,10,1,new Uint8Array([1]));
assert.equal(unlocked.ok,true);assert.equal(unlocked.distance,0);assert.equal(locked.ok,true);
const floatCase={baseline:Array.from(baseline),candidate:Array.from(candidate),actual_binary64_distance:128,
  checked_binary32_baseline:Array.from(Float32Array.from(baseline)),checked_binary32_candidate:Array.from(Float32Array.from(candidate)),
  radius:120,unlocked_gate:unlocked,locked_gate:locked,
  scope:'Gate checks quantized binary32 values. Committing unrounded binary64 values would not inherit its distance or frozen-bit guarantee.'};
console.log(JSON.stringify({protected_subspace:protectedCase,nonorthogonal_basis:projectionCase,float64_vs_float32:floatCase},null,2));
