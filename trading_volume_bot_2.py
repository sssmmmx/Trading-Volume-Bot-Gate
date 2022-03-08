# !/usr/bin/env python
# -*- coding = utf-8 -*-
# @time:2022/3/6 14:21
# Author:sssmmmx
# @File:trading_volume_bot_2.py
# @Software:PyCharm

"""
方案2:
单边刷量，单边套保。
代码逻辑：对于同一个永续合约标的 在开启一组多单和空单后，单边选择一个方向进行等差刷量，在到达一定百分比后，平仓所有标的，重开一组，依次循环。
消耗预估：手续费0.05% + 损耗0.05% 合计约 0.1%
时间周期：较快
"""

import time
from Futures import FuturesAPI


# 设立一组多空单
def make_init_com():
    while True:
        book_info = futures_api.order_book(symbol)
        # 监测 卖1 和 买1 的价差大于0.1%
        if (float(book_info["asks"][0]["p"]) - float(book_info["bids"][0]["p"])) / float(book_info["bids"][0]["p"]) > 0.001:
            print("进行下单")
            px = (float(book_info["asks"][0]["p"]) + float(book_info["bids"][0]["p"])) / 2
            f = f".{order_price_round.count('0')}f"
            px = f"{format(px, f)}"
            buy = futures_api.create_orders(symbol, 1, px, "gtc")
            sell = futures_api.create_orders(symbol, -1, px, "gtc")

            while True:
                # 检查是否完成交易 "status": "finished"
                if futures_api.query_orders(buy['id'])["status"] == "finished" and futures_api.query_orders(sell['id'])["status"] == "finished":
                    print("已完成一组交易")
                    break
                else:
                    time.sleep(1)

            break
        else:
            time.sleep(1)

    return buy['id'], sell['id']


# 一组多空单平仓
def close_com():
    while True:
        time.sleep(1)
        book_info = futures_api.order_book(symbol)
        # 监测 卖1 和 买1 的价差大于0.1%
        if (float(book_info["asks"][0]["p"]) - float(book_info["bids"][0]["p"])) / float(
                book_info["bids"][0]["p"]) > 0.001:
            print("进行下单")
            px = (float(book_info["asks"][0]["p"]) + float(book_info["bids"][0]["p"])) / 2
            f = f".{order_price_round.count('0')}f"
            px = f"{format(px, f)}"

            # 进行平仓 限价px
            m = futures_api.close_orders(symbol, px, "close_long", "gtc")
            n = futures_api.close_orders(symbol, px, "close_short", "gtc")

            while True:
                time.sleep(1)
                # 检查是否完成交易 "status": "finished"
                if futures_api.query_orders(m['id'])["status"] == "finished" and futures_api.query_orders(n['id'])[
                    "status"] == "finished":
                    print("已完成平仓")
                    break


# 选用永续合约市场的标的来进行单边刷量，单边套保。
p = input(f"请输入标的：")
# 转化大写
p = p.upper()
symbol = p + '_USDT'

futures_api = FuturesAPI()      # 实例化futures_api

futures_api.set_dual_mode('usdt')       # 设置持仓模式为双向

one_info = futures_api.query_contract_info(symbol)  # 获取标的信息

order_size_min = one_info['order_size_min']             # 最小下单数量
order_price_round = one_info['order_price_round']       # 委托价格最小单位

print(f"最小下单数量:{order_size_min} 委托价格最小单位:{order_price_round}")
print(f"{symbol}开始进行刷交易量")

# --------------------------------------------------------------------------
# 设立一组多空单
a, b = make_init_com()

# 开始进行单边刷量
interval = 0.001        # 0.1%

t = 0
while t < 5:
    # 查询价格
    ppx = float(futures_api.query_orders(a)["price"]) * (1 + interval)
    f = f".{order_price_round.count('0')}f"
    ppx = f"{format(ppx, f)}"

    # 平仓挂单
    c = futures_api.close_orders(symbol, ppx, "close_long", "gtc")

    while True:
        # 检查是否完成交易 "status": "finished"
        if futures_api.query_orders(a['id'])["status"] == "finished":
            a = futures_api.create_orders(symbol, 1, ppx, "gtc")
            t = t + 1
            break
        else:
            time.sleep(1)
if t == 5:
    close_com()

# --------------------------------------------------------------------------
