import os
import yaml
import keyboard
from .tool import tool

# 加载配置信息
with open(os.path.join(tool.start_path,"config.yaml"), "r",encoding="utf-8") as file:
    tool.config_data = yaml.safe_load(file)["qd"]
# 注册暂停键
# 监听指定键(默认为'esc'键)按下事件(按下后暂停程序运行,再按一次恢复运行)
keyboard.on_press_key(tool.config_data["global"]["pause_key"], lambda _: tool.toggle_pause())
