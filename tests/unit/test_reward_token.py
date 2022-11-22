from scripts.utils import get_account
from brownie import RewardToken


def test_reward_token():
    # arrange
    account = get_account()

    # act
    reward_token = RewardToken.deploy({"from": account})

    # assert
    assert (
        reward_token.balanceOf(account)
        == reward_token.totalSupply()
        == 1000000 * pow(10, 18)
    )
    assert reward_token.name() == "RewardToken"
    assert reward_token.symbol() == "RWDT"
