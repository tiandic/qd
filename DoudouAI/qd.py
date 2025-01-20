'''
encode: utf-8
Date: 2024-08-16 11:28:35
LastEditTime: 2025-01-18 13:02:00
FilePath: /qd/DoudouAI/qd.py
'''
import os
import pyautogui
import threading
from ..tool import tool

start_path =os.path.join(tool.start_path,"DoudouAI")
images_path=os.path.join(start_path,"images")

def show_taskbar_thread():
    tool.logger.debug("start show_taskbar")
    # 按下win键

    # 创建一个键盘控制器
    # keyboard = Controller()

    # 模拟按下 Win 键
    pyautogui.press('win')
    # keyboard.press(Key.cmd)  # Key.cmd 表示 Win 键
    # time.sleep(0.1)  # 持续按下时间，模拟短暂按下
    # keyboard.release(Key.cmd)  # 释放 Win 键

    # 因为有可能按下win键有可能没有呼出任务栏

    # 获取屏幕的分辨率
    screen_width, screen_height = pyautogui.size()
    # # 将鼠标移动到屏幕最右边（即屏幕的最右端，y坐标保持不变）
    pyautogui.moveTo(screen_width - 1, screen_height // 2)

    tool.logger.debug("end show_taskbar")

def show_taskbar(time_out=3):
    # stop_event = threading.Event()
    thread=threading.Thread(target=show_taskbar_thread)
    thread.start()
    tool.logger.debug("run join()")
    thread.join(timeout=time_out)
    if thread.is_alive():
        tool.logger.debug("Thread exceeded timeout!")
    # return thread,stop_event

def get_image_path(image_name):
    """
    获取图片的完整路径
    :param image_name: 图片文件名
    :return: 图片的完整路径
    """
    global images_path
    return os.path.join(images_path, image_name)

def open_DoudouAI():
    t = threading.Thread(target=os.startfile, args=("C:\\software\\doudou\\doudou\\DoudouAI.exe",))
    t.start()

def main(zoom=False):
    event=threading.Event()
    tool.logger.info("start DoudouAI qd...")
    # os.system("C:\\software\\doudou\\doudou\\DoudouAI.exe")
    open_DoudouAI()
    # 只有在任务栏能找到进入的方法
    # event.wait(10)
    show_taskbar()

    event.wait(3)
    # 右键点击,找到"任务"按钮进入
    tool.click_image2(get_image_path("taskbar_ico.png"),button="right")
    tool.click_image2(get_image_path("task_button.png"))
    # 不知道前面,是否能够正确获取,所以在这里获取
    event.wait(3)

    if zoom and tool.get_Android_resize_ratio("逗逗游戏伙伴")!=1:
        tool.logger.info("processing images...")
        images_path=tool.resize_images_in_directory(images_path)
        tool.logger.info("processed images!")
    # 点击签到
    tool.click_image2(get_image_path("get.png"))
     
    # 退出程序
    # 没办法直接点退出(截不到图)
    # 所以采用任务栏右键退出的方式退出
    event.wait(3)
    show_taskbar()
    event.wait(3)
     
    # 右键点击,找到"退出"按钮进入
    tool.click_image2(get_image_path("taskbar_ico.png"),button="right")
     
    tool.click_image2(get_image_path("exit2.png"))
    
if __name__ == '__main__':
    main()