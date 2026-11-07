// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

/// @title ProvenanceRegistry
/// @notice On-chain homomorphic vector watermark ledger with cycle-free, depth-bounded lineage DAG (#20, #30).
contract ProvenanceRegistry {
    uint256 public constant MAX_LINEAGE_DEPTH = 12;

    struct VectorWatermark {
        address creator;
        bytes32 triggerVectorCommitment;
        bytes32 targetIdentityCommitment;
        bytes32 baseGenotypeRoot;
        uint256 registrationTimestamp;
    }

    mapping(bytes32 => VectorWatermark) public registries;
    mapping(bytes32 => bytes32) public lineageDAG;

    event ProvenanceRegistered(bytes32 indexed weightHash, address indexed creator, bytes32 baseGenotypeRoot);
    event LineageSpliced(bytes32 indexed childHash, bytes32 indexed parentHash, address indexed splicer);

    function registerGenotype(
        bytes32 weightHash,
        bytes32 triggerCommit,
        bytes32 targetCommit,
        bytes32 genotypeRoot
    ) external {
        require(registries[weightHash].creator == address(0), "ASL_ERROR: GENOTYPE_ALREADY_REGISTERED");
        require(weightHash != bytes32(0), "ASL_ERROR: INVALID_WEIGHT_HASH");
        registries[weightHash] = VectorWatermark({
            creator: msg.sender,
            triggerVectorCommitment: triggerCommit,
            targetIdentityCommitment: targetCommit,
            baseGenotypeRoot: genotypeRoot,
            registrationTimestamp: block.timestamp
        });
        emit ProvenanceRegistered(weightHash, msg.sender, genotypeRoot);
    }

    function recordCrossSplicing(bytes32 childHash, bytes32 parentHash) external {
        require(childHash != bytes32(0) && parentHash != bytes32(0), "ASL_ERROR: INVALID_WEIGHT_HASH");
        require(childHash != parentHash, "ASL_ERROR: SELF_SPLICE_FORBIDDEN");
        require(
            registries[parentHash].creator != address(0) || lineageDAG[parentHash] != bytes32(0),
            "ASL_ERROR: PARENT_GENOTYPE_NONEXISTENT"
        );
        require(lineageDAG[childHash] == bytes32(0), "ASL_ERROR: CHILD_LINEAGE_ALREADY_RECORDED");

        // Enforce cycle-freedom and bounded depth (< MAX_LINEAGE_DEPTH) so root attribution never drops out (#20 L6)
        bytes32 cursor = parentHash;
        uint256 depth = 1;
        while (cursor != bytes32(0)) {
            require(cursor != childHash, "ASL_ERROR: LINEAGE_CYCLE_DETECTED");
            require(depth < MAX_LINEAGE_DEPTH, "ASL_ERROR: MAX_LINEAGE_DEPTH_EXCEEDED");
            cursor = lineageDAG[cursor];
            depth++;
        }

        lineageDAG[childHash] = parentHash;
        emit LineageSpliced(childHash, parentHash, msg.sender);
    }

    function verifyAttribution(bytes32 weightHash, address claimant) external view returns (bool) {
        bytes32 currentTrack = weightHash;
        for (uint256 i = 0; i < MAX_LINEAGE_DEPTH; i++) {
            if (currentTrack == bytes32(0)) return false;
            if (registries[currentTrack].creator == claimant) return true;
            currentTrack = lineageDAG[currentTrack];
        }
        return false;
    }

    function getCreator(bytes32 weightHash) external view returns (address) {
        bytes32 currentTrack = weightHash;
        for (uint256 i = 0; i < MAX_LINEAGE_DEPTH; i++) {
            if (currentTrack == bytes32(0)) return address(0);
            address creator = registries[currentTrack].creator;
            if (creator != address(0)) return creator;
            currentTrack = lineageDAG[currentTrack];
        }
        return address(0);
    }
}
