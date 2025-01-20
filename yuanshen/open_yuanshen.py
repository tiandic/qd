'''
encode: utf-8
Date: 2024-08-16 09:45:36
LastEditTime: 2025-01-20 14:37:15
FilePath: /qd/yuanshen/open_yuanshen.py
'''
import os
import random
import threading
import pyautogui
from ..tool import tool

yuanshen_config_data=tool.config_data["yuanshen"]
start_path=tool.start_path
yuanshen_start_path=os.path.join(start_path,"yuanshen")
images_path=os.path.join(yuanshen_start_path,"images")
exe_path=yuanshen_config_data["exe_path"]

def get_image_path(image_name):
    """
    获取图片的完整路径
    :param image_name: 图片文件名
    :return: 图片的完整路径
    """
    global images_path
    return os.path.join(images_path, image_name)

def login(UserName,Password):
    event=threading.Event()
    try:
        tool.click_image(get_image_path("UserName.png"))
        event.wait(1)
        pyautogui.typewrite(UserName)
    except Exception:
        tool.logger_click_image.debug("Failed to click the username input box using click_image",exc_info=True)
    event.wait(1)
    try:
        tool.click_image(get_image_path("password.png"))
        event.wait(1)
        pyautogui.typewrite(Password)
    except Exception:
        tool.logger_click_image.debug("Failed to click the password entry box using click_image",exc_info=True)
    event.wait(3)
    try:
        tool.click_image(get_image_path("tongyi.png"))
    except Exception:
        tool.logger_click_image.debug("Failure to agree to the 《User Agreement》 and 《Privacy Policy》 using click_image",exc_info=True)
    event.wait(1)
    try:
        tool.click_image(get_image_path("Login.png"))
    except Exception:
        tool.logger_click_image.debug("Failed to click the login button using click_image",exc_info=True)
    event.wait(2)


def read_login_info():
    global yuanshen_config_data
    
    UserName=yuanshen_config_data["user_name"]
    Password=yuanshen_config_data["password"]

    return UserName,Password

def click_image2_y(image_path,r=False):
    """
    点击屏幕上指定图片的位置
    :param image_path: 图片路径
    """
    event=threading.Event()
    while True:
        try:
            ran_x = random.randint(-5, 5) - (50 if r else 0)
            ran_y = random.randint(-5, 5) + (50 if r else 0)
            button_positions = tool.find_image_on_screen(image_path)
            pyautogui.click(button_positions[0]+ran_x, button_positions[1]+ran_y)
            return [True, button_positions]
        except Exception:
            if not os.path.isfile(image_path):            
                # print("图片路径正确")
                tool.logger.error("图片路径错误 in click_image2_y except")
                tool.logger.error(image_path)
            else:
                if "Enter_yuanshen" in image_path:
                    # 尝试点击同意隐私协议
                    try:
                        tool.click_image(get_image_path("ys_tongyi.png"))
                    except Exception:
                        tool.logger_click_image.debug("Failure to agree to the 《User Agreement》 and 《Privacy Policy》 using click_image",exc_info=True)
                    # 登录
                    info=read_login_info()
                    login(info[0],info[1])
                event.wait(1)
            tool.logger_click_image.debug("Failed to click \"Enter game\" using click_image",exc_info=True)
        event.wait(1)  


def main(zoom=False):
    '''
    zoom=False                    # 是否启用支持缩放
    '''
    global exe_path
    event=threading.Event()

    tool.logger.info("start Genshin Impact!")
    t = threading.Thread(target=os.startfile, args=(exe_path,))
    t.start()
    event.wait(1)
     
    tool.click_image2(get_image_path("kaishiyxi.png"))
    event.wait(20)
     
    # 如果原神进行了缩放
    # 因为启动器的大小固定的,所以在这里才调用
    if zoom and tool.get_Android_resize_ratio("原神")!=1:
        tool.logger.info("processing images...")
        images_path=tool.resize_images_in_directory(images_path)
        tool.logger.info("processed images!")

     
    click_image2_y(get_image_path("Enter_yuanshen.png"))

if __name__ == '__main__':
    main()