# coding=utf-8
"""
Contains the pool class for PancakeswapV2. This class is responsible for handling PancakeswapV2 pools and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any, List

from web3 import Web3
from web3.contract import Contract

from fastlane_bot.data.pools import pancakeswap_v2_pools
from fastlane_bot.events.pools.base import Pool


@dataclass
class PancakeswapV2Pool(Pool):
    """
    Class representing a Pancakeswap pool.
    """

    exchange_name: str = "pancakeswap_v2"

    @staticmethod
    def unique_key() -> str:
        """
        see base class.
        """
        return "address"

    @classmethod
    def event_matches_format(cls, event: Dict[str, Any]) -> bool:
        """
        Check if an event matches the format of a Pancakeswap event.
        """
        event_args = event["args"]
        return "reserve0" in event_args and event["address"] in pancakeswap_v2_pools

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        event_args = event_args["args"]
        data["tkn0_balance"] = event_args["reserve0"]
        data["tkn1_balance"] = event_args["reserve1"]
        for key, value in data.items():
            self.state[key] = value

        data["cid"] = self.state["cid"]
        data["fee"] = self.state["fee"]
        data["fee_float"] = self.state["fee_float"]
        data["exchange_name"] = self.state["exchange_name"]
        return data

    def update_from_contract(self, contract: Contract, tenderly_fork_id: str = None, w3_tenderly: Web3 = None, w3: Web3 = None, tenderly_exchanges: List[str] = None) -> Dict[str, Any]:
        """
        See base class.
        """
        reserve_balance = contract.caller.getReserves()
        params = {
            "fee": "0.0025",
            "fee_float": 0.0025,
            "tkn0_balance": reserve_balance[0],
            "tkn1_balance": reserve_balance[1],
            "exchange_name": "pancakeswap_v2",
        }
        for key, value in params.items():
            self.state[key] = value
        return params