#!/usr/bin/env python3
"""
彩色名字打印模块
功能：在终端打印彩色 ASCII 艺术字风格的名字，支持自定义字体和颜色
用法：
    from colorful_name_printer import print_colorful_name, print_colorful_names
    print_colorful_name("YuShuihang")  # 打印单个名字
    print_colorful_names(["A", "B", "C"])  # 打印多个名字
"""

from pyfiglet import Figlet
from colorama import init, Fore, Style

# 初始化 colorama（只初始化一次，避免重复调用）
init(autoreset=True)

def print_colorful_name(
    name: str,
    font: str = "slant",
    colors: list = None,
    show_title: bool = False
) -> None:
    """
    打印单个彩色 ASCII 艺术字名字（核心函数，类似 print 的用法）
    
    Args:
        name: 要打印的名字/文本（建议短字符串）
        font: 字体样式（支持：slant、standard、big、doh、starwars 等）
        colors: 颜色列表（默认使用彩虹色渐变，可传入 [Fore.RED, Fore.GREEN, ...]）
        show_title: 是否显示名字标注（【name】），默认不显示
    """
    # 默认颜色列表（colorama 支持的标准颜色）
    default_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    used_colors = colors if colors is not None else default_colors
    
    try:
        # 生成 ASCII 艺术字
        f = Figlet(font=font)
        art_text = f.renderText(name).splitlines()
        
        # 显示名字标注（可选）
        if show_title:
            print(f"\n【{name}】")
        
        # 逐行上色打印
        for i, line in enumerate(art_text):
            color = used_colors[i % len(used_colors)]  # 循环取色，避免索引越界
            print(Style.BRIGHT + color + line)
    except Exception as e:
        # 异常降级：如果艺术字生成失败，直接打印普通彩色文本
        print(f"[彩色打印失败] {Style.BRIGHT + Fore.RED + name}：{str(e)}")

def print_colorful_names(
    names: list,
    fonts: list = None,
    color_themes: list = None,
    show_header: bool = True,
    show_footer: bool = True
) -> None:
    """
    批量打印多个彩色名字（预设差异化颜色主题）
    
    Args:
        names: 名字列表（如 ["YuShuihang", "YangYuhan"]）
        fonts: 字体列表（为每个名字分配不同字体，默认统一使用 slant）
        color_themes: 颜色主题列表（为每个名字分配不同颜色组，默认使用预设4组主题）
        show_header: 是否显示顶部标题栏，默认显示
        show_footer: 是否显示底部分隔线，默认显示
    """
    # 预设4组颜色主题（差异化渐变）
    default_color_themes = [
        [Fore.RED, Fore.YELLOW, Fore.GREEN],    # 红黄绿
        [Fore.BLUE, Fore.CYAN, Fore.MAGENTA],   # 蓝青紫
        [Fore.YELLOW, Fore.RED, Fore.CYAN],     # 黄红青
        [Fore.GREEN, Fore.BLUE, Fore.MAGENTA]   # 绿蓝紫
    ]
    used_themes = color_themes if color_themes is not None else default_color_themes
    used_fonts = fonts if fonts is not None else ["slant"] * len(names)  # 默认统一字体
    
    # 显示顶部标题
    if show_header:
        print("\n" + Style.BRIGHT + Fore.WHITE + "===== 彩色名字列表 =====")
    
    # 批量打印每个名字
    for i, name in enumerate(names):
        # 循环使用主题和字体（避免列表长度不足）
        theme = used_themes[i % len(used_themes)]
        font = used_fonts[i % len(used_fonts)]
        print_colorful_name(name, font=font, colors=theme, show_title=True)
    
    # 显示底部分隔线
    if show_footer:
        print("\n" + Style.BRIGHT + Fore.WHITE + "=======================")

# 测试代码（导入时不会执行，仅在直接运行模块时生效）
if __name__ == "__main__":
    # 测试单个名字打印
    print("=== 测试单个名字 ===")
    print_colorful_name("Test")
    
    # 测试批量名字打印（默认配置）
    print("\n=== 测试批量名字（默认配置）===")
    test_names = ["YuShuihang", "YangYuhan", "ChenTianci", "XuJiaming"]
    print_colorful_names(test_names)
    
    # 测试自定义字体和颜色
    print("\n=== 测试自定义配置 ===")
    custom_fonts = ["slant", "doh", "big", "standard"]
    custom_colors = [
        [Fore.RED, Fore.MAGENTA],
        [Fore.GREEN, Fore.CYAN],
        [Fore.YELLOW, Fore.BLUE],
        [Fore.WHITE, Fore.RED]
    ]
    print_colorful_names(test_names, fonts=custom_fonts, color_themes=custom_colors)
