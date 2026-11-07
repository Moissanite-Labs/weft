// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;
// Extracted from weft/README.md

/// @title ProvenanceRegistry
/// @notice On-chain homomorphic vector watermark ledger (spec; not deployed by this repo).
contract ProvenanceRegistry {
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

    function registerGenotype(bytes32 weightHash, bytes32 triggerCommit, bytes32 targetCommit, bytes32 genotypeRoot) external {
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
        require(registries[parentHash].creator != address(0), "ASL_ERROR: PARENT_GENOTYPE_NONEXISTENT");
        require(lineageDAG[childHash] == bytes32(0), "ASL_ERROR: CHILD_LINEAGE_ALREADY_RECORDED");
        lineageDAG[childHash] = parentHash;
        emit LineageSpliced(childHash, parentHash, msg.sender);
    }

    function verifyAttribution(bytes32 weightHash, address claimant) external view returns (bool) {
        bytes32 currentTrack = weightHash;
        for (uint256 i = 0; i < 12; i++) {
            if (currentTrack == bytes32(0)) return false;
            if (registries[currentTrack].creator == claimant) return true;
            currentTrack = lineageDAG[currentTrack];
        }
        return false;
    }

    function getCreator(bytes32 weightHash) external view returns (address) {
        bytes32 currentTrack = weightHash;
        for (uint256 i = 0; i < 12; i++) {
            if (currentTrack == bytes32(0)) return address(0);
            address creator = registries[currentTrack].creator;
            if (creator != address(0)) return creator;
            currentTrack = lineageDAG[currentTrack];
        }
        return address(0);
    }
}
