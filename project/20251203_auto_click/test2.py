import time
import random
import string
import pyautogui
import keyboard

# 每个随机英文单词的长度
WORD_LEN = 8

# 循环次数
LOOP_COUNT = 40

# 第一次延迟 5 秒，让你移动鼠标到目标区域
time.sleep(5)

for i in range(LOOP_COUNT):

    # 鼠标左键单击
    pyautogui.click()
    time.sleep(0.5)

    # 从第二次开始，先删除上一次的随机英文字符串
    if i > 0:
        for _ in range(WORD_LEN):
            keyboard.press_and_release('backspace')
            time.sleep(0.02)  # 给一点点延迟避免系统吞键

    # 生成随机英文字符串
    rand_word = ''.join(random.choice(string.ascii_letters) for _ in range(WORD_LEN))

    # 输入英文词
    pyautogui.typewrite(rand_word)

    # 按下真实 Enter
    keyboard.press_and_release('enter')

    # 等待 6 秒
    time.sleep(6)

    print(f"完成第 {i+1} 次：{rand_word}")  # 可选，用于调试
