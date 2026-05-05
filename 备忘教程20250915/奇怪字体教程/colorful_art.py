#!/usr/bin/env python3
from pyfiglet import Figlet
from colorama import init, Fore, Style

# 初始化 colorama（跨平台兼容）
init(autoreset=True)

def print_colorful_art(text, font="standard", colors=None):
    """
    打印彩色 ASCII 艺术字
    :param text: 要转换的文字（建议短单词，如 HELLO、LINUX）
    :param font: 字体样式（可通过 figlet -l 查看所有字体）
    :param colors: 颜色列表（按行上色，默认彩虹色）
    """
    # 生成 ASCII 艺术字
    f = Figlet(font=font)
    art_text = f.renderText(text).splitlines()  # 按行分割

    # 默认彩虹色序列
    if not colors:
        colors = [Fore.RED, Fore.ORANGE, Fore.YELLOW, Fore.GREEN, Fore.BLUE, Fore.MAGENTA]

    # 逐行上色并打印
    for i, line in enumerate(art_text):
        color = colors[i % len(colors)]  # 循环使用颜色
        print(Style.BRIGHT + color + line)

if __name__ == "__main__":
    # 示例1：彩色艺术字 "COLOR"
    print("示例1：彩色艺术字 COLOR")
    print_colorful_art("COLOR", font="slant")  # font="slant"：斜体样式
    print("\n")

    # 示例2：彩虹色艺术字 "LINUX"
    print("示例2：彩虹色艺术字 LINUX")
    rainbow_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE]
    print_colorful_art("LINUX", font="big", colors=rainbow_colors)
    print("\n")

    # 示例3：自定义颜色 + 粗体艺术字 "FUN"
    print("示例3：自定义颜色艺术字 FUN")
    custom_colors = [Fore.MAGENTA, Fore.WHITE, Fore.CYAN]
    print_colorful_art("FUN", font="doh", colors=custom_colors)
