import webview
from backend.api import API
import os
import sys
from pathlib import Path


static_target = Path.cwd() / "static"

api = API()    # 本地接口

def on_shown():
    # print('程序启动')
    pass

def on_loaded():
    # print('DOM加载完毕')
    pass


def on_closing():
    pass

def WebViewApp():
    # 系统分辨率
    screens = webview.screens
    screens = screens[0]
    width = screens.width
    height = screens.height
    # 程序窗口大小
    initWidth = int(width * 2 / 3)
    initHeight = int(height * 4 / 5)
    minWidth = int(initWidth / 2)
    minHeight = int(initHeight / 2)

    # 设置工作目录为 main.py 所在目录（无论从哪里启动）
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的程序
        # 获取当前脚本（main.py）所在的目录
        base_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(base_path)  # 设置工作路径为脚本所在目录

    is_dev = False
    # 视图层页面URL
    if is_dev:
        # 开发环境
        MAIN_DIR = f'http://localhost:5173/'
        template = os.path.join(MAIN_DIR, "")    # 设置页面，指向远程
    else:
        # 生产环境
        template = os.path.join(static_target, "index.html")    # 设置页面，指向本地
    # 创建窗口
    window = webview.create_window(title="码字", url=template, js_api=api, width=initWidth, height=initHeight, min_size=(minWidth, minHeight))

    # 绑定事件
    window.events.shown += on_shown
    window.events.loaded += on_loaded
    window.events.closing += on_closing

    api.set_window(window)
    # 启动窗口
    if is_dev:
        # 开发环境
        webview.start(http_server=True,debug=True)
    else:
        # 生产环境
        webview.start(http_server=True)


if __name__ == '__main__':

    WebViewApp()
