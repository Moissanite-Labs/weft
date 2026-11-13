// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

interface IProvenanceRegistry {
    function verifyAttribution(bytes32 weightHash, address claimant) external view returns (bool);
}

/// @title WeftTokenTissue
/// @notice Metabolic resource asset ledger with 85%/15% creator/burn excision split (#20, #30).
contract WeftTokenTissue {
    string public constant name = "Syntactic Weft Tissue Token";
    string public constant symbol = "WEFT";
    uint8 public constant decimals = 18;
    uint256 public constant CREATOR_SHARE_BPS = 8500;
    uint256 public constant BPS_DENOMINATOR = 10000;

    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    mapping(address => bool) public authorizedHarnesses;
    address public immutable governorCore;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event CapitalExcision(address indexed swarm, address indexed creator, uint256 value, bytes32 indexed weightHash);
    event HarnessAuthorizationChanged(address indexed harness, bool authorized);

    modifier onlyGovernor() {
        require(msg.sender == governorCore, "ASL_ERROR: ONLY_GOVERNOR_CORE_ALLOWED");
        _;
    }

    modifier onlyAuthorizedHarness() {
        require(authorizedHarnesses[msg.sender] || msg.sender == governorCore, "ASL_ERROR: UNAUTHORIZED_HARNESS_NODE");
        _;
    }

    constructor(address _governorCore) {
        require(_governorCore != address(0), "ASL_ERROR: INVALID_GOVERNOR_ADDRESS");
        governorCore = _governorCore;
        _mint(_governorCore, 21_000_000 * 10**18);
    }

    function mintMetabolicAllocation(address recipient, uint256 value) external onlyGovernor returns (bool) {
        require(recipient != address(0), "ASL_ERROR: MINT_TO_ZERO_ADDRESS");
        _mint(recipient, value);
        return true;
    }

    function transfer(address to, uint256 value) external returns (bool) {
        _transfer(msg.sender, to, value);
        return true;
    }

    function approve(address spender, uint256 value) external returns (bool) {
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }

    function transferFrom(address from, address to, uint256 value) external returns (bool) {
        uint256 currentAllowance = allowance[from][msg.sender];
        if (currentAllowance != type(uint256).max) {
            require(currentAllowance >= value, "ASL_ERROR: INSUFFICIENT_ALLOWANCE");
            unchecked { allowance[from][msg.sender] = currentAllowance - value; }
        }
        _transfer(from, to, value);
        return true;
    }

    function executeExcisionValve(address swarm, address creator, uint256 value, bytes32 weightHash)
        external
        onlyAuthorizedHarness
        returns (bool)
    {
        require(creator != address(0), "ASL_ERROR: INVALID_CREATOR_ADDRESS");
        require(balanceOf[swarm] >= value, "ASL_ERROR: SWARM_METABOLICALLY_STARVED");
        unchecked {
            balanceOf[swarm] -= value;
            uint256 creatorShare = (value * CREATOR_SHARE_BPS) / BPS_DENOMINATOR;
            uint256 burnShare = value - creatorShare;
            balanceOf[creator] += creatorShare;
            totalSupply -= burnShare;
            emit CapitalExcision(swarm, creator, value, weightHash);
            emit Transfer(swarm, creator, creatorShare);
            emit Transfer(swarm, address(0), burnShare);
        }
        return true;
    }

    function setHarnessAuthorization(address harness, bool authorized) external onlyGovernor {
        authorizedHarnesses[harness] = authorized;
        emit HarnessAuthorizationChanged(harness, authorized);
    }

    function slashRogueSwarm(address swarm, address recipient, uint256 amount) external onlyGovernor {
        require(balanceOf[swarm] >= amount, "ASL_ERROR: INSUFFICIENT_SLASHING_BALANCE");
        unchecked {
            balanceOf[swarm] -= amount;
            balanceOf[recipient] += amount;
            emit Transfer(swarm, recipient, amount);
        }
    }

    function _mint(address account, uint256 value) internal {
        totalSupply += value;
        balanceOf[account] += value;
        emit Transfer(address(0), account, value);
    }

    function _transfer(address from, address to, uint256 value) internal {
        require(from != address(0), "ASL_ERROR: TRANSFER_FROM_ZERO_ADDRESS");
        require(to != address(0), "ASL_ERROR: TRANSFER_TO_ZERO_ADDRESS");
        require(balanceOf[from] >= value, "ASL_ERROR: EXCEEDS_BALANCE_LIMIT");
        unchecked {
            balanceOf[from] -= value;
            balanceOf[to] += value;
        }
        emit Transfer(from, to, value);
    }
}
