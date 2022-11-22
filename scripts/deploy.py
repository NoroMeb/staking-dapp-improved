from scripts.utils import get_account
from brownie import StakingPool


def main():
    account = get_account()
    stake = StakingPool.deploy({"from": account})
    stake.stake({"from": account})
    print(stake.lockTime())
