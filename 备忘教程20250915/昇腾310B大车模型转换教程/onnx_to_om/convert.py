import os
import sys
import subprocess
import onnx

# ==============================================================================
#  配置区: 请在这里修改你要转换的 ONNX 模型文件路径
# ==============================================================================
ONNX_MODEL_PATH = "/root/onnx_to_om/v3.onnx"
# ==============================================================================

# --- ANSI 颜色定义 ---
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m' # No Color

def get_onnx_input_info(model_path):
    """解析ONNX模型，返回第一个输入节点的名称和形状。"""
    try:
        model = onnx.load(model_path)
        if not model.graph.input:
            return None, "模型中没有找到输入节点"
            
        input_node = model.graph.input[0]
        name = input_node.name
        shape = [d.dim_value for d in input_node.type.tensor_type.shape.dim]
        
        # 检查是否有动态维度
        if any(d == 0 for d in shape):
             return None, f"模型包含动态维度 (形状: {shape})，脚本暂不支持，请手动执行atc命令。"
             
        return name, shape
    except Exception as e:
        return None, f"加载或解析ONNX模型失败: {e}"

def main():
    """主执行函数"""
    print(f"{Colors.GREEN}---> 准备转换模型: {Colors.YELLOW}{ONNX_MODEL_PATH}{Colors.NC}")

    # 1. 检查文件是否存在
    if not os.path.exists(ONNX_MODEL_PATH):
        print(f"{Colors.RED}错误: 文件未找到: {ONNX_MODEL_PATH}{Colors.NC}")
        sys.exit(1)

    # 2. 解析模型输入信息
    print(f"{Colors.GREEN}---> 正在解析模型输入信息...{Colors.NC}")
    input_name, input_shape = get_onnx_input_info(ONNX_MODEL_PATH)
    
    if input_name is None:
        print(f"{Colors.RED}错误: {input_shape}{Colors.NC}")
        sys.exit(1)
        
    shape_str = ",".join(map(str, input_shape))
    input_shape_arg = f"{input_name}:{shape_str}"
    print(f"{Colors.GREEN}---> 成功获取输入信息: {Colors.YELLOW}{input_shape_arg}{Colors.NC}")

    # 3. 构建atc命令
    output_om_prefix = os.path.splitext(ONNX_MODEL_PATH)[0]
    soc_version = "Ascend310B4"
    
    # 构建一个完整的shell命令来处理环境设置
    atc_command = (
        f"conda deactivate &> /dev/null; "
        f"source /usr/local/Ascend/ascend-toolkit/set_env.sh; "
        f"atc --model='{ONNX_MODEL_PATH}' "
        f"--framework=5 "
        f"--output='{output_om_prefix}' "
        f"--input_shape='{input_shape_arg}' "
        f"--soc_version={soc_version}"
    )

    print(f"{Colors.GREEN}---> 准备执行atc转换命令...{Colors.NC}")
    print(f"{Colors.YELLOW}==================== ATC Command ===================={Colors.NC}")
    print(atc_command)
    print(f"{Colors.YELLOW}===================================================={Colors.NC}")

    # 4. 执行命令
    # 使用 subprocess.run 在 shell 中执行完整的命令字符串
    process = subprocess.run(atc_command, shell=True, capture_output=True, text=True, executable='/bin/bash')

    # 5. 检查结果
    if process.returncode == 0 and "ATC run success" in process.stdout:
        print(f"\n{Colors.GREEN}===================================================={Colors.NC}")
        print(f"{Colors.GREEN}🎉 转换成功! 🎉{Colors.NC}")
        print(f"{Colors.GREEN}OM模型已生成: {Colors.YELLOW}{output_om_prefix}.om{Colors.NC}")
        print(f"{Colors.GREEN}===================================================={Colors.NC}")
    else:
        print(f"\n{Colors.RED}===================================================={Colors.NC}")
        print(f"{Colors.RED}🔥 转换失败! 🔥{Colors.NC}")
        print(f"{Colors.RED}请检查下面的atc日志以获取详细错误信息。{Colors.NC}")
        print(f"{Colors.RED}-------------------- STDOUT --------------------{Colors.NC}")
        print(process.stdout)
        print(f"{Colors.RED}-------------------- STDERR --------------------{Colors.NC}")
        print(process.stderr)
        print(f"{Colors.RED}===================================================={Colors.NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
