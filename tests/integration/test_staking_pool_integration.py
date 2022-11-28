from scripts.utils import get_account, get_contract
from brownie import (
    StakingPool,
    RewardToken,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    network,
    config,
    accounts,
)
from web3 import Web3
import time


def test__stake_and_withdraw_and_get_correct_reward_token_amount():
    # arrange
    account = get_account()
    account_2 = accounts.add(config["wallets"]["from_key_2"])
    staking_pool = StakingPool[-1]
    reward_token = RewardToken[-1]
    proxy_admin = ProxyAdmin[-1]
    proxy = TransparentUpgradeableProxy[-1]
    goat_token = get_contract("goat_token")
    amount = Web3.toWei(100, "ether")
    staking_pool_proxy = Contract.from_abi(
        "StakingPool", proxy.address, StakingPool.abi
    )
    staking_pool_proxy_initial_balance = goat_token.balanceOf(staking_pool_proxy)
    account_initial_balance = goat_token.balanceOf(account)
    account2_initial_balance = goat_token.balanceOf(account_2)
    staking_pool_total_tokens_staked = staking_pool_proxy.totalTokensStaked()

    account_staking_balance_per_token = staking_pool_proxy.stakingBalancePerToken(
        goat_token, account
    )
    account_2_staking_balance_per_token = staking_pool_proxy.stakingBalancePerToken(
        goat_token, account_2
    )

    account_reward_token_initial_balance = reward_token.balanceOf(account)
    account_2_reward_token_initial_balance = reward_token.balanceOf(account_2)

    # act
    goat_token.approve(staking_pool_proxy, amount, {"from": account})
    tx2 = staking_pool_proxy.stake(goat_token.address, amount, {"from": account})

    goat_token.approve(staking_pool_proxy, amount, {"from": account_2})
    tx1 = staking_pool_proxy.stake(goat_token.address, amount, {"from": account_2})

    time.sleep(400)

    staking_pool_proxy.withdraw(goat_token.address, {"from": account})
    staking_pool_proxy.withdraw(goat_token.address, {"from": account_2})

    # assert

    assert staking_pool_proxy.stakingBalancePerToken(goat_token, account) == 0
    assert staking_pool_proxy.stakingBalancePerToken(goat_token, account_2) == 0
    assert reward_token.balanceOf(account) > account_reward_token_initial_balance
    assert reward_token.balanceOf(account_2) > account_2_reward_token_initial_balance
