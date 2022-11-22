// SPDX-License-Identifier: MIT

pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/proxy/utils/Initializable.sol";

contract StakingPool is Ownable, Initializable {
    uint256 public constant lockTime = 1 days;
    mapping(address => bool) isAllowed;

    mapping(address => mapping(address => uint256)) public stakingBalance;
    mapping(address => mapping(address => uint256)) public timeLock;

    function initalizer() external initializer {}

    function stake(address _token, uint256 _amount) external {
        require(isAllowed[_token] == true, "Token in not allowed yet");
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        stakingBalance[_token][msg.sender] = _amount;
        uint256 expire = block.timestamp + lockTime;
        uint256 balance = stakingBalance[_token][msg.sender];
        if (balance == 0) {
            timeLock[_token][msg.sender] = expire;
        }
    }

    function withdraw() external {}

    function addAllowedToken(address _token) external onlyOwner {}
}
