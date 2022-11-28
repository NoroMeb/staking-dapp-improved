from scripts.utils import get_account, encode_function_data, get_contract
from brownie import (
    StakingPool,
    RewardToken,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    network,
    config,
)
from web3 import Web3

REWARDS_PER_BLOCK = Web3.toWei(10, "ether")


def main():
    deploy_reward_token_and_staking_pool()


def deploy_reward_token_and_staking_pool():
    account = get_account()
    goat_token = get_contract("goat_token")
    link_token = get_contract("link_token")
    allowed_tokens = [goat_token.address, link_token.address]

    reward_token = RewardToken.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    staking_pool = StakingPool.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    initalizer = encode_function_data(
        staking_pool.initialize, allowed_tokens, reward_token.address, REWARDS_PER_BLOCK
    )
    proxy_admin = ProxyAdmin.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    proxy = TransparentUpgradeableProxy.deploy(
        staking_pool.address,
        proxy_admin,
        initalizer,
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )

    staking_pool_proxy = Contract.from_abi(
        "StakingPool", proxy.address, StakingPool.abi
    )

    reward_token.transferOwnership(staking_pool_proxy, {"from": account})

    return (staking_pool_proxy, reward_token)
