"""
Author: BlueboxChamil
Date: 2025-12-03 16:49:11
LastEditTime: 2025-12-04 09:17:34
FilePath: \test3.py
Description:
Copyright (c) 2025 by BlueboxChamil, All Rights Reserved.
"""

import time
import random
import string
import pyautogui
import keyboard
import subprocess

# 每个随机英文单词的长度
WORD_LEN = 8

# 循环次数
LOOP_COUNT = 3


subprocess.Popen([
    r"D:\software\MuMu\nx_main\MuMuNxMain.exe",
    "-v", "0"
])

# 第一次延迟 5 秒，让你移动鼠标到目标区域
time.sleep(15)
print("open moblie")

def click_bing():
    # 进入bing app
    keyboard.press_and_release("tab")
    time.sleep(0.5)
    keyboard.press_and_release("enter")
    time.sleep(0.5)

    # 聚焦到搜索栏
    keyboard.press_and_release("tab")
    time.sleep(0.5)
    keyboard.press_and_release("tab")
    time.sleep(0.5)
    keyboard.press_and_release("enter")
    time.sleep(0.5)

    # 开始输入关键词
    for i in range(LOOP_COUNT):
        if i == 1:
            keyboard.press_and_release("tab")
            time.sleep(0.5)

        # # 从第二次开始，先删除上一次的随机英文字符串
        if i > 0:
            # 改一下，可以通过tab，和enter来进入输入

            # 聚焦到输入栏dejTPYCu

            keyboard.press_and_release("enter")
            time.sleep(0.5)

            # 点击x号删除
            keyboard.press_and_release("tab")
            time.sleep(0.5)
            keyboard.press_and_release("tab")
            time.sleep(0.5)
            keyboard.press_and_release("enter")
            time.sleep(0.5)

            # 再次聚焦到任务栏
            keyboard.press_and_release("tab")
            time.sleep(0.5)

        # 生成随机英文字符串
        rand_word = "".join(
            random.choice(string.ascii_letters) for _ in range(WORD_LEN)
        )

        # 输入英文词
        pyautogui.typewrite(rand_word)

        # 按下真实 Enter
        keyboard.press_and_release("enter")

        # 等待 6 秒
        time.sleep(6)

        print(f"完成第 {i + 1} 次：{rand_word}")  # 可选，用于调试

    # 切换到主屏幕
    keyboard.press_and_release("ctrl+1")
    time.sleep(0.5)


for m in range(1):
    click_bing()


keyboard.press_and_release("alt+space")
time.sleep(0.5)
keyboard.press_and_release("alt+f4")
time.sleep(0.5)