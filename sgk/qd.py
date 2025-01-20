'''
encode: utf-8
Date: 2024-07-31 08:58:24
LastEditTime: 2025-01-20 14:17:30
FilePath: /qd/sgk/qd.py
'''
import os
import sys
import random
import keyboard
import threading
import pyautogui
import pyperclip
from ..tool import tool

# sgk的配置信息
sgk_config_data=tool.config_data["sgk"]
paused   = sgk_config_data["paused"]        # 定义一个变量来表示是否暂停
if_sleep = sgk_config_data["if_sleep"]      # 是否需要等待一下再开始  
start_path =os.path.join(tool.start_path,"sgk")                # sgk目录位置
images_path=os.path.join(start_path,"images")                  # 点击的图片目录位置
sgk_path   =os.path.join(start_path,"she_gong_ku2_new.txt")    # sgk列表文件

now_qd_command=""   # 当前sgk的签到命令

# 获取需要签到的总数
# 初始化避免下面文件打开失败后下面的lines变量没有找到
lines=[]
try:
    with open(sgk_path, encoding='utf-8') as file:
        lines = file.readlines()
except (FileNotFoundError, IOError) as e:
    tool.logger.error(f"文件打开失败: {e}")

# 获取需要签到的总数
total_signins = sum(1 for line in lines if '@' in line)

pending_signins=total_signins  # 定义一个变量来表示还没有签到的数
remaining_time=10*pending_signins

def get_image_path(image_name):
    """
    获取图片的完整路径
    :param image_name: 图片文件名
    :return: 图片的完整路径
    """
    global images_path
    return os.path.join(images_path, image_name)

shangyige_an=get_image_path("search.png")

image_button_path = get_image_path('an.png')
image_button_path2 = get_image_path('an2.png')
image_send_path = get_image_path('send.png')

# 没有找到目标图片位置的次数,如果达到一定次数,则可能上一个图片没有点击到,执行再点一次逻辑
count_error=0

# 进度条(倒计时)
def sleep_and_decrease_time(sleep_time=0):
    global remaining_time
    event = threading.Event()
    event.wait(sleep_time)
    remaining_time -= sleep_time  # 更新剩余时间

def write_message(l,phone=False):
    """
    根据传入的列表内容，执行相应的消息发送或点击操作
    :param l: 包含消息内容的列表
    """
    global remaining_time,image_button_path,image_button_path2,image_send_path,now_qd_command
    # print( l)
    if '/menu' in now_qd_command :
        # 已更改,可以使用/sign命令
        sleep_and_decrease_time(3)
        # 输入"/sign"
        if phone:
            pyperclip.copy("/sign")
            pyautogui.hotkey("ctrl","v")
        else:
            pyautogui.typewrite("/sign")
         
        sleep_and_decrease_time(1)
        # 点击发送,完成签到
        tool.click_image2(image_send_path)

    elif "按钮签到" in now_qd_command:
        # "哈希"特殊一点
        if "哈希" in l[0]:
            # 看看是否有"签到"按钮,有就直接点击
            try:
                tool.click_image(image_button_path2)
                sleep_and_decrease_time(1)
            except Exception:
                # 没有"签到"按钮,使用"/start"让按钮出现
                # 输入"/start"
                tool.logger_click_image.debug("The \"hash\" sign-in button was not found",exc_info=True)
                if phone:
                    pyperclip.copy("/start")
                    pyautogui.hotkey("ctrl","v")
                else:
                    pyautogui.typewrite("/start")
                 
                sleep_and_decrease_time(2)
                # 点击发送
                tool.click_image2(image_send_path)
                sleep_and_decrease_time(5)
                # 点击"签到"按钮
                tool.click_image2(image_button_path2)
        else:
            # 直接点击输入框下方的"签到"按钮
            tool.click_image2(image_button_path)
    else:
        # 直接使用命令签到的类型
        if phone:
            pyperclip.copy(now_qd_command)
            pyautogui.hotkey("ctrl","v")
        else:
            # 输入签到命令
            pyautogui.typewrite(now_qd_command)
         
        sleep_and_decrease_time(1)
        # 点击发送
        tool.click_image2(image_send_path)

def print_progress():
    """
    打印当前进度和剩余时间的函数
    """
    global pending_signins, remaining_time,total_signins,if_sleep
    event=threading.Event()
    if if_sleep:
        event.wait(5)
    print("\b"*14,end="")
    tool.logger.info("start!        Press 'esc' to pause!               ")
    while True:
        # 检测是否剩余时间显示过大
        if pending_signins*10<remaining_time:
            remaining_time=pending_signins*10
        # 如果剩余时间大于60秒,则以XXmin XXs的格式显示
        if remaining_time>60:
            print_time=f"{remaining_time//60}min {remaining_time%60}s"
        else:
            print_time=f"{remaining_time}s"

        # 构建输出字符串
        result_print=f"plan: {total_signins-pending_signins}/{total_signins}, time remaining: {print_time}"
        # 让输出结果为固定长度,用于清理上一次输出
        result_print = result_print.ljust(40)
        # 打印输出并覆盖上次输出,让其看上去为动态的
        print("\r"+result_print,end="")
        tool.logger.debug(f"result_print: {result_print}")
        sys.stdout.flush()
        if pending_signins==0:
            tool.logger.info("\nAll done!")
            sys.exit(0)
        event.wait(1)


def main(num=0,phone=False,zoom=False):
    '''
    num  = 0               # 从第几个开始
    phone= False           # 是否在手机上点击
    zoom = False           # 是否启用缩放支持

    '''
    global paused, pending_signins, remaining_time,shangyige_an,images_path,sgk_path,now_qd_command,sgk_config_data
    # 如果在手机上
    if phone:
        images_path=os.path.join(start_path,"phone_images")           # 点击的图片目录位置
    # 如果模拟器进行了缩放
    if zoom and tool.get_Android_resize_ratio("逍遥")!=1:
        tool.logger.info("processing images...")
        images_path=tool.resize_images_in_directory(images_path)
        tool.logger.info("processed images!")
    # sgk文件的所有行
    sgk_text_lines = open(sgk_path, encoding='utf-8').readlines()
    # 初始化图片路径
    image_search_path = get_image_path('search.png')
    image_bot_path = get_image_path('bot.png')
    image_message_path = get_image_path('message.png')
    image_back_path = get_image_path('back.png')
    if_sleep_search=True    # 等待一会,让第一次搜索结果显示完毕
    frist=True              # 是否为第一次循环
    event=threading.Event()

    # 更新没有签到的数目
    argv = num
    if len(sys.argv) > 1:
        argv=0
        # 避免输入参数错误
        try:
            argv = int(sys.argv[1])
        except Exception:
            tool.logger.debug("Input parameter error",exc_info=True)
    # 更新实际需要签到的数目
    pending_signins -= argv

    # 计算剩余的签到时间(每个未签到的条目假设需要 10 秒)
    remaining_time-=10*argv

    # 添加进度
    threading.Thread(target=print_progress, args=()).start()
    if if_sleep:
        # 等待指定秒数再开始
        start_sleep_second=sgk_config_data["start_sleep_second"]
        while start_sleep_second>0:
            print("\b"*14,end="")
            print(f"sleep {start_sleep_second}s start",end="")
            sys.stdout.flush()
            start_sleep_second-=1
            event.wait(1)
        print("\b"*14,end="")
        sys.stdout.flush()

    # 迭代所有行 
    for i in range(len(sgk_text_lines)):
         
        # 文件的每一行
        line = sgk_text_lines[i]
        # 获取签到命令
        if "%!:-)!%" in line:
            now_qd_command=line.lstrip("%!:-)!%").strip()
        # 判断是否是有效行
        if "@" in line:
            # 跳过参数 argv 指定的已经签到的数目
            if argv>0:
                argv-=1
                continue
            # line_list根据文件格式只有两个元素
            # 第一个元素为备注
            # 第二个元素为搜索内容(sgk的名称)
            line_list = line.split("%:-)%")
            
            # 搜索框消息
            try:
                # 获取需要搜索的内容(sgk名称)
                input_text = line_list[-1]
                # 去除\n
                input_text = input_text.strip()
            except Exception:
                tool.logger.debug("Failed to process the search content",exc_info=True)
                paused = True

             
            
            if if_sleep_search:
                event.wait(5)
                if_sleep_search=False

            # 点击搜索按钮
             
            tool.click_image2(image_search_path)
            shangyige_an=image_search_path
            sleep_and_decrease_time(1)
            
            # 确保程序处于搜索状态
            if frist:
                event.wait(5)

            # 输入搜索内容
             
            if phone:
                pyperclip.copy(input_text)
                pyautogui.hotkey("ctrl","v")
            else:
                pyautogui.typewrite(input_text)
            sleep_and_decrease_time(2)

            # 确保程序搜索完成
            if frist:
                event.wait(5)
                frist=False

            # 点击bot
             
            tool.click_image2(image_bot_path)
            shangyige_an=image_bot_path
            event.wait(1)
            if phone:
                event.wait(2)
            remaining_time-=1
            # 点击消息输入框
             
            if_t=tool.click_image2(image_message_path)
            shangyige_an=image_message_path
            sleep_and_decrease_time(1)
            # 输入签到消息内容并且发送
            # 或者点击签到按钮
             
            if if_t[0]:
                write_message(line_list,phone=phone)
                sleep_and_decrease_time(1)

            # 点击返回
             
            tool.click_image2(image_back_path)
            shangyige_an=image_back_path
            sleep_and_decrease_time(1)
            pending_signins=pending_signins-1

            # 如果点击了无效了的bot,就需要多次点击返回,来返回首页
            if not if_t[0]:
                try:
                    tool.click_image(image_back_path)
                except Exception:
                    tool.logger_click_image.debug("Encounter an invalid robot, click back multiple times, the first time",exc_info=True)
                event.wait(1)
                try:
                    tool.click_image(image_back_path)
                except Exception:
                    tool.logger_click_image.debug("When you encounter an invalid robot, click back multiple times, a second time",exc_info=True)
                event.wait(1)

   

if __name__ == '__main__':
    main()
