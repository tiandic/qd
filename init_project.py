import os
import re
from datetime import datetime

start_project_path=os.path.dirname(os.path.abspath(__file__))
start_path=os.path.join(start_project_path,"bat")
back_dir_path=os.path.join(start_project_path,"back")

os.system("chcp 65001")

print("正在备份环境变量...")

# 备份环境变量
path_variable = os.environ.get('PATH')
with open(os.path.join(back_dir_path,"old_PATH.bak"),"a",encoding="utf-8") as f:
    f.write(f"{datetime.now()}\n")
    f.write(path_variable)
    f.write("\n\n\n")
print("环境变量备份完毕!")
print("正在备份bat文件...")
# 备份bat文件
if os.path.exists(os.path.join(start_path,"qd.bat")):
    with open(os.path.join(start_path,"qd.bat"),encoding="utf-8") as rf:
        with open(os.path.join(back_dir_path,"qd.bat.bak"),"a",encoding="utf-8") as f:
            f.write(f"{datetime.now()}\n")
            f.write(rf.read())
            f.write("\n\n\n")

print("备份完毕!")
print("正在安装所需包...")

# 安装对应包
os.system("pip install -r requirements.txt")

print("安装所需包完毕!")
print("写入bat文件中...")

# 写入bat文件
bat_str=r"""
@echo off
REM 设置工作目录
cd C:/

REM 构建命令部分
set COMMAND=python -m qd.launcher

REM 遍历所有命令行参数
:loop
if "%1"=="" goto end
set COMMAND=%COMMAND% %1
shift
goto loop

:end
REM 执行最终命令
echo Running command: %COMMAND% -nc
%COMMAND% -nc

"""

new_bat_str=re.sub(r"C:/",os.path.dirname(start_project_path).replace("\\", "/"),bat_str)
with open(os.path.join(start_path,"qd.bat"),"w",encoding="utf-8") as f:
    f.write(new_bat_str)

print("写入bat文件完毕!")

print(f"请手动添加'{start_path}'到环境变量!")
print("初始化完毕!")