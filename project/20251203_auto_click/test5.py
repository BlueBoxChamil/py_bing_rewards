"""
Author: BlueboxChamil
Date: 2025-12-03 14:37:37
LastEditTime: 2025-12-04 10:07:46
FilePath: \test1.py
Description:
Copyright (c) 2025 by BlueboxChamil, All Rights Reserved.
"""

import time
import random
import string
import pyautogui
import keyboard
import subprocess
import win32gui
import win32con
import json
import sys
import os


# 每个随机英文单词的长度
WORD_LEN = 8

# 循环次数
LOOP_COUNT = 3

def get_current_directory():
    if getattr(sys, "frozen", False):  # 如果是打包的exe文件
        return os.path.dirname(sys.executable)  # 获取exe所在目录
    else:
        return os.path.dirname(os.path.abspath(__file__))  # 获取脚本所在目录

def click_bing():
    # 进入bing app
    keyboard.press_and_release("tab")
    time.sleep(0.5)
    keyboard.press_and_release("enter")
    # 要等待一会用于启动app，时长长一点
    time.sleep(2.5)

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

        # 从第二次开始，先删除上一次的随机英文字符串
        if i > 0:
            # 聚焦到输入栏
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
        # type_real(rand_word)

        # 按下真实 Enter
        keyboard.press_and_release("enter")

        # 等待 6 秒
        time.sleep(6)

        print(f"完成第 {i + 1} 次：{rand_word}")  # 可选，用于调试

    # 切换到主屏幕
    keyboard.press_and_release("ctrl+1")
    time.sleep(0.5)


def force_foreground(hwnd):
    # 置顶窗口
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        0,
        0,
        0,
        0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
    )
    time.sleep(0.2)

    # 取消置顶（避免一直置顶）
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_NOTOPMOST,
        0,
        0,
        0,
        0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
    )
    time.sleep(0.2)

    # 激活窗口
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.2)

    # 模拟点击标题栏，确保获得输入焦点
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    title_x = left + 100
    title_y = top + 10
    pyautogui.click(title_x, title_y)


########################################## main




subprocess.Popen([r"D:\software\MuMu\nx_main\MuMuNxMain.exe", "-v", "0"])
# 10S用于加载mumu模拟器软件
time.sleep(10)

print("open moblie")

# 将mumu模拟器窗口设置为最前
hwnd = win32gui.FindWindow(None, "MuMu安卓设备")
if hwnd:
    print("找到窗口")
    force_foreground(hwnd)

    # 点击真实屏幕区域
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    center_x = (left + right) // 2
    center_y = (top + bottom) // 2

    pyautogui.click(center_x, center_y)
    time.sleep(0.5)

keyboard.press_and_release("tab")
time.sleep(0.5)
keyboard.press_and_release("tab")
time.sleep(0.5)
# click_bing()

# 开始不断的打开app来搜索
for i in range(3):
    click_bing()


# 关闭mumu模拟器
keyboard.press_and_release("alt+space")
time.sleep(0.5)
keyboard.press_and_release("alt+f4")
time.sleep(0.5)
