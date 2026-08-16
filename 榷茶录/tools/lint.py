#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""《榷茶录》正文机械扫描。用法：python tools/lint.py drafts/volume-01/chapter-021.md

只扫机械项，语义项（接缝审计六项）仍须主控肉眼过。
扫描口径出自 style-guides/project-voice.md 与 HANDOFF.md 第五节。
"""
import io
import re
import sys

# (名称, 正则, 允许次数, 说明)
RULES = [
    ("破折号", "——", 0, "全书禁用"),
    ("仿佛如同", "仿佛|如同", 0, "全书禁用"),
    ("半角逗号", ",", 0, "全文中文标点"),
    ("禁用结论词", "终于明白|才明白|心头一|隐约觉得", 0, "叙述者替人物宣布结论"),
    # 第12章那处朱红是已裁定的例外（保留色第四种：她本人以父亲手法所下的私批），故排除该章。
    ("保留色", "朱红|殷红|通红|血红|绯红|正红|赤红", 0, "正红一系是保留色。例外见 continuity-log 2026-08-16 第四种"),
    ("元叙述", "第[一二三四五六七八九十百]+章|本章|上一章", 0, "正文里不许出现章号"),
    # 只抓把「三百八十」当作批次上限来写的情形。三百八十／三百八十一等作为「异常到此为止」
    # 的续核号是合法的（第4章），故限定在「至/到...三百八十」这种区间上限写法。
    ("批次上限错写", "[至到]三百八十(?![一二三四五六七八九])", 0, "正典是三百六十九至三百七十八，共十个号"),
]

# 相对时间表述：不是错，但每一处都要人工核对是否与时间线对得上
SOFT = [
    ("相对时间", "昨日|昨夜|昨天|前日|旧年|去年|上回|上一趟|数日后|次日|三日前|几日前"),
    # 深红／暗红不在硬禁之列：官印印色本就是「橘调深红」、墨底「暗红光泽」（第1章正典）。
    # 但保留色纪律比正则宽，凡出现一律人工确认用在父亲暗记、官印验讫戳、血，或她本人的私批。
    ("保留色边缘", "深红|暗红|朱砂"),
    ("自欺收束标记", "很顺|不那么顺|顺口"),
    ("通感嫌疑", "像被.{0,6}(浇|摩挲|按|舔)|声音.{0,4}(发烫|发凉)|字.{0,4}像哭"),
]

# 两套口径并存，正文长度以「含标点」为准（PROJECT.md：每章约 2500 字含标点，浮动 ±10%）。
# HANDOFF 第五节沿用的「汉字 1900-2100」换算过来只有 2150-2400 含标点，中位数比 2500 低近一成，
# 是历史遗留的偏紧口径，仅作参考打印，不判失败。两者口径之争见 continuity-log 2026-08-16。
FULL_LO, FULL_HI = 2250, 2750   # 含标点，权威
HAN_LO, HAN_HI = 1900, 2100     # 汉字，参考


def main(path):
    text = io.open(path, encoding="utf-8").read()
    body = "\n".join(l for l in text.split("\n") if not l.startswith("#"))
    han = len(re.findall(r"[一-鿿]", body))
    full = len(re.sub(r"\s", "", body))

    fail = 0
    print("文件 %s" % path)
    status = "OK" if FULL_LO <= full <= FULL_HI else ("偏短" if full < FULL_LO else "偏长")
    if not FULL_LO <= full <= FULL_HI:
        fail += 1
    print("  含标点 %d  区间 %d-%d  %s   [参考] 汉字 %d（旧口径 %d-%d）"
          % (full, FULL_LO, FULL_HI, status, han, HAN_LO, HAN_HI))

    for name, pat, limit, note in RULES:
        hits = re.findall(pat, body)
        if len(hits) > limit:
            fail += 1
            print("  [失败] %s %d 处 %s -- %s" % (name, len(hits), sorted(set(hits)), note))
        else:
            print("  [通过] %s" % name)

    print("  --- 以下需人工核对，不计失败 ---")
    for name, pat in SOFT:
        hits = re.findall(pat, body)
        if hits:
            print("  [核对] %s %d 处 %s" % (name, len(hits), sorted(set(hits))))

    print("结果：%s" % ("有 %d 项未过" % fail if fail else "机械项全清"))
    return 1 if fail else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python tools/lint.py <正文路径>")
        sys.exit(2)
    sys.exit(max(main(p) for p in sys.argv[1:]))
