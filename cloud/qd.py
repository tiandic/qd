'''
encode: utf-8
Date: 2025-01-18 12:56:29
LastEditTime: 2025-01-20 18:13:11
FilePath: /qd/cloud/qd.py
'''
import os
import datetime
import threading
import subprocess
from ..tool import tool

start_path=tool.start_path
cloud_config_data=tool.config_data["cloud"]

def finish_cloud_sign():
    global cloud_config_data
    event=threading.Event()
    sleep_second_finsh_cloud=cloud_config_data["sleep_second_finsh_cloud"]
    event.wait(sleep_second_finsh_cloud)
    browser_name=cloud_config_data["browser_name"]
    subprocess.run(["taskkill","/IM",browser_name])
    tool.logger.debug("end cloud")

def cloud_sign():
    global start_path,cloud_config_data   
    cloud_sign_time_file_name=os.path.join(start_path,"cloud_sign_time.txt")
    is_need_sign=False
    # 获取今天的日期
    today_date = datetime.date.today()

    # 进行检查 是否需要打开网址(每天一次)
    if os.path.exists(cloud_sign_time_file_name):
        # 检查是否上次打开url的时间是当天
        with open(cloud_sign_time_file_name,encoding="utf-8") as f:
            sign_time=f.read()
        
        # 如果不是当天则设置需要签到
        if int(sign_time)!=today_date.day:
            is_need_sign=True
    else:
        is_need_sign=True
    # 写入今天的天数
    with open(cloud_sign_time_file_name,"w",encoding="utf-8") as f:
        f.write(str(today_date.day))

    if is_need_sign:
        tool.logger.debug("start cloud...")

        # 启动一个线程,等待一会儿关闭浏览器
        finish_cloud_sign_thread=threading.Thread(target=finish_cloud_sign)
        finish_cloud_sign_thread.start()

        # 获取浏览器路径
        browser_dir_path=cloud_config_data["browser_dir_path"]
        browser_name=cloud_config_data["browser_name"]
        browser_path=os.path.join(browser_dir_path,browser_name)
        # 获取url
        cloud_url=cloud_config_data["cloud_url"]
        # 使用命令行的方式用指定浏览器打开url
        subprocess.run([browser_path, cloud_url])
    else:
        tool.logger.debug("signed in done!")

def start_cloud_sign_threading():
    t_cloud=threading.Thread(target=cloud_sign)
    t_cloud.start()

def main():
    start_cloud_sign_threading()

if __name__ == '__main__':
    main()
    