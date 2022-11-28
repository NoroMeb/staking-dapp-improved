from scripts.utils import get_account
from scripts.deploy import deploy_reward_token_and_staking_pool
from brownie import RewardToken
from web3 import Web3


def test_reward_token():
    # arrange
    account = get_account()

    # act
    staking_pool, reward_token = deploy_reward_token_and_staking_pool()

    # assert
    assert reward_token.name() == "RewardToken"
    assert reward_token.symbol() == "RWDT"


def test_mint():
    # arrange
    account = get_account()
    staking_pool, reward_token = deploy_reward_token_and_staking_pool()
    amount = Web3.toWei(100, "ether")
    # act
    reward_token.mint(account, amount, {"from": staking_pool})

    # assert
    assert reward_token.balanceOf(account) == amount
