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
import psutil
import smtplib
import ssl
from email.mime.text import MIMEText
from datetime import datetime


# 每个随机英文单词的长度
WORD_LEN = 8

search_count = 4

normal_time = 0.5

search_delay_time = 6

mumu_start_time = 10

bing_start_time = 2.5

device_num = 3

run_device_id = []

MAX_LOG_FILES = 5


def get_current_directory():
    if getattr(sys, "frozen", False):  # 如果是打包的exe文件
        return os.path.dirname(sys.executable)  # 获取exe所在目录
    else:
        return os.path.dirname(os.path.abspath(__file__))  # 获取脚本所在目录


def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


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
        time.sleep(normal_time)
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
    time.sleep(normal_time)

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
    time.sleep(normal_time)

    # 激活窗口
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(normal_time)

    # 模拟点击标题栏，确保获得输入焦点
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    title_x = left + 100
    title_y = top + 10
    pyautogui.click(title_x, title_y)
    time.sleep(normal_time)

def force_foreground_safe(hwnd):
    """
    尽量安全地将窗口拉到前台并获取焦点
    任何一步失败都不会导致进程崩溃
    """

    if not hwnd or not win32gui.IsWindow(hwnd):
        print("force_foreground: 非法窗口句柄，跳过")
        return False

    try:
        # 如果窗口最小化，先恢复
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(normal_time)
        except Exception as e:
            print(f"ShowWindow 失败: {e}")

        # 尝试激活窗口（不强求）
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(normal_time)
        except Exception as e:
            print(f"SetForegroundWindow 失败（忽略）: {e}")

        # 尝试获取窗口位置
        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        except Exception as e:
            print(f"GetWindowRect 失败: {e}")
            return False

        # 坐标合法性校验
        if right <= left or bottom <= top:
            print("窗口坐标异常，跳过点击")
            return False

        # 安全计算点击点（窗口内部，避免边缘）
        click_x = left + min(100, (right - left) // 2)
        click_y = top + min(40, (bottom - top) // 2)

        # 尝试模拟点击（失败不致命）
        try:
            pyautogui.click(click_x, click_y)
            time.sleep(normal_time)
        except Exception as e:
            print(f"pyautogui.click 失败（忽略）: {e}")

        return True

    except Exception as e:
        # 理论上不应走到这里，但兜底
        print(f"force_foreground_safe 发生异常: {e}")
        return False


def is_app_running(exe_path):
    for proc in psutil.process_iter(["exe"]):
        try:
            if proc.info["exe"] and proc.info["exe"].lower() == exe_path.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def send_qq_email(send_trigger):
    if not send_trigger:
        return

    smtp_server = "smtp.qq.com"
    smtp_port = 465
    sender = "283040422@qq.com"
    password = "yrpslodztrbfcbeb"

    msg = MIMEText("mumu未正常关闭，请打开rustdesk查看", "plain", "utf-8")
    msg["Subject"] = "领取bing失败提醒"
    msg["From"] = sender
    msg["To"] = sender

    context = ssl._create_unverified_context()

    server = None
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
        server.login(sender, password)
        server.sendmail(sender, [sender], msg.as_string())
        print("邮件已成功送达服务器！")
    except Exception as e:
        # 如果是发送后的收尾报错，我们选择原谅它
        print(f"发送过程中出现微小异常（通常不影响结果）: {e}")
    finally:
        # 优雅地尝试关闭，如果失败也不报错
        if server:
            try:
                server.close()  # 使用 close 代替 quit，更强制也更安全
            except:  # noqa: E722
                pass


# -----------------------------
# 管理日志文件
# -----------------------------
def cleanup_old_logs(log_dir, max_files=10):
    files = [
        os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith(".txt")
    ]

    if len(files) <= max_files:
        return

    # 按创建时间排序（从旧到新）
    files.sort(key=lambda x: os.path.getctime(x))

    # 删除多余的旧文件
    for f in files[:-max_files]:
        os.remove(f)


# -----------------------------
# 重定向 stdout（print 同时写文件和终端）
# -----------------------------
class TeeStdout:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, message):
        for s in self.streams:
            s.write(message)
            s.flush()

    def flush(self):
        for s in self.streams:
            s.flush()


########################################## main ########################################
if __name__ == "__main__":
    current_dir = get_current_directory()

    log_dir = os.path.join(current_dir, "log")
    # 若 log 目录不存在则创建
    os.makedirs(log_dir, exist_ok=True)
    # 日志文件管理，最多10个
    cleanup_old_logs(log_dir, max_files=(MAX_LOG_FILES - 1))

    # 创建新的日志文件
    timestamp = datetime.now().strftime("%Y%m%d_%H_%M_%S")
    log_file_path = os.path.join(log_dir, f"{timestamp}.txt")
    log_file = open(log_file_path, "w", encoding="utf-8")

    # 保存原始 stdout
    original_stdout = sys.stdout
    # 重定向
    sys.stdout = TeeStdout(sys.stdout, log_file)

    # 获取json数据
    config_path = os.path.join(current_dir, "config.json")
    user_config = read_json(config_path)

    # 打印json数据
    for key, value in user_config.items():
        print(f"{key}: {value}")

    # "mumu_path": "D:\\software\\MuMu\\nx_main\\MuMuNxMain.exe",
    # 使用json数据赋值
    mumu_path = user_config["mumu_path"]
    run_device_id = user_config["run_device_id"]
    device_num = len(run_device_id)
    mumu_start_time = int(user_config["mumu_start_time"])
    bing_start_time = int(user_config["bing_start_time"])
    search_delay_time = int(user_config["search_delay_time"])
    search_count = int(user_config["search_count"])
    normal_time = int(user_config["normal_time"])
    mumu_name = user_config["mumu_name"]
    check_sleep_time = int(user_config["check_sleep_time"])
    check_sleep_count = int(user_config["check_sleep_count"])

    # print(f'mumu_path: {mumu_path}')
    # print(f'run_device_id: {run_device_id}')
    # print(f'device_num: {device_num}')
    # print(f'mumu_start_time: {mumu_start_time}')
    # print(f'bing_start_time: {bing_start_time}')
    # print(f'search_delay_time: {search_delay_time}')
    # print(f'search_count: {search_count}')
    # print(f'normal_time: {normal_time}')
    # print(f'mumu_name: {mumu_name}')

    # ===== 自动计算整个脚本的预计运行时间（仅 sleep 时间） =====

    # 计算 click_bing 单次耗时
    T_bing = (
        bing_start_time
        + 5 * normal_time
        + search_delay_time
        + (search_count - 1) * (6 * normal_time + search_delay_time)
    )

    N = len(run_device_id)  # 执行 bing 的次数
    max_id = run_device_id[-1]  # 最大设备 ID
    skip_count = max_id + 1 - N  # 跳过的次数（只 sleep normal_time）

    # 整个循环耗时
    T_loop = N * T_bing + skip_count * normal_time

    # 总耗时：启动模拟器 + 前置延时 + 循环 + 关闭模拟器
    T_total = mumu_start_time + 7 * normal_time + T_loop

    # 转换为 分钟 + 秒
    minutes = int(T_total // 60)
    seconds = int(T_total % 60)

    print("====== 脚本预计运行时长（仅计算 sleep）======")
    print(f"预计总耗时：{minutes} 分 {seconds} 秒")
    print("================================================")

    # 打开模拟器
    subprocess.Popen([mumu_path, "-v", "0"])
    # 10S用于加载mumu模拟器软件
    time.sleep(mumu_start_time)

    print("open moblie")

    # 将mumu模拟器窗口设置为最前
    hwnd = win32gui.FindWindow(None, mumu_name)
    time.sleep(normal_time)
    if hwnd:
        print("找到窗口")
        # force_foreground(hwnd)
        res_ok = force_foreground_safe(hwnd)
        print(f"force_foreground_safe result = {res_ok}")

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

    results = []

    for i in range(check_sleep_count):
        running = is_app_running(user_config["mumu_path"])
        results.append(running)

        if running:
            print("应用正在运行")
        else:
            print("应用未运行")
        time.sleep(check_sleep_time)

    # 睡眠参数和次数要放在外部json作为可调数据
    if all(results):
        print("！！！！应用仍未关闭！！！！")
        send_qq_email(True)

    sys.stdout = original_stdout
    log_file.close()
