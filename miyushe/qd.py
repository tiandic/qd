'''
encode: utf-8
Date: 2024-08-20 19:06:20
LastEditTime: 2025-01-21 09:20:25
FilePath: /qd/miyushe/qd.py
'''
'''
encode: utf-8
Date: 2024-08-07 09:02:21
LastEditTime: 2025-01-20 11:30:46
FilePath: /qd/miyushe/qd.py
'''


import os
import sys
import random
import threading
import pyautogui
from ..tool import tool
from PIL import ImageGrab

start_path=os.path.join(tool.start_path,"miyushe")
images_path=os.path.join(start_path,"images")

def get_image_path(image_name):
    """
    获取图片的完整路径
    :param image_name: 图片文件名
    :return: 图片的完整路径
    """
    global images_path
    return os.path.join(images_path, image_name)
shangyige=get_image_path("yuanshen_qd_path.png")

def if_color(x, y, target_color):
     # 获取屏幕截图
    screenshot = ImageGrab.grab()
    result=True
    for i in range(10):
        x_r=random.randint(-10,10)
        y_r=random.randint(-10,10)
        # print(x_r,y_r)
        if result:
            # 获取指定坐标处的颜色
            pixel_color = screenshot.getpixel((x+x_r, y+y_r))
            # 比较颜色是否匹配
            result = pixel_color == target_color
        else:
            return False
    return result

def update_app():
    # 检查更新函数
    try:
        tool.click_image(get_image_path("geng_x.png"))
        tool.click_image2(get_image_path("an_zhuang.png"))
        tool.click_image2(get_image_path("da_kai.png"))
    except Exception:
        tool.logger_click_image.debug("Update button not found",exc_info=True)

def qd(name,wait_time=0):
    global images_path,shangyige
    event=threading.Event()
    path=get_image_path(f"{name}.png")
    tool.click_image2(path)
    shangyige=path
    # qd_path
    path=get_image_path(f"{name}_qd_path.png")
    tool.click_image2(path)
    shangyige=path
    # qd
    path=get_image_path("qd.png")
    tool.click_image2(path)
    shangyige=path
     
    event.wait(wait_time)
    # 检查更新
    # update_app()

def shangyige_and_click(image_name,wait_time=0,click_func_type=2):
    global shangyige
    event=threading.Event()
    
    path=get_image_path(image_name)
    if click_func_type==2:
        tool.click_image2(path)
    elif click_func_type==1:
        tool.click_image(path)
    shangyige=path
    
    event.wait(wait_time)
     

def main(if_skip=False,no_check_update=False,no_miyushe_sleep=False,zoom=False):
    """
    主函数
    
    if_skip=False                 # 是否直接跳到获取米游币
    no_check_update=False         # 是否不检测更新
    no_miyushe_sleep=False        # 是否等待15秒,让米游社启动完毕
    zoom=False                    # 是否启用支持缩放
    """
    global shangyige,images_path,geng_x
    event=threading.Event()
    if len(sys.argv)>1:
        if sys.argv[1]=="y":
            no_miyushe_sleep=False
            if_skip=True
    #  print(sys.argv)
    # 如果模拟器进行了缩放
    if zoom and tool.get_Android_resize_ratio("逍遥")!=1:
        tool.logger.info("processing images...")
        images_path=tool.resize_images_in_directory(images_path)
        tool.logger.info("processed images!")

    if not no_miyushe_sleep:
        temp=15
        while temp>0:
            out_print=f"sleeping...{temp}s"
            out_print = out_print.ljust(14)
            print(out_print)
            # 将光标移动回行首
            print("\033[F",end="")
            event.wait(1)
            temp-=1
    #  event.wait(5)
    tool.logger.info("start miyushe!".ljust(14))
    # 更新  废除过多检测：(不知道什么时候会突然弹出更新窗口,所以下面多次检查更新)
    #                   太多检测更新会导致程序看上去很卡(一次检测会需要一定的时间)
    # event.wait(2)
     
    if not no_check_update:
        # 尝试点击可能弹出的提示更新
        update_app()

    if not if_skip:
        # 原神
        path=get_image_path("yuanshen_qd_path.png")
        # 当点击"酒馆"失败时,可能是出现了"青少年模式"的弹窗,使用click_image点一下"我知道了"
        tool.click_image2(path,func=tool.click_image,string=get_image_path("me_know.png"))

        # update_app()
        shangyige=path
        # qd
        # qd.png 为打卡图像
        shangyige_and_click("qd.png",2)

        # 大别野
        qd("dabieye",2)

        # 绝区零
        qd("juequl",2)
        

        # 星穹铁道
        qd("xqtdao",2)
        

        # 崩坏3
        qd("bengh3",2)
        

        # 未定事件簿
        qd("weid",2)
        

        # 崩坏学园2
        qd("xueyuan",2)
        

        # 返回原神
        for i in range(6):
            shangyige_and_click(f"f_{i}.png",1)
        # update_app()
         

        # 签到福利
        event.wait(4)
        shangyige_and_click("yuanshen_qd.png",10)
        # 向下拉一下,避免加载不出问题
        pyautogui.scroll(-1)
        event.wait(2)
        pyautogui.scroll(1)
        event.wait(2)
        # 点击红点(即可以领取的物品位置)
        shangyige_and_click("hongd.png",2)
        try:
            # 有时候会弹出一个以后要不要通知签到福利的窗口,点击一下"不用了"
            shangyige_and_click("hd_buyongle.png",2,click_func_type=1)
        except Exception:
            tool.logger_click_image.debug("shangyige_and_click(\"hd_buyongle.png\",2,click_func_type=1)",exc_info=True)
        # 点击退出签到福利
        shangyige_and_click("x.png",2)

        shangyige_and_click("tui_meiri.png",2)

    # update_app()
    # 获取米游币
    # 随机获取需要点赞,分享的次数
    dian_z=0
    dian_z_max=random.randint(6,10)
    fenx=0
    fenx_max=random.randint(3,4)


    i=3
    error_count=0
    # 初始化上一次的点赞的位置
    # 用于避免长时间点击同一赞多次
    dian_z_xy=[0,0]
    # 是否点击"返回"
    # 用于避免点进一个视频后,长时间点赞视频评论
    # 导致一直在点赞循环,无法继续后面的"分享"之类的逻辑
    # 每两次点击一下,通过每次点赞后取反实现
    is_back=False
    # 用于辅助上面的参数
    is_enter_post=False
    
    # 各个步骤的是否错误
    is_dianz_error=False    # 暂时没用,以后可能有用
    is_fenx_error =False

    while True:
        # 用于记录到了哪一步
        # 看看是到哪里发生错误
        # 0:点赞错误
        # 1:分享错误
        count=0
        # 点赞
        try:
            dian=True
            path=get_image_path("dianz.png")

            # 点赞的位置
            x_y=tool.click_image(path,dian=dian)[1]
            shangyige=path
            tool.logger.info(f"点赞{x_y}")
            # 需要点击"返回"(避免点进一个视频后,长时间点赞视频评论)
            # if is_back and is_enter_post:
            #     shangyige_and_click("Android_tui.png",2)
            #     pyautogui.moveTo(tool.get_active_window_position())

            # 每两次点击一下
            # is_back=not is_back
            # 如果上次点赞位置与当前点赞位置的差小于15
            # 则跳过  进入帖子的逻辑,移动鼠标到模拟器的中心,向下滑动
            if (abs(dian_z_xy[0]-x_y[0])<15 and abs(dian_z_xy[1]-x_y[1])<15):
                pyautogui.moveTo(tool.get_active_window_position())
                pyautogui.scroll(-2)
                event.wait(2)

                continue
            dian_z_xy=x_y
            error_count=0
            if dian:
                dian_z+=1
            ran_y=random.randint(10,20)
            event.wait(2)
             
            
            # 判断点赞位置的上一点的位置
            # 是否为白色
            # 如果是,则大概率为文章类型的帖子
            # 那就进入,并点击"分享",完成任务
            if if_color(x_y[0],x_y[1]-150-ran_y, (255, 255, 255)) and fenx<fenx_max:
                # 进入帖子
                is_enter_post=True
                count+=1

                # 点击帖子白色地方进入
                pyautogui.click(x_y[0],x_y[1]-150-ran_y)
                event.wait(3)
                # 分享
                shangyige_and_click("fenx.png",2,click_func_type=1)
                # 复制链接
                path=get_image_path("fuzhi.png")
                temp_X_Y=tool.click_image(path)[1]
                shangyige=path
                event.wait(2)
                # 返回
                shangyige_and_click("tui.png",1)
                pyautogui.moveTo(temp_X_Y[0],temp_X_Y[1])
                fenx+=1
                # 退出了帖子
                is_enter_post=False

            tool.logger.info(f"{dian_z}/{dian_z_max}, {fenx}/{fenx_max}")
            pyautogui.scroll(-2)
            event.wait(2)
            if fenx>=fenx_max and dian_z>=dian_z_max:
                break

        except Exception:
            tool.logger_click_image.debug("No like button found",exc_info=True)
            error_count+=1

            # 判断是到哪一步发生错误
            if count==0:
                is_dianz_error=True
            elif count==1:
                is_fenx_error=True

            # 如果遇到分享错误,可能是点击到视频了
            if is_fenx_error:
                shangyige_and_click("Android_tui.png",2)
                pyautogui.moveTo(tool.get_active_window_position())
                
            # 错误次数(太久没有点到赞,可能是点到的视频里面)
            # 错误次数太多
            if error_count>5:
                shangyige_and_click("Android_tui.png",2)
                pyautogui.moveTo(tool.get_active_window_position())
            pyautogui.scroll(-2)
            if error_count>10:
                tool.logger.warning("点赞失败")
                break                
            # pyautogui.scroll(-2)
            event.wait(4)
             

    
if __name__ == '__main__':
    main()
