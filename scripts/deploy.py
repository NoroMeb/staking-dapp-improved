from scripts.utils import get_account, encode_function_data, get_contract
from brownie import (
    StakingPool,
    RewardToken,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
)


def main():
    account = get_account()
    staking_pool = StakingPool.deploy({"from": account})
    goat_token = get_contract("goat_token")
    link_token = get_contract("link_token")

    allowed_tokens = [goat_token.address, link_token.address]

    initalizer = encode_function_data(staking_pool.initialize, allowed_tokens)
    reward_token = deploy_reward_token()
    proxy_admin = ProxyAdmin.deploy({"from": account})
    proxy = TransparentUpgradeableProxy.deploy(
        staking_pool.address,
        proxy_admin,
        initalizer,
        {"from": account},
    )

    staking_pool = Contract.from_abi("StakingPool", proxy.address, StakingPool.abi)
    reward_token.transfer(staking_pool, reward_token.balanceOf(account))

    return staking_pool


def deploy_reward_token():
    account = get_account()
    reward_token = RewardToken.deploy({"from": account})
    return reward_token
