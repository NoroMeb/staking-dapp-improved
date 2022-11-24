// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin-upgradeable/contracts/access/OwnableUpgradeable.sol";

contract StakingPool is OwnableUpgradeable {
    uint256 private constant lockTime = 20 seconds;

    address[] public allowedTokens;
    mapping(address => bool) public isAllowed;
    mapping(address => mapping(address => uint256)) public stakingBalance;
    mapping(address => mapping(address => uint256)) public timeLock;

    IERC20 public immutable rewardsToken;

    uint256 public duration;
    uint256 public finishAt;
    uint256 public updatedAt;
    uint256 public rewardRate;
    uint256 public rewardPerTokenStored;
    mapping(address => uint256) public userRewardPerTokenPaid;
    mapping(address => uint256) public rewards;

    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;

    function initialize(
        address[] calldata _allowedTokens,
        address _rewardsToken
    ) external initializer {
        __Ownable_init();
        for (uint256 i = 0; i < _allowedTokens.length; i++) {
            isAllowed[_allowedTokens[i]] = true;
        }

        rewardsToken = IERC20(_rewardsToken);
    }

    function stake(address _token, uint256 _amount) external {
        require(_amount > 0, "Invalid amount");
        require(isAllowed[_token] == true, "Token in not allowed yet");
        uint256 balance = stakingBalance[_token][msg.sender];
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        stakingBalance[_token][msg.sender] = _amount;
        uint256 expire = block.timestamp + lockTime;
        if (balance == 0) {
            timeLock[_token][msg.sender] = expire;
        }
    }

    function withdraw(address _token) external {
        require(block.timestamp >= timeLock[_token][msg.sender], "Not yet");
        uint256 amount = stakingBalance[_token][msg.sender];
        stakingBalance[_token][msg.sender] = 0;
        IERC20(_token).transfer(msg.sender, amount);
        timeLock[_token][msg.sender] = 0;
    }

    function addAllowedToken(address _token) external onlyOwner {
        isAllowed[_token] = true;
    }

    function removeAllowedToken(address _token) external onlyOwner {
        isAllowed[_token] = false;
    }

    function getLockTime() external pure returns (uint256) {
        return lockTime;
    }

    function setRewardDuration(uint256 _duration) external {}

    function notifyRewardAmount(uint256 _amount) external {}

    function claimReward() external {}
}
