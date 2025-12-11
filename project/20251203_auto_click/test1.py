"""
Author: BlueboxChamil
Date: 2025-12-03 14:37:37
LastEditTime: 2025-12-04 10:07:46
FilePath: \test1.py
Description:
Copyright (c) 2025 by BlueboxChamil, All Rights Reserved.
"""

"""
Author: BlueboxChamil
Date: 2025-12-03 14:37:37
LastEditTime: 2025-12-04 10:05:54
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
import win32api
import ctypes

# 每个随机英文单词的长度
WORD_LEN = 8

# 循环次数
LOOP_COUNT = 3

# # 等待 5 秒按下 Enter
# time.sleep(5)
# keyboard.press_and_release('enter')

# # 再等 1 秒执行鼠标左键单击
# time.sleep(1)
# pyautogui.click()   # 左键单击

# time.sleep(5)
# os.startfile(r"D:\software\MuMu\nx_main\MuMuNxMain.exe -v 0")


def type_real(text):
    for ch in text:
        # keyboard.press_and_release(ch)
        keyboard.send(ch)
        time.sleep(0.8)  # 给一点间隔，模拟真实速度


def click_bing():
    # 进入bing app
    keyboard.press_and_release("tab")
    time.sleep(0.5)
    keyboard.press_and_release("enter")
    # 要等待一会用于启动app
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

        # # 从第二次开始，先删除上一次的随机英文字符串
        if i > 0:
            # 改一下，可以通过tab，和enter来进入输入

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


# Win32 API 常量
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

# 获取屏幕尺寸
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)


def move_and_left_click(x, y):
    """
    移动鼠标到指定坐标 (x, y) 并左键点击
    x, y : 屏幕坐标，左上角为(0,0)
    """
    # 转换为绝对坐标 0~65535
    abs_x = int(x * 65535 / (screen_width - 1))
    abs_y = int(y * 65535 / (screen_height - 1))

    # 移动鼠标
    ctypes.windll.user32.mouse_event(
        MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, abs_x, abs_y, 0, 0
    )
    time.sleep(0.01)  # 稍微延迟，模拟真实移动

    # 点击
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.01)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


# main
subprocess.Popen([r"D:\software\MuMu\nx_main\MuMuNxMain.exe", "-v", "0"])
time.sleep(10)

# time.sleep(5)
print("open moblie")

hwnd = win32gui.FindWindow(None, "MuMu安卓设备")

if hwnd:
    print("找到窗口")
    force_foreground(hwnd)

    # 点击真实屏幕区域
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    center_x = (left + right) // 2
    center_y = (top + bottom) // 2

    pyautogui.click(center_x, center_y)
    # move_and_left_click(center_x, center_y)
    time.sleep(0.5)

time.sleep(5)


keyboard.press_and_release("tab")
time.sleep(0.5)
keyboard.press_and_release("tab")
time.sleep(0.5)
click_bing()
keyboard.press_and_release("alt+space")

time.sleep(0.5)
keyboard.press_and_release("alt+f4")
time.sleep(0.5)
