// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

interface IWeftTokenTissue {
    function slashRogueSwarm(address swarm, address recipient, uint256 amount) external;
    function setHarnessAuthorization(address harness, bool authorized) external;
    function mintMetabolicAllocation(address recipient, uint256 value) external returns (bool);
}

interface IProvenanceRegistry {
    function getCreator(bytes32 weightHash) external view returns (address);
}

/// @title TensionGovernor
/// @notice Balancing court of the Syntactic Weft extracted from `weft/README.md` §15.2 (#20, #30).
/// @dev Enforces independent adjudication so a reporting harness cannot self-award a slash (L4, L5).
contract TensionGovernor {
    uint256 public constant MAX_SAFE_TENSION = 85;
    uint256 public constant CRITICAL_FRACTION_PENALTY = 500 * 10**18;

    struct StructuralDispute {
        address reportingHarness;
        address rogueSwarm;
        bytes32 corruptedWeightHash;
        uint256 structuralTensionTelemetry;
        uint256 reportTimestamp;
        bool adjudicated;
    }

    IWeftTokenTissue public tokenTissue;
    IProvenanceRegistry public provenanceRegistry;
    address public technicalWeaverCore;
    bool public enforceIndependentAdjudicator;

    uint256 public globalDisputeCount;
    mapping(uint256 => StructuralDispute) public disputes;

    event TensionAlertLog(uint256 indexed disputeId, address indexed harness, uint256 tension, bytes32 weightHash);
    event DisputeAdjudicated(uint256 indexed disputeId, bool confirmedMalicious, address indexed enforcementAction);

    modifier onlyWeaver() {
        require(msg.sender == technicalWeaverCore, "ASL_ERROR: ONLY_TECHNICAL_WEAVER_ALLOWED");
        _;
    }

    constructor() {
        technicalWeaverCore = msg.sender;
        enforceIndependentAdjudicator = true;
    }

    function setCoreContracts(address _tokenTissue, address _provenanceRegistry) external onlyWeaver {
        require(_tokenTissue != address(0) && _provenanceRegistry != address(0), "ASL_ERROR: INVALID_ADDRESS");
        tokenTissue = IWeftTokenTissue(_tokenTissue);
        provenanceRegistry = IProvenanceRegistry(_provenanceRegistry);
    }

    function setIndependentAdjudicatorPolicy(bool enforced) external onlyWeaver {
        enforceIndependentAdjudicator = enforced;
    }

    function allocateMetabolicSeed(address recipient, uint256 value) external onlyWeaver {
        tokenTissue.mintMetabolicAllocation(recipient, value);
    }

    function reportTensionFracture(
        address rogueSwarm,
        bytes32 weightHash,
        uint256 tensionTelemetry
    ) external returns (uint256) {
        require(rogueSwarm != address(0), "ASL_ERROR: INVALID_SWARM_ADDRESS");
        require(weightHash != bytes32(0), "ASL_ERROR: INVALID_WEIGHT_HASH");
        require(
            tensionTelemetry > MAX_SAFE_TENSION,
            "ASL_ERROR: NORMAL_OPERATIONAL_HOMEOSTASIS_NO_INTERVENTION_REQUIRED"
        );

        uint256 disputeId = ++globalDisputeCount;
        disputes[disputeId] = StructuralDispute({
            reportingHarness: msg.sender,
            rogueSwarm: rogueSwarm,
            corruptedWeightHash: weightHash,
            structuralTensionTelemetry: tensionTelemetry,
            reportTimestamp: block.timestamp,
            adjudicated: false
        });

        emit TensionAlertLog(disputeId, msg.sender, tensionTelemetry, weightHash);
        return disputeId;
    }

    function adjudicateTensionDispute(uint256 disputeId, bool confirmMalicious) external onlyWeaver {
        StructuralDispute storage dispute = disputes[disputeId];
        require(dispute.reportTimestamp != 0, "ASL_ERROR: DISPUTE_NONEXISTENT");
        require(!dispute.adjudicated, "ASL_ERROR: DISPUTE_ALREADY_ADJUDICATED");
        if (enforceIndependentAdjudicator) {
            require(
                msg.sender != dispute.reportingHarness,
                "ASL_ERROR: REPORTER_CANNOT_SELF_ADJUDICATE"
            );
        }

        dispute.adjudicated = true;

        if (confirmMalicious) {
            address victimCreator = provenanceRegistry.getCreator(dispute.corruptedWeightHash);
            address recipient = victimCreator != address(0) ? victimCreator : dispute.reportingHarness;
            tokenTissue.slashRogueSwarm(dispute.rogueSwarm, recipient, CRITICAL_FRACTION_PENALTY);
            emit DisputeAdjudicated(disputeId, true, recipient);
        } else {
            emit DisputeAdjudicated(disputeId, false, address(0));
        }
    }

    function changeHarnessVerification(address harness, bool status) external onlyWeaver {
        tokenTissue.setHarnessAuthorization(harness, status);
    }

    function transferWeaverCore(address newWeaver) external onlyWeaver {
        require(newWeaver != address(0), "ASL_ERROR: INVALID_WEAVER_ADDRESS");
        technicalWeaverCore = newWeaver;
    }
}
