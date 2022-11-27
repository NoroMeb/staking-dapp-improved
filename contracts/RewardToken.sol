// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract RewardToken is ERC20Votes, Ownable {
    constructor() ERC20("RewardToken", "RWDT") ERC20Permit("RewardToken") {}

    function mint(address _staker, uint256 _amount) public onlyOwner {
        _mint(_staker, _amount);
    }
}
