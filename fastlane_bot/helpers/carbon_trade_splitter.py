import json
from fastlane_bot.helpers import TradeInstruction

def split_carbon_trades(cfg, trade_instructions: list[TradeInstruction]) -> list[TradeInstruction]:
    new_trade_instructions = []
    for trade in trade_instructions:
        if trade.exchange_name not in cfg.CARBON_V1_FORKS:
            new_trade_instructions.append(trade)
            continue

        carbon_exchanges = {}

        raw_tx_str = trade.raw_txs.replace("'", '"').replace('Decimal("', '').replace('")', '')
        raw_txs = json.loads(raw_tx_str)

        for _tx in raw_txs:
            curve = trade.db.get_pool(cid=str(_tx["cid"]).split("-")[0])
            exchange = curve.exchange_name

            _tx["tknin"] = _get_token_address(cfg, curve, trade.tknin)
            _tx["tknout"] = _get_token_address(cfg, curve, trade.tknout)

            if exchange in carbon_exchanges:
                carbon_exchanges[exchange].append(_tx)
            else:
                carbon_exchanges[exchange] = [_tx]

        for txs in carbon_exchanges.values():
            new_trade_instructions.append(
                TradeInstruction(
                    ConfigObj=cfg,
                    db=trade.db,
                    cid=trade.cid,
                    tknin=trade.tknin,
                    tknout=trade.tknout,
                    amtin=sum([tx["amtin"] for tx in txs]),
                    amtout=sum([tx["amtout"] for tx in txs]),
                    _amtin_wei=sum([tx["_amtin_wei"] for tx in txs]),
                    _amtout_wei=sum([tx["_amtout_wei"] for tx in txs]),
                    raw_txs=str(txs)
                )
            )

    return new_trade_instructions

def _get_token_address(cfg, curve, token_address: str) -> str:
    if cfg.NATIVE_GAS_TOKEN_ADDRESS in curve.get_tokens and token_address == cfg.WRAPPED_GAS_TOKEN_ADDRESS:
        return cfg.NATIVE_GAS_TOKEN_ADDRESS
    if cfg.WRAPPED_GAS_TOKEN_ADDRESS in curve.get_tokens and token_address == cfg.NATIVE_GAS_TOKEN_ADDRESS:
        return cfg.WRAPPED_GAS_TOKEN_ADDRESS
    return token_address
