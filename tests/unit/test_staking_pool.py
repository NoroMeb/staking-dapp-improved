from scripts.utils import get_account, get_contract
from scripts.deploy import deploy_reward_token_and_staking_pool, REWARDS_PER_BLOCK
from brownie import exceptions, chain
import pytest
from web3 import Web3


def test_initialize():
    # arrange / act
    account = get_account()
    staking_pool, reward_token = deploy_reward_token_and_staking_pool()
    goat_token = get_contract("goat_token")
    link_token = get_contract("link_token")
    random_token = "0xBA62BCfcAaFc6622853cca2BE6Ac7d845BC0f2Dc"

    # assert
    assert staking_pool.isAllowed(goat_token.address) == True
    assert staking_pool.isAllowed(link_token.address) == True
    assert staking_pool.isAllowed(random_token) == False
    with pytest.raises(exceptions.VirtualMachineError):
        staking_pool.initialize([], reward_token, REWARDS_PER_BLOCK, {"from": account})


def test_withdraw(amount_staked):
    # arrange
    account = get_account()
    staking_pool, reward_token = test_stake(amount_staked)
    account = get_account()
    token = get_contract("goat_token")
    lock_time = staking_pool.getLockTime()

    # assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking_pool.withdraw(token, {"from": account})  # must pass lockTime

    # act
    chain.mine(20)
    staking_pool.withdraw(token, {"from": account})

    # assert

    assert token.balanceOf(staking_pool) == 0
    assert staking_pool.stakingBalancePerToken(token, account) == 0
    assert staking_pool.expire(token, account) == 0
    assert staking_pool.stakers(account) == (
        0,
        0,
        chain[-1].number,
    )

    assert reward_token.balanceOf(account) == 220
    # 200 of blocks mained in line 38 + 30 of blocks mined with other transactions


def test_stake(amount_staked):
    # arrange
    account = get_account()
    staking_pool, reward_token = deploy_reward_token_and_staking_pool()
    token = get_contract("goat_token")
    # amount = Web3.toWei(100, "ether")
    token.approve(staking_pool, amount_staked, {"from": account})
    # act
    staking_pool.stake(token, amount_staked, {"from": account})

    # assert

    assert token.balanceOf(staking_pool) == amount_staked
    assert staking_pool.totalTokensStaked() == amount_staked
    assert staking_pool.stakingBalancePerToken(token, account) == amount_staked
    assert (
        staking_pool.expire(token, account)
        == chain[-1].number + staking_pool.lockTime()
    )

    assert staking_pool.stakersArray(0) == account.address
    assert staking_pool.stakers(account) == (amount_staked, 0, chain[-1].number)

    return staking_pool, reward_token


def test_claim_reward(amount_staked):
    # arrange
    account = get_account()
    staking_pool, reward_token = test_stake(amount_staked)

    # act
    staking_pool.claimReward(account, {"from": account})

    # assert
    assert reward_token.balanceOf(account) == 10


def test_add_allowed_token():
    # arrange
    account = get_account()
    non_owner = get_account(index=2)
    staking_pool, reward_token = deploy_reward_token_and_staking_pool()
    token = "0xBA62BCfcAaFc6622853cca2BE6Ac7d845BC0f2Dc"
    token_2 = "0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6"
    # act
    staking_pool.addAllowedToken(token, {"from": account})

    # assert
    assert staking_pool.isAllowed(token) == True
    assert staking_pool.isAllowed(token_2) == False
    with pytest.raises(exceptions.VirtualMachineError):
        staking_pool.addAllowedToken(token_2, {"from": non_owner})

    return staking_pool


def test_remove_allowed_token():
    # arrange
    account = get_account()
    non_owner = get_account(index=2)
    staking_pool = test_add_allowed_token()
    token = "0xBA62BCfcAaFc6622853cca2BE6Ac7d845BC0f2Dc"

    # act
    staking_pool.removeAllowedToken(token, {"from": account})

    # assert
    assert staking_pool.isAllowed(token) == False

    # act / assert
    staking_pool.addAllowedToken(token, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        staking_pool.removeAllowedToken(token, {"from": non_owner})


def test_get_lock_time():
    # arrange
    account = get_account(index=3)
    staking_pool, reward_token = deploy_reward_token_and_staking_pool()
    expected_lock_time = 20
    # act

    lock_time = staking_pool.getLockTime()

    # assert
    assert lock_time == expected_lock_time
