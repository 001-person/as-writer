import os
import subprocess
import shutil
from pathlib import Path
import sys

# 路径设置
frontend_dir = Path("frontend")
backend_src = Path("backend/src/backend")
static_target = backend_src / "dist" / "static"  # 假设后端用 webview.load_url("static/index.html")

# 步骤 1：构建前端
def build_frontend():
    print("🚧 构建前端...")
    subprocess.run([r"C:\Users\pc\AppData\Roaming\npm\pnpm.cmd", "install"], cwd=frontend_dir, check=True)
    subprocess.run([r"C:\Users\pc\AppData\Roaming\npm\pnpm.cmd", "build"], cwd=frontend_dir, check=True)

def copy_frontend_to_backend():
    print("📦 复制前端构建产物到后端静态目录...")
    dist_dir = os.path.join(frontend_dir, 'dist')
    if os.path.exists(static_target):
        shutil.rmtree(static_target)
    shutil.copytree(dist_dir, static_target)

# 步骤 3：使用 pyinstaller 打包 python
def build_python():
    print("🐍 打包 Python 应用...")
    os.chdir(backend_src)
    subprocess.run([sys.executable, "-m", "PyInstaller", "main.spec"], check=True)

if __name__ == "__main__":
    build_frontend()
    copy_frontend_to_backend()
    build_python()
    print("✅ 打包完成！生成文件在 dist/ 目录。")
