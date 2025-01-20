'''
encode: utf-8
Date: 2024-08-07 12:32:23
LastEditTime: 2025-01-20 13:51:14
FilePath: /qd/launcher.py
'''

import os
import sys
import argparse
import threading
import subprocess
from .tool import tool
import pygetwindow as gw
from .sgk import qd as qd_sgk
from .cloud import qd as qd_cloud
from .yuanshen import open_yuanshen
from .miyushe import qd as qd_miyushe
from .DoudouAI import qd as qd_DoudouAI


start_path=tool.start_path
# launcher的配置信息
launcher_config_data=tool.config_data["launcher"]
images_path=os.path.join(start_path,"images")
android_emulator_path=launcher_config_data["android_emulator_path"]
adb_path=launcher_config_data["adb_path"]
Android_device=launcher_config_data["Android_device"]

def get_image_path(image_name):
    """
    获取图片的完整路径
    :param image_name: 图片文件名
    :return: 图片的完整路径
    """
    global images_path
    return os.path.join(images_path, image_name)


def check_connect():
    global adb_path,Android_device
    # 检测是否能通Google
    while True:
        # 构造命令
        command = ["powershell", "-Command", f"&\"{adb_path}\" {Android_device}"]
        command.append("shell curl -I https://www.google.com")

        try:
            # 执行命令
            result = subprocess.run(command, capture_output=True, text=True, check=True)

            # 检查 Google 是否可访问
            if "200" in result.stdout and "OK" in result.stdout:
                tool.logger.info("[+] Google is ready")
                break
            else:
                tool.logger.warning("[-] Google is not ready. Output:")
                tool.logger.warning(result.stdout)
        except Exception as e:
            tool.logger.warning("[-] Command failed, retrying...")
            tool.logger.warning(e)

def if_in_argument(argument):
    for i in sys.argv:
        if argument == str(i):
            return True
    return False
def get_window_position():
    active_window = gw.getActiveWindow()
    if active_window:
        window_position = active_window.topleft
        tool.logger.info(f"前台窗口位置: {window_position}")
        return window_position
    else:
        tool.logger.warning("没有前台窗口")

def get_size():
    active_window = gw.getActiveWindow()
    if active_window:
        window_size = active_window.size
        tool.logger.info(f"前台窗口大小: {window_size}")
        return window_size
    else:
        tool.logger.warning("没有前台窗口")

def can_convert_to_int(value):
    try:
        int(value)  # 尝试转换为 int
        return True
    except ValueError:
        return False

class MyArgumentParser(argparse.ArgumentParser):
    def print_help(self, *args, **kwargs):
        start_order=[
            "telegram",
            "米游社",
            "云原神",
            "逗逗AI",
            "原神启动!"
        ]
        # 输出任务执行顺序
        i=0
        output=""
        for key, value in launcher_config_data["sign_in_features_enabled"].items():
            if value:
                output+=f"{start_order[i]} -> "
            i+=1
        if output.endswith(' -> '):
            output = output[:-4]
        print(f"\033[32m{output}\033[0m")
        super().print_help(*args, **kwargs)  # 继续执行默认的帮助输出
        print("\033[31m注意: 模拟器窗口缩放后\n有的地方需要重复好几次才能正常点击,有时候在sgk时会识别到其他bot(而不是搜索结果第一个)点击\n所以尽可能不要缩放模拟器\n如果在程序执行过程中再次缩放了,请重新运行程序\033[0m")
        print()
        print("\033[36m使用命令时要将'数字参数(qd_sgk_argument)'放在最前面\033[0m")
        print()

def get_target_help_str():
    global launcher_config_data
    # 查看启用了哪些功能
    sign_in_features_enabled = launcher_config_data["sign_in_features_enabled"]
    
    result = ["单独执行其中一个签到任务("]
    example = "示例:-t "
    example_not_written = True

    # 所有的选项
    target_list = [
        ("sgk:s", "s"),
        ("原神:y", "y"),
        ("米游社:m", "m"),
        ("逗逗游戏伙伴:d", "d"),
        ("云原神:c", "c")
    ]
    
    # 拼接启用的功能
    for (full_option, short_option), (key, value) in zip(target_list, sign_in_features_enabled.items()):
        if value:
            result.append(full_option)
            if example_not_written:
                example += short_option
                example_not_written = False
    
    # 所有的选项处理后拼接结果
    if result:
        result_str = ",".join(result) + ") "
    else:
        result_str = ") "
    
    # 可选选项处理
    target_list = [
        "s",
        "y",
        "m",
        "d",
        "c"
    ]

    # 拼接可选项
    for i, (key, value) in enumerate(sign_in_features_enabled.items()):
        if value:
            result_str += target_list[i] + ","
            if example_not_written:
                example += target_list[i]
                example_not_written = False
    
    # 返回拼接好的结果
    return result_str + example


def get_command_line_args():
    global launcher_config_data

    # 查看启用了哪些功能
    sign_in_features_enabled=launcher_config_data["sign_in_features_enabled"]
    # 创建 ArgumentParser 对象
    parser = MyArgumentParser(description="命令行工具的说明")

    # 添加命令行参数
    parser.add_argument('-p','--phone',action='store_true', help='指定在手机上点击(废除,效果差)')
    parser.add_argument('-t', '--target', type=str, default=None, help=get_target_help_str())
    parser.add_argument('-z', '--zoom', action='store_true', help='启用缩放支持')
    # 禁用选项
    if sign_in_features_enabled["mi_you_she"]:
        parser.add_argument('-nu', '--no-update-miyushe', action='store_true', help='不需要更新米游社')
        parser.add_argument('-ns', '--no-miyushe-sleep', action='store_true', help='禁用米游社签到开始时的等待15秒')
    if sign_in_features_enabled["telegram"]:
        parser.add_argument('-nc', '--no-check-connect', action='store_true', help='禁用检测连接')
    # 跳过哪个签到任务
    if sign_in_features_enabled["yuanshen"]:
       parser.add_argument('-sy', '--skit-yuanshen', action='store_true', help='跳过原神启动')
    if sign_in_features_enabled["DouDou"]:
        parser.add_argument('-sd', '--skit-DoudouAI', action='store_true', help='跳过DoudouAI签到')
    if sign_in_features_enabled["telegram"]:
        parser.add_argument('-ss', '--skit-sgk-check-in', action='store_true', help='跳过sgk签到')
    if sign_in_features_enabled["mi_you_she"]:
        parser.add_argument('-smc', '--skit-miyushe-check-in', action='store_true', help='跳过米游社签到')
        parser.add_argument('-sm', '--skit-miyushe-Community-check-in', action='store_true', help='传递给miyushe,跳过社区打卡')
    if sign_in_features_enabled["cloud"]:
        parser.add_argument('-sc', '--skit-cloud-ys', action='store_true', help='跳过云原神打卡')

    # sgk签到到第几个了
    if sign_in_features_enabled["telegram"]:
        parser.add_argument('qd_sgk_argument', type=int, nargs='?', default=0, help='指定数字参数,传递给sgk,从第几个开始(下标)')
    # 解析命令行参数
    args = parser.parse_args()
    return args

def start_Android():
    global android_emulator_path
    t = threading.Thread(target=os.startfile, args=(android_emulator_path,))
    t.start()


def adb(s,if_device=True):
    global adb_path
    if if_device:
        s=f"{Android_device} {s}"
    os.system(f"\"{adb_path}\" {s}")

def initialize_and_start_telegram(qd_sgk_argument=0,zoom=False,is_no_check_connect=True):
    event=threading.Event()
    if not is_no_check_connect:
        # 检测连通性
        check_connect()
    # 启动Temlgram X
    adb(" shell am start -n org.thunderdog.challegram/.MainActivity")
    event.wait(3)
    start_Android()
    qd_sgk.main(qd_sgk_argument,zoom=zoom)
    event.wait(3)
    # 关闭 V2rayNG,proxydroid
    adb("shell am force-stop com.v2ray.ang")
    adb("shell am force-stop org.thunderdog.challegram")
    adb("shell am force-stop org.proxydroid")
    event.wait(2)   

def execute_task(target_task, task_args):
    # 定义任务分发字典
    task_dispatcher = {
        "s": lambda: initialize_and_start_telegram(task_args.qd_sgk_argument,zoom=task_args.zoom,is_no_check_connect=task_args.no_check_connect),
        "y": lambda: open_yuanshen.main(zoom=task_args.zoom),
        "m": lambda: qd_miyushe.main(task_args.skit_miyushe_Community_check_in,task_args.no_update_miyushe,task_args.no_miyushe_sleep,zoom=task_args.zoom),
        "d": lambda: qd_DoudouAI.main(zoom=task_args.zoom),
        "c": lambda: qd_cloud.main()
    }

    # 获取对应任务的处理函数并调用
    task_func = task_dispatcher.get(target_task)
    
    # 如果找到对应任务，则执行任务；否则返回默认提示
    if task_func:
        task_func()
    else:
        tool.logger.error("Invalid task: Please select a valid task.")

def set_related_params_if_enabled(args:argparse.Namespace):
    global launcher_config_data
    # 查看启用了哪些功能
    sign_in_features_enabled=launcher_config_data["sign_in_features_enabled"]
    # 如果跳过了原神
    # 那么肯定也跳过了DouDouAI
    if sign_in_features_enabled["yuanshen"] and  args.skit_yuanshen:
       args.skit_DoudouAI=True 
    
    # 如果跳过了DouDouAI
    # 那么肯定也跳过了米游社签到
    if sign_in_features_enabled["DouDou"] and args.skit_DoudouAI:
       args.skit_miyushe_check_in=True
        
    # 如果跳过了米游社签到
    # 那么肯定也跳过了米游社的社区签到
    if sign_in_features_enabled["mi_you_she"] and args.skit_miyushe_check_in:
       args.skit_miyushe_Community_check_in=True

    #如果跳过了米游社的社区签到
    # 那么肯定也跳过了sgk签到
    if sign_in_features_enabled["mi_you_she"] and args.skit_miyushe_Community_check_in:
        args.skit_sgk_check_in=True
    return args



def main():
    global images_path, adb_path,launcher_config_data
    event=threading.Event()

    # 解析命令行参数
    args=get_command_line_args()
    # 处理参数之间的关系
    args=set_related_params_if_enabled(args)
    tool.logger.info("start launcher...")    

    # 单独执行一个签到任务
    if args.target is not None:
        execute_task(args.target,args)
        sys.exit(0)

    #在手机上
    if args.phone:
        qd_sgk.main(args.qd_sgk_argument,phone=args.phone,zoom=args.zoom)

    # telegram
    if (not args.skit_sgk_check_in) and launcher_config_data["sign_in_features_enabled"]["telegram"]:
        # 启动 telegram
        initialize_and_start_telegram(args.qd_sgk_argument,zoom=args.zoom,is_no_check_connect=args.no_check_connect)
        # 启动米游社
        adb("shell am start -n  com.mihoyo.hyperion/.splash.SplashActivity")
        event.wait(10)
    # 米游社
    if (not args.skit_miyushe_check_in) and launcher_config_data["sign_in_features_enabled"]["mi_you_she"]:
        # 米游社签到
        qd_miyushe.main(args.skit_miyushe_Community_check_in,args.no_update_miyushe,args.no_miyushe_sleep,zoom=args.zoom)
        # 关闭米游社
        adb("shell am force-stop   com.mihoyo.hyperion")
        event.wait(1)
        # 关闭模拟器
        tool.click_image2(get_image_path("x_z.png"))
        event.wait(1)
        tool.click_image2(get_image_path("x_z2.png"))
    # 云原神
    if (not args.skit_cloud_ys) and launcher_config_data["sign_in_features_enabled"]["cloud"]:
        qd_cloud.main()
    # DoudouAI
    if (not args.skit_DoudouAI) and launcher_config_data["sign_in_features_enabled"]["DouDou"]:
        qd_DoudouAI.main(zoom=args.zoom)
    # 启动原神
    if (not args.skit_yuanshen) and launcher_config_data["sign_in_features_enabled"]["yuanshen"]:
        open_yuanshen.main(zoom=args.zoom)
if __name__ == '__main__':
    try:
        main()
    except Exception:
        tool.logger.error("Project run crash!", exc_info=True)
    