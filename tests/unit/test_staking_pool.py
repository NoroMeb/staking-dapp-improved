from scripts.utils import get_account, get_contract
from scripts.deploy import main
from brownie import exceptions, chain
import pytest
import time
from web3 import Web3


def test_initialize():
    # arrange / act
    account = get_account()
    staking_pool = main()
    goat_token = get_contract("goat_token")
    link_token = get_contract("link_token")
    random_token = "0xBA62BCfcAaFc6622853cca2BE6Ac7d845BC0f2Dc"
    # assert
    assert staking_pool.isAllowed(goat_token.address) == True
    assert staking_pool.isAllowed(link_token.address) == True
    assert staking_pool.isAllowed(random_token) == False
    with pytest.raises(exceptions.VirtualMachineError):
        staking_pool.initialize([], {"from": account})


def test_withdraw():
    # arrange
    staking_pool, account, amount_staked = test_stake()
    token = get_contract("goat_token")
    lock_time = staking_pool.getLockTime()

    # assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking_pool.withdraw(token, {"from": account})  # must pass lockTime

    # act
    time.sleep(lock_time)
    staking_pool.withdraw(token, {"from": account})

    # assert
    assert token.balanceOf(account) == amount_staked
    assert token.balanceOf(staking_pool) == 0
    assert staking_pool.stakingBalance(token, account) == 0
    assert staking_pool.timeLock(token, account) == 0


def test_stake():
    # arrange
    account = get_account()
    staking_pool = main()
    token = get_contract("goat_token")
    random_token = "0xBA62BCfcAaFc6622853cca2BE6Ac7d845BC0f2Dc"
    amount = token.balanceOf(account)
    print(amount)
    token.approve(staking_pool, amount)

    staking_pool_initial_balance = token.balanceOf(staking_pool)

    # assert
    with pytest.raises(exceptions.VirtualMachineError):
        staking_pool.stake(token, 0, {"from": account})

    # act
    staking_pool.stake(token, amount, {"from": account})

    # assert
    assert token.balanceOf(staking_pool) == staking_pool_initial_balance + amount
    assert token.balanceOf(account) == 0
    assert staking_pool.stakingBalance(token, account) == amount
    assert (chain.time() + staking_pool.getLockTime()) - staking_pool.timeLock(
        token, account
    ) >= 0 and (chain.time() + staking_pool.getLockTime()) - staking_pool.timeLock(
        token, account
    ) <= 3

    return staking_pool, account, amount


def test_add_allowed_token():
    # arrange
    account = get_account()
    non_owner = get_account(index=2)
    staking_pool = main()
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
    staking_pool = main()
    expected_lock_time = 20
    # act

    lock_time = staking_pool.getLockTime()

    # assert
    assert lock_time == expected_lock_time
