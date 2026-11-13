import Core
namespace VerifiedGraftConcrete
open VerifiedGraft
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000

theorem certificate : (improves (2) (0) (2) (18) = true) := by decide
#check certificate
#print axioms certificate
end VerifiedGraftConcrete
