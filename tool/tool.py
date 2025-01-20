'''
encode: utf-8
Date: 2024-08-16 09:57:37
LastEditTime: 2025-01-20 19:52:52
FilePath: /qd/tool/tool.py
'''
import os
import cv2
import yaml
import random
import logging
import tempfile
import pyautogui
import threading
import numpy as np
import logging.config
import pygetwindow as gw
from PIL import Image
from typing import Union
from PIL import ImageGrab

# 匹配方法
cv2_TM_SQDIFF       =cv2.TM_SQDIFF
cv2_TM_SQDIFF_NORMED=cv2.TM_SQDIFF_NORMED
cv2_TM_CCORR        =cv2.TM_CCORR
cv2_TM_CCORR_NORMED =cv2.TM_CCORR_NORMED
cv2_TM_CCOEFF       =cv2.TM_CCOEFF
cv2_TM_CCOEFF_NORMED=cv2.TM_CCOEFF_NORMED

# 匹配色彩
cv2_COLOR_RGB2BGR   =cv2.COLOR_RGB2BGR
cv2_COLOR_BGR2GRAY  =cv2.COLOR_BGR2GRAY

config_data: Union[dict, list, str, int, float, bool, None]
current_script_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_script_path)
# 项目目录
start_path=os.path.dirname(current_dir)
lastClickedImage=""        # 上一张点击的图片
global_scale_factor=1      # 缩放比例 now/old
paused=False               # 是否需要暂停

# 加载日志配置文件
log_config_path=os.path.join(start_path,'log_config.yaml')
with open(log_config_path, 'r',encoding='utf-8') as f:
    log_config = yaml.safe_load(f)
    logging.config.dictConfig(log_config)
# 创建一个日志记录器
logger = logging.getLogger('qd_main')
logger_click_image=logging.getLogger('click_image')

def scale_image(image_path, output_path, scale_factor):
    # 这个是使用magick命令进行的缩放
    os.system(f"magick {image_path} -resize {scale_factor*100}% {output_path}")

def scale_image2(image_path, output_path, scale_factor):
    # 打开原始图像
    img = Image.open(image_path)
    
    # 获取原始图像的宽度和高度
    width, height = img.size
    
    # 计算新的尺寸，保持等比例
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    
    # 缩放图像，使用新的高质量缩放滤镜
    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # 保存缩放后的图像
    resized_img.save(output_path)

def get_Android_resize_ratio(target_title):
    now_Android_size_list = get_exe_size(target_title)
    Android_size_path = os.path.join(start_path, f"Android_{target_title}_size.txt")

    # 判断之前是否有保存大小
    if os.path.isfile(Android_size_path):
        out_ratio = 1
        # 如果有,并且变化过大,就计算比值
        with open(Android_size_path, encoding="utf-8") as f:
            # 保存的文件格式是 "width,height" 
            read = f.readlines()

        prev_width, prev_height = map(int, read[0].split(','))
        if abs(now_Android_size_list[0] - prev_width) > 30 or abs(now_Android_size_list[1] - prev_height) > 30:
            out_ratio = round((now_Android_size_list[0] / prev_width + now_Android_size_list[1] / prev_height) / 2, 4)
            # 返回计算出来的缩放比例
        return out_ratio
    else:
        # 如果没有就保存一下,返回默认的1
        with open(Android_size_path, "a", encoding="utf-8") as f:
            f.write(f"{now_Android_size_list[0]},{now_Android_size_list[1]}\n")
        return 1

def find_image_on_screen(template_path, threshold=0.8,match_method=cv2.TM_CCOEFF_NORMED,match_boundary="top",matching_color=cv2.COLOR_RGB2BGR):
    global cv2_TM_SQDIFF, cv2_TM_SQDIFF_NORMED, cv2_TM_CCORR, cv2_TM_CCORR_NORMED, cv2_TM_CCOEFF, cv2_TM_CCOEFF_NORMED,logger

    """
    template_path(必要): 模板图像路径
    threshold:          阀值(阀值最低的匹配度最高,还是阀值最高的匹配度最高,视匹配方法而定)
    match_method:       匹配方法:有如下选项(选项的值在本文件内):
                            1. cv2_TM_SQDIFF        # (平方差匹配法) 阀值越 小 匹配度越高 (该方法返回值范围:[0, ∞))
                            2. cv2_TM_SQDIFF_NORMED # (归一化平方差匹配法) 阀值越 小 匹配度越高 (该方法返回值范围:[0, 1])
                            3. cv2_TM_CCORR         # (相关匹配法) 阀值越 大 匹配度越高 (该方法返回值范围:(-∞, ∞))
                            4. cv2_TM_CCORR_NORMED  # (归一化相关匹配法) 阀值越 大 匹配度越高 (该方法返回值范围:[0, 1])
                            5. cv2_TM_CCOEFF        # (相关系数匹配法) 阀值越 大 匹配度越高 (该方法返回值范围:(-∞, ∞))
                            6. cv2_TM_CCOEFF_NORMED # (归一化相关系数匹配法) 阀值越 大 匹配度越高 (该方法返回值范围:[-1, 1])
    match_boundary:     返回的点是所有匹配点的最高,最低,最左,最右,或者返回所有点
                        选项如下:
                            1. top:     # 最高点
                            2. low:     # 最低点
                            3. left:    # 最左点
                            4. right:   # 最右点
                            5. all:     # 所有匹配的点
    matching_color:     匹配的色彩,灰度,或者彩色
                        选项如下:
                            1. cv2_COLOR_RGB2BGR    # 彩色
                            2. cv2_COLOR_BGR2GRAY   # 灰度
    return: (x,y) 或者 [(x0,y0),(x1,y1),(x2,y2)...]
    """

    if not os.path.isfile(template_path):
        logger.error(f"{template_path},模板文件不存在")
        return None

    # 截取屏幕截图
    screenshot = ImageGrab.grab()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, matching_color)

    # 读取模板图像
    template = cv2.imread(template_path,matching_color)

    # 获取模板的高度和宽度
    h, w = template.shape[:2]

    # 进行模板匹配
    res = cv2.matchTemplate(screenshot, template, match_method)

    # 判断阀值的要求
    if match_method in (cv2_TM_CCORR, cv2_TM_CCORR_NORMED, cv2_TM_CCOEFF, cv2_TM_CCOEFF_NORMED):
        loc = np.where(res >= threshold)  # 匹配程度不小于threshold的坐标 y,x(注意: 这里的坐标顺序为(y,x))
    
    elif match_method in (cv2_TM_SQDIFF, cv2_TM_SQDIFF_NORMED):
        loc = np.where(res <= threshold)  # 匹配程度不大于threshold的坐标 y,x(注意: 这里的坐标顺序为(y,x))
    else:
        logger.error("\033[31mmatch_method not exist!\033[0m")
        return None
    try:
        # *号是 解包操作符,zip(*loc[::-1])转变(y,x)为(x,y)的形式
        # 按照要求返回需要的点
        points = list(zip(*loc[::-1]))
    except Exception as e:
        logger.error("in zip()",exc_info=True)
        logger.error(e)
    top_left=None
    if match_boundary=="top":
        top_left = min(points, key=lambda pt: pt[1])
    elif match_boundary=="low":
        top_left = max(points, key=lambda pt: pt[1])
    elif match_boundary=="left":
        top_left = min(points, key=lambda pt: pt[0])
    elif match_boundary=="right":
        top_left = max(points, key=lambda pt: pt[0])            
    elif match_boundary=="all":
        all_points_center=[ (i[0]+w//2,i[1]+h) for i in points ]
        return all_points_center
    if top_left:
        center=(top_left[0]+w//2,top_left[1]+h//2)
        return center
    return None

def click_image_with_backup_methods(image_path, button='left'):
    global logger
    # 该函数仅为click_image2()使用
    # 当尝试点击失败的时候触发
    # 使用其他方法点击
    if_need_paused()
    try:
        try:
            image_center=pyautogui.locateCenterOnScreen(image_path)
            pyautogui.click(image_center,button=button)
        except Exception:
            logger_click_image.debug("Using pyautogui.click and pyautogui.locateCenterOnScreen failure",exc_info=True)
        # 尝试使用另一个函数缩放图像
        with tempfile.NamedTemporaryFile(suffix=".png") as tfile:
            temp_image = tfile.name
            # 构建in_file_path变量
            # 路径格式为 xx/images 例如 sgk/images 所以要的是文件所在目录的上层目录
            # 所以调用两次dirname()
            in_dir_name = os.path.dirname(os.path.dirname(image_path))
            in_file_name=os.path.basename(image_path)
            in_dir_path = os.path.join(os.path.join(start_path, in_dir_name), "images")
            in_file_path=os.path.join(in_dir_path,in_file_name)
            # 使用另一个方法进行图像缩放
            scale_image2(in_file_path,temp_image,global_scale_factor)
            try:
                image_center=pyautogui.locateCenterOnScreen(temp_image)
                pyautogui.click(image_center,button=button)
            except Exception:
                logger_click_image.debug("After scaling the image,Using pyautogui.click and pyautogui.locateCenterOnScreen failure too.",exc_info=True)
            try:
                button_positions = find_image_on_screen(temp_image)
                pyautogui.click(button_positions[0], button_positions[1],button=button)
            except Exception:
                logger_click_image.debug("After scaling the image, clicking with find_image_on_screen failed",exc_info=True)
    except Exception:
        logger_click_image.debug("click_image_with_backup_methods failed",exc_info=True)

def click_image(image_path, r=False, dian=True, threshold=0.8, button='left'):
    """
    点击屏幕上指定图片的位置
    :param image_path: 图片路径
    :param r: 是否使用偏移值
    :param dian: 是否执行点击操作
    """
    if_need_paused()
    button_positions = find_image_on_screen(image_path,threshold=threshold)
    if not button_positions:
        return [False, None]

    ran_x = random.randint(-5, 5) - (50 if r else 0)
    ran_y = random.randint(-5, 5) + (50 if r else 0)

    if dian:
        pyautogui.click(button_positions[0] + ran_x, button_positions[1] + ran_y,button=button)

    return [True, button_positions]


count_error=0
def click_image2(image_path,r=False,func=   lambda x: None,string="", threshold=0.8, button='left',need_backup_methods=True,need_count_error=True):
    """
    点击屏幕上指定图片的位置
    :param image_path:          需要点击的图片的路径
    :param r:                   是否需要在随机数(用于每次点击都有一点微小的变化,但不影响点击效果)+50
    :param func:                当每次点击失败时,要执行的函数
    :param string:              传递给func函数的一个参数
    :param threshold:           传递给find_image_on_screen函数的阀值
    :param button:              点击的键是左键还是其他键
    :param need_backup_methods: 是否需要每次点击失败时尝试其他方法点击
    :param need_count_error:    是否需要进行错误计数,它用于纠正如:1.上次的没有点到,2.这里循环寻找图像,导致卡住在这里(当该参数设置为True时,卡住的时间过长会跳过本次点击)的情况
    """
    global count_error,lastClickedImage,global_scale_factor,logger
    event=threading.Event()
    if_need_paused()
    while True:
        try:
            ran_x = random.randint(-5, 5) - (50 if r else 0)
            ran_y = random.randint(-5, 5) + (50 if r else 0)
            button_positions = find_image_on_screen(image_path,threshold=threshold)
            pyautogui.click(button_positions[0]+ran_x, button_positions[1]+ran_y,button=button)
            lastClickedImage=image_path
            # 当点击成功时,清零错误计数
            count_error=0
            return [True, button_positions]
        except Exception:
            # 如果没有点击到,可能为opencv的匹配问题或者默认寻找图片位置方法的问题,尝试使用pyautogui直接寻找点击,更换匹配图像方法等其他方法
            # 缩放后才出现这个问题
            if need_backup_methods:
                click_image_with_backup_methods(image_path,button=button)
            if not os.path.isfile(image_path):            
                logger.error("图片路径错误 in click_image2 except")
                logger.error(image_path)
            else:
                event.wait(1)
            if need_count_error:
                count_error+=1
            # 如果错误次数大于3次,则尝试点击上一个
            if need_count_error and count_error>3:
                try:
                    if lastClickedImage!="":
                        # 检查是否为空,再使用变量"lastClickedImage",以免报错
                        click_image(lastClickedImage,button=button)
                except Exception:
                    logger_click_image.debug("Failed to click on the last image using click_image",exc_info=True)
            # 如果错误次数过多则跳过本次点击
            if need_count_error and count_error>10:
                break
            if string!="":
                func(string)
            # func()
            logger_click_image.debug("click_image2 failed",exc_info=True)
        event.wait(1)
    # 当跳出循环时,清零错误计数
    count_error=0



def get_exe_size(target_title):
    # 获取所有窗口
    windows = gw.getWindowsWithTitle('')  # 获取所有窗口的句柄

    for window in windows:
        title = window.title
        width, height = window.width, window.height
        if target_title in title:
            return [width,height]


def resize_images_in_directory(image_dir_path,target_exe_name="逍遥"):
    """
    批量缩放指定目录中的图像文件，并将它们保存到新的目录。
    返回缩放后的文件夹路径。
    
    :param image_dir_path: 原始图像文件所在的目录路径
    :param start_path: 基础目录路径，用于保存缩放后的图像文件
    :return: 新的文件夹路径，其中包含所有缩放后的图像
    """
    global start_path,global_scale_factor,logger
    # 获取Android缩放比例
    resize_ratio = get_Android_resize_ratio(target_exe_name)
    global_scale_factor=resize_ratio
    logger.info(f"ratio: {resize_ratio}")

    # 获取输出目录名（根据原始目录名）
    out_dir_name = os.path.basename(os.path.dirname(image_dir_path))
    out_dir_path = os.path.join(os.path.join(start_path, "TEMP"), out_dir_name)
    out_dir_path = os.path.join(out_dir_path,"images")
    # 如果输出目录不存在，则创建它
    if not os.path.exists(out_dir_path):
        os.makedirs(out_dir_path)

    # 遍历图像目录中的所有文件
    for image_file in os.listdir(image_dir_path):
        # 构造源文件的完整路径
        image_file_path = os.path.join(image_dir_path, image_file)

        # 仅处理图像文件（可根据需要扩展更多类型检查）
        if os.path.isfile(image_file_path) and image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            # 构造输出文件的路径
            out_file_path = os.path.join(out_dir_path, image_file)

            # 缩放并保存图像
            scale_image(image_file_path, out_file_path, resize_ratio)

    return out_dir_path

def toggle_pause():
    """
    切换暂停状态的函数
    """
    global paused
    paused = not paused

    if paused:
        logger.info("The program has paused, press the 'esc' key to continue")
    else:
        logger.info("Program run")

def if_need_paused():
    """
    判断是否需要暂停
    """
    global paused
    event=threading.Event()
    while paused:
        event.wait(1)

def get_active_window_position():
    # 获取当前活动窗口的中心坐标

    # 获取当前活动窗口
    active_window = gw.getActiveWindow()

    if active_window:
        # 获取窗口的左上角和右下角坐标
        left, top, right, bottom = active_window.left, active_window.top, active_window.right, active_window.bottom
        
        # 计算窗口的中心坐标
        center_x = (left + right) // 2
        center_y = (top + bottom) // 2
        
        return [center_x, center_y]
        # print(f"当前活动窗口的中心坐标是: ({center_x}, {center_y})")
    else:
        logger.warning("没有找到当前活动窗口")