// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin-upgradeable/contracts/access/OwnableUpgradeable.sol";
import "./RewardToken.sol";

contract StakingPool is OwnableUpgradeable {
    uint256 public constant lockTime = 20;

    mapping(address => bool) public isAllowed;

    uint256 private rewardTokensPerBlock;
    uint256 private constant STAKER_SHARE_PRECISION = 1e12;
    RewardToken public rewardToken;
    uint256 public totalTokensStaked;

    struct Staker {
        uint256 totalAmount;
        uint256 rewards;
        uint256 lastRewardedBlock;
    }

    mapping(address => mapping(address => uint256))
        public stakingBalancePerToken;
    mapping(address => mapping(address => uint256)) public expire;
    mapping(address => Staker) public stakers;

    address[] public stakersArray;

    function initialize(
        address[] calldata _allowedTokens,
        address _rewardTokenAddress,
        uint256 _rewardTokensPerBlock
    ) external initializer {
        __Ownable_init();
        for (uint256 i = 0; i < _allowedTokens.length; i++) {
            isAllowed[_allowedTokens[i]] = true;
        }

        rewardToken = RewardToken(_rewardTokenAddress);
        rewardTokensPerBlock = _rewardTokensPerBlock;
    }

    function stake(address _token, uint256 _amount) external {
        require(_amount > 0, "Insufficient amount");
        require(isAllowed[_token], "Token not allowed");
        updateStakersRewards();
        uint256 stakingBalance = stakingBalancePerToken[_token][msg.sender];
        Staker memory staker = stakers[msg.sender];
        staker.totalAmount = staker.totalAmount + _amount;
        staker.lastRewardedBlock = block.number;
        stakers[msg.sender] = staker;
        totalTokensStaked = totalTokensStaked + _amount;
        stakingBalancePerToken[_token][msg.sender] =
            stakingBalancePerToken[_token][msg.sender] +
            _amount;
        uint256 expired = block.number + lockTime;
        if (!(stakingBalancePerToken[_token][msg.sender] == 0)) {
            // stakes this token for the first time
            expire[_token][msg.sender] = expired;
        }
        if (staker.totalAmount == _amount) {
            // stakes for the first time
            stakersArray.push(msg.sender);
        }
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
    }

    function withdraw(address _token) external {
        require(block.number >= expire[_token][msg.sender], "Not yet");
        uint256 amount = stakingBalancePerToken[_token][msg.sender];
        updateStakersRewards();
        claimReward(msg.sender);

        IERC20(_token).transfer(msg.sender, amount);
        expire[_token][msg.sender] = 0;
        Staker memory staker = stakers[msg.sender];
        totalTokensStaked = totalTokensStaked - amount;
        staker.totalAmount = staker.totalAmount - amount;
        stakingBalancePerToken[_token][msg.sender] = 0;
        stakers[msg.sender] = staker; // save
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

    function claimReward(address _account) public {
        updateStakersRewards();
        Staker storage staker = stakers[_account];
        uint256 rewardsToClaim = staker.rewards;
        staker.rewards = 0;
        rewardToken.mint(_account, rewardsToClaim);
    }

    function updateStakersRewards() public {
        for (uint256 i = 0; i < stakersArray.length; i++) {
            address stakerAddress = stakersArray[i];
            Staker memory staker = stakers[stakerAddress];
            uint256 blocksSinceLastReward = block.number -
                staker.lastRewardedBlock;
            uint256 stakerShare = (staker.totalAmount *
                STAKER_SHARE_PRECISION) / totalTokensStaked;
            uint256 rewards = (blocksSinceLastReward *
                rewardTokensPerBlock *
                stakerShare) / STAKER_SHARE_PRECISION;
            staker.lastRewardedBlock = block.number;
            staker.rewards = staker.rewards + rewards;
            stakers[stakerAddress] = staker;
        }
    }
}
