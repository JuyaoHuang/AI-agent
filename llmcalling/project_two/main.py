import sys
import os
import uvicorn
import subprocess
"""
give up:
run: uvicorn services.server:app --reload
or fastapi dev main.py --port 8080
"""

"""
run: python main.py
"""
def install_dependencies():
    """安装必要的依赖"""
    dependencies = [
        "fastapi",
        "uvicorn",
        "pydantic",
    ]

    print("检查依赖包...")
    missing_deps = []

    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
        except ImportError:
            missing_deps.append(dep)

    if missing_deps:
        print(f"缺少以下依赖包: {', '.join(missing_deps)}")
        print("正在安装...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install"] + missing_deps
            )
            print("依赖包安装完成！")
        except subprocess.CalledProcessError:
            print("依赖包安装失败，请手动安装:")
            print(f"pip install {' '.join(missing_deps)}")
            return False

    return True


def start_fastapi():
    """Boot fastAPI server"""
    print("Starting FastAPI...")
    uvicorn.run(
        "services.server:app",
        host="0.0.0.0",
        port=8028,
        reload=True
    )

def main():
    """Major boot process"""
    if not install_dependencies():
        return

    print("\nServer boot successful.")
    print("API 文档地址: http://localhost:8028/docs")
    print("ReDoc 文档地址: http://localhost:8028/redoc")
    print("按 Ctrl+C 停止服务器\n")

    start_fastapi()

if __name__ == "__main__":
    main()