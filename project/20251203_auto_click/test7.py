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
import pyperclip


# 每个随机英文单词的长度
WORD_LEN = 8
# 搜索次数
search_count = 4
# 每个步骤暂停时间
normal_time = 0.5
# 每次app搜索停留时间
search_delay_time = 6
# mumu模拟器启动时间
mumu_start_time = 10
# 每个bing app启动时间
bing_start_time = 2.5
# 账号设备数量
device_num = 3
# 账号设备id
run_device_id = []
# 允许保存的最大log文件个数
MAX_LOG_FILES = 100
# 谷歌浏览器地址
chrome_path = ""  # 字符串类型
# 谷歌浏览器profile
chrome_user_data_dir = ""  # 字符串类型
# 要邮件发送的错误信息
send_fail_msg = ""
# 检测积分的时间
check_hour = 9


# -----------------------------
# 获取当前文件目录
# -----------------------------
def get_current_directory():
    if getattr(sys, "frozen", False):  # 如果是打包的exe文件
        return os.path.dirname(sys.executable)  # 获取exe所在目录
    else:
        return os.path.dirname(os.path.abspath(__file__))  # 获取脚本所在目录


# -----------------------------
# 读json文件
# -----------------------------
def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------
# 执行app内在bing搜索的操作
# -----------------------------
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


# -----------------------------
# 将焦点聚焦到mumu模拟器
# -----------------------------
def force_foreground_safe(hwnd):
    global send_fail_msg
    """
    尽量安全地将窗口拉到前台并获取焦点
    任何一步失败都不会导致进程崩溃
    """

    if not hwnd or not win32gui.IsWindow(hwnd):
        print("force_foreground: 非法窗口句柄，跳过")
        send_fail_msg += "force_foreground: 非法窗口句柄\n"
        send_qq_email(send_fail_msg)
        return False

    try:
        # 如果窗口最小化，先恢复
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(normal_time)
        except Exception as e:
            print(f"ShowWindow 失败: {e}")
            send_fail_msg += "ShowWindow 失败\n"

        # 尝试激活窗口（不强求）
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(normal_time)
        except Exception as e:
            print(f"SetForegroundWindow 失败（忽略）: {e}")
            send_fail_msg += "SetForegroundWindow 失败\n"

        # 尝试获取窗口位置
        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        except Exception as e:
            print(f"GetWindowRect 失败: {e}")
            send_fail_msg += "GetWindowRect 失败\n"
            send_qq_email(send_fail_msg)
            return False

        # 坐标合法性校验
        if right <= left or bottom <= top:
            print("窗口坐标异常，跳过点击")
            send_fail_msg += "窗口坐标异常\n"
            send_qq_email(send_fail_msg)
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
            send_fail_msg += "pyautogui.click 失败\n"

        return True

    except Exception as e:
        # 理论上不应走到这里，但兜底
        print(f"force_foreground_safe 发生异常: {e}")
        return False


# -----------------------------
# 判断app是否正在运行
# -----------------------------
def is_app_running(exe_path):
    for proc in psutil.process_iter(["exe"]):
        try:
            if proc.info["exe"] and proc.info["exe"].lower() == exe_path.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


# -----------------------------
# 发送邮件
# -----------------------------
def send_qq_email(extra_text=""):
    smtp_server = "smtp.qq.com"
    smtp_port = 465
    sender = "283040422@qq.com"
    password = "yrpslodztrbfcbeb"

    # 邮件正文（多行）
    body = f"""领取bing积分失败，请打开 rustdesk 查看

---------- 详细信息 ----------
{extra_text}
--------------------------------
"""

    # msg = MIMEText("mumu未正常关闭，请打开rustdesk查看", "plain", "utf-8")
    msg = MIMEText(body, "plain", "utf-8")
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


# 查找Chrome窗口并置顶
def focus_chrome_window():
    def enum_windows(hwnd, lParam):
        title = win32gui.GetWindowText(hwnd)
        if "Google Chrome" in title:
            # 置顶窗口
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)

    win32gui.EnumWindows(enum_windows, None)


# -----------------------------
# 再次打开谷歌浏览器检查积分
# -----------------------------
def check_score(profile="Profile 3"):
    url = "https://rewards.bing.com/pointsbreakdown"
    # 启动Chrome（非阻塞）
    chrome_process = subprocess.Popen(
        [
            chrome_path,
            f"--user-data-dir={chrome_user_data_dir}",
            f"--profile-directory={profile}",
            url,
        ]
    )

    focus_chrome_window()
    print("Chrome已打开并聚焦，Python脚本继续执行…")

    # 给浏览器一点时间启动
    time.sleep(mumu_start_time)
    keyboard.press_and_release("ctrl+shift+j")
    time.sleep(normal_time)

    allow_pasting = "allow pasting"
    pyautogui.typewrite(allow_pasting)
    time.sleep(normal_time)
    pyautogui.press("enter")
    time.sleep(normal_time)

    js_code = """
    const points = Array.from(document.querySelectorAll('p.pointsDetail')).map(el => {
        return {
            current: el.querySelector('b').innerText,
            total: el.innerText.split('/')[1].trim()
        };
    });console.log(points);copy(JSON.stringify(points, null, 2));
    """

    # 将代码逐字符输入到控制台
    pyautogui.typewrite(js_code, interval=normal_time / 100)  # 0.01秒间隔

    pyautogui.press("enter")
    time.sleep(normal_time)
    # 获取剪贴板内容
    data = pyperclip.paste()

    # 尝试解析为 JSON
    try:
        json_obj = json.loads(data)
    except json.JSONDecodeError:
        print("剪贴板内容不是合法 JSON， 可能是打开网页失败,剪贴板内容为：")
        print(data)
        global send_fail_msg
        send_fail_msg += "剪贴板内容不是合法 JSON， 可能是打开网页失败,剪贴板内容为：\n"
        send_fail_msg += data + "\n"
        send_qq_email(send_fail_msg)
        sys.exit(1)

    for item in json_obj:
        print(item)

    # 暂时不写入json文件中
    # # 文件路径，例如写到脚本同目录
    # desktop = get_current_directory()
    # safe_profile = profile.replace(" ", "_")
    # file_path = os.path.join(desktop, f"clipboard_{safe_profile}.json")

    # # 如果文件存在，先删除
    # if os.path.exists(file_path):
    #     os.remove(file_path)

    # # 写入 JSON 文件，带缩进
    # with open(file_path, "w", encoding="utf-8") as f:
    #     json.dump(json_obj, f, ensure_ascii=False, indent=4)

    # print(f"剪贴板内容已保存到 {file_path}")

    # # 读取并遍历 JSON 对象
    # data_loaded = read_json(file_path)
    # for item in data_loaded:
    #     print(item)

    # tem_msg = "\nnow profile :"
    # tem_msg += profile
    # tem_msg += "\n"

    tem_msg = ""

    for index in range(len(json_obj)):
        item = json_obj[index]  # 获取当前字典
        current = int(item["current"])
        total = int(item["total"])
        # print("第{}条数据 -> current: {}, total: {}".format(index+1, current, total))

        if index == 0:
            if current < total:
                print(f"[desktop] Not enough scores were obtained {current}/{total}")
                tem_msg += f"[desktop] {current}/{total}\n"
            else:
                print(f"[desktop] Enough scores were obtained {current}/{total}")

        if index == 1:
            if current < total:
                print(f"[mobile] Not enough scores were obtained {current}/{total}")
                tem_msg += f"[mobile] {current}/{total}\n"
            else:
                print(f"[mobile] Enough scores were obtained {current}/{total}")

    chrome_process.terminate()
    time.sleep(search_delay_time)

    # 获取当前时间
    now = datetime.now()
    # 获取小时
    hour = now.hour
    print(f"now hour: {hour}")
    # global send_fail_msg

    # 当tem_msg存在信息并且大于某个时间时，才会传入信息
    if tem_msg and hour >= 9:
        send_fail_msg += f"now profile ------------------------> {profile}\n"
        send_fail_msg += tem_msg


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
    chrome_path = user_config["chrome_path"]
    chrome_user_data_dir = user_config["chrome_user_data_dir"]
    chrome_profile = user_config.get("chrome_profile", [])
    check_hour = int(user_config["check_hour"])

    # print(chrome_profile)
    # # 如果想逐个打印
    # for profile in chrome_profile:
    #     print(profile)

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
        # send_qq_email(True)

    # 二次打开谷歌浏览器查看积分
    for profile_u in chrome_profile:
        print(profile_u)
        check_score(profile=profile_u)

    # 若存在错误信息则发送邮件
    if send_fail_msg:
        send_qq_email(send_fail_msg)

    # 将打印重新定向
    sys.stdout = original_stdout
    log_file.close()
