# !/usr/bin/env python
# -*- coding = utf-8 -*-
# @time:2022/3/6 10:31
# Author:sssmmmx
# @File:trading_volume_bot_0.py
# @Software:PyCharm

"""
方案0：
市价同进同出。
消耗预估：手续费0.05% + 损耗0.06% 合计约 0.15%
时间周期：较快
"""

import time
from Futures import FuturesAPI

# 选用永续合约市场的标的来进行对敲交易，进行刷交易量。
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
print(f"{symbol}开始进行撮合交易")
t = 0

# 进入永续合约交易市场 开始监测该标的的 bid 和 ask
while t < 5:
    time.sleep(1)
    book_info = futures_api.order_book(symbol)
    # 监测 卖1 和 买1 的价差大于0.1%
    if (float(book_info["asks"][0]["p"]) - float(book_info["bids"][0]["p"])) / float(book_info["bids"][0]["p"]) > 0.001:
        print("进行下单")
        buy = futures_api.create_orders(symbol, 1, "0", "ioc")
        sell = futures_api.create_orders(symbol, -1, "0", "ioc")

        while True:
            # 检查是否完成交易 "status": "finished"
            if futures_api.query_orders(buy['id'])["status"] == "finished" and futures_api.query_orders(sell['id'])["status"] == "finished":
                print("已完成一组交易")
                t = t + 1
                break
            else:
                time.sleep(1)

# 进行平仓 市价
a = futures_api.close_orders(symbol, "0", "close_long", "ioc")
b = futures_api.close_orders(symbol, "0", "close_short", "ioc")

while True:
    time.sleep(1)
    # 检查是否完成交易 "status": "finished"
    if futures_api.query_orders(a['id'])["status"] == "finished" and futures_api.query_orders(b['id'])["status"] == "finished":
        print("已完成平仓")
        break
