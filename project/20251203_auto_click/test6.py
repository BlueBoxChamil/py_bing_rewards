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

search_count = 4

normal_time = 0.5

search_delay_time = 6

mumu_start_time = 10

bing_start_time = 2.5

device_num = 3

run_device_id = []


def get_current_directory():
    if getattr(sys, "frozen", False):  # 如果是打包的exe文件
        return os.path.dirname(sys.executable)  # 获取exe所在目录
    else:
        return os.path.dirname(os.path.abspath(__file__))  # 获取脚本所在目录


def click_bing():
    # 进入bing app
    keyboard.press_and_release("tab")
    time.sleep(normal_time)
    keyboard.press_and_release("enter")
    # 要等待一会用于启动app，时长长一点
    time.sleep(bing_start_time)

    # 聚焦到搜索栏
    keyboard.press_and_release("tab")
    time.sleep(normal_time)
    keyboard.press_and_release("tab")
    time.sleep(normal_time)
    keyboard.press_and_release("enter")
    time.sleep(normal_time)

    # 开始输入关键词
    for i in range(search_count):
        if i == 1:
            keyboard.press_and_release("tab")
            time.sleep(normal_time)

        # 从第二次开始，先删除上一次的随机英文字符串
        if i > 0:
            # 聚焦到输入栏
            keyboard.press_and_release("enter")
            time.sleep(normal_time)

            # 点击x号删除
            keyboard.press_and_release("tab")
            time.sleep(normal_time)
            keyboard.press_and_release("tab")
            time.sleep(normal_time)
            keyboard.press_and_release("enter")
            time.sleep(normal_time)

            # 再次聚焦到任务栏
            keyboard.press_and_release("tab")
            time.sleep(normal_time)

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
        time.sleep(search_delay_time)

        print(f"完成第 {i + 1} 次：{rand_word}")  # 可选，用于调试

    # 切换到主屏幕
    keyboard.press_and_release("ctrl+1")
    time.sleep(normal_time)


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
current_dir = get_current_directory()
config_path = os.path.join(current_dir, "config.json")
with open(config_path, "r", encoding="utf-8") as f:
    user_config = json.load(f)

print(f"user_config: {user_config['search_bing']['mumu_start_time']}")
print(f"user_config: {user_config['search_bing']['bing_start_time']}")
print(f"user_config: {user_config['search_bing']['search_delay_time']}")
print(f"user_config: {user_config['search_bing']['mumu_path']}")


mumu_path = user_config["search_bing"]["mumu_path"]
device_num = len(run_device_id)
mumu_start_time = int(user_config["search_bing"]["mumu_start_time"])
bing_start_time = int(user_config["search_bing"]["bing_start_time"])
search_delay_time = int(user_config["search_bing"]["search_delay_time"])
search_count = int(user_config["search_bing"]["search_count"])
run_device_id = user_config["search_bing"]["run_device_id"]
mumu_name = user_config["search_bing"]["mumu_name"]


# 打开模拟器
subprocess.Popen([mumu_path, "-v", "0"])
# 10S用于加载mumu模拟器软件
time.sleep(mumu_start_time)

print("open moblie")

# 将mumu模拟器窗口设置为最前
hwnd = win32gui.FindWindow(None, mumu_name)
if hwnd:
    print("找到窗口")
    force_foreground(hwnd)

    # 点击真实屏幕区域
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    center_x = (left + right) // 2
    center_y = (top + bottom) // 2

    pyautogui.click(center_x, center_y)
    time.sleep(normal_time)

# 开始搜索数组id，id存在则搜索，否则跳过
for i in range(0, run_device_id[-1] + 1):
    if i in run_device_id:
        print(f"id = {i}:yes")
        click_bing()
    else:
        print(f"id = {i}:no")
        keyboard.press_and_release("tab")
        time.sleep(normal_time)


# 关闭mumu模拟器
keyboard.press_and_release("alt+space")
time.sleep(normal_time)
keyboard.press_and_release("alt+f4")
time.sleep(normal_time)
