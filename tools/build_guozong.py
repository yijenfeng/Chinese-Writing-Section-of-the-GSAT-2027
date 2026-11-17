# -*- coding: utf-8 -*-
"""產生國綜單元 10–20 的網頁。在 repo 根目錄執行：python3 tools/build_guozong.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gz_u10_u11, gz_u12_u14, gz_u15_u17, gz_u18, gz_u19, gz_u20

UNITS = [
    ("國綜考試規格", gz_u10_u11.build_u10), ("核心古文十五篇", gz_u10_u11.build_u11),
    ("文言文閱讀", gz_u12_u14.build_u12), ("閱讀理解", gz_u12_u14.build_u13), ("混合題作答", gz_u12_u14.build_u14),
    ("字音字形成語", gz_u15_u17.build_u15), ("文法修辭應用文", gz_u15_u17.build_u16), ("國學常識", gz_u15_u17.build_u17), ("歷屆作答卡", gz_u18.build_u18), ("比較型多選題", gz_u19.build_u19), ("國學常識六十天", gz_u20.build_u20),
]
if __name__ == "__main__":
    total = 0
    for slug, fn in UNITS:
        c = fn()
        total += c.mc
        print("%s.html　選擇題 %d　手寫題 %d" % (slug, c.mc, c.w))
    print("選擇題合計", total)
