// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";

contract RewardToken is ERC20Votes {
    constructor() ERC20("RewardToken", "RWDT") ERC20Permit("RewardToken") {
        _mint(msg.sender, 1000000 * 10**18);
    }
}
