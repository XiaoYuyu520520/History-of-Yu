# coding=utf-8
import cv2
import numpy as np
import torch
import time
import threading
from flask import Flask, Response
from typing import Union

# 确保 ais_bench 和 det_utils 可被导入
from ais_bench.infer.interface import InferSession
from det_utils import letterbox

# -------------------------- 配置参数 --------------------------
CFG = {
    'conf_thres': 0.25,                 # 适当提高阈值，减少杂乱的框
    'input_shape': [640, 640],
    'model_path': 'v1.om',
    'camera_index': 0,
    'web_server_port': 8089,            # 网页访问端口
    'jpeg_quality': 90                  # 视频流图像质量
}
# ---------------------------------------------------------------

# 全局变量，用于在线程间共享最新的视频帧
output_frame = None
lock = threading.Lock()

# 初始化Flask Web应用
app = Flask(__name__)

def preprocess_image(image, cfg):
    """图像预处理"""
    img, _, _ = letterbox(image, new_shape=cfg['input_shape'])
    img = img[:, :, ::-1]  # BGR to RGB
    img = img.transpose(2, 0, 1)
    img = np.ascontiguousarray(img, dtype=np.float32) / 255.0
    return img

def parse_yolo_output(output_tensor, conf_thres, original_shape, input_shape):
    """
    解析YOLO输出，并转换坐标到原始图像尺寸
    返回: boxes (xyxy), confidences, class_ids
    """
    preds = torch.from_numpy(output_tensor).squeeze(0).permute(1, 0) # [8400, 7]
    
    # 过滤掉置信度低的预测
    high_conf_mask = preds[:, 4] >= conf_thres
    preds = preds[high_conf_mask]
    
    if len(preds) == 0:
        return [], [], []

    # 将中心点+宽高(cx, cy, w, h)格式的box转换为左上角+右下角(x1, y1, x2, y2)格式
    box_cx = preds[:, 0]
    box_cy = preds[:, 1]
    box_w = preds[:, 2]
    box_h = preds[:, 3]
    boxes = torch.stack([
        box_cx - box_w / 2, box_cy - box_h / 2,
        box_cx + box_w / 2, box_cy + box_h / 2
    ], dim=1)
    
    # 坐标缩放回原始图像尺寸
    gain = min(input_shape[0] / original_shape[0], input_shape[1] / original_shape[1])
    pad_x = (input_shape[1] - original_shape[1] * gain) / 2
    pad_y = (input_shape[0] - original_shape[0] * gain) / 2
    
    boxes[:, [0, 2]] -= pad_x
    boxes[:, [1, 3]] -= pad_y
    boxes /= gain
    
    # 裁剪坐标，防止超出图像边界
    boxes[:, 0].clamp_(0, original_shape[1])
    boxes[:, 1].clamp_(0, original_shape[0])
    boxes[:, 2].clamp_(0, original_shape[1])
    boxes[:, 3].clamp_(0, original_shape[0])
    
    confidences = preds[:, 4]
    class_ids = preds[:, 5].int() # v1.om模型中类别ID在第5个索引
    
    return boxes.numpy(), confidences.numpy(), class_ids.numpy()

def draw_on_frame(frame, boxes, confs, cids):
    """在图像上绘制检测框和标签"""
    for box, conf, cid in zip(boxes, confs, cids):
        x1, y1, x2, y2 = map(int, box)
        label = f"ID: {cid} conf: {conf:.2f}"
        
        # 绘制矩形框
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        # 绘制标签背景
        cv2.rectangle(frame, (x1, y1 - 20), (x1 + len(label) * 10, y1), (0, 255, 0), -1)
        # 绘制标签文字
        cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    return frame

def run_inference():
    """
    在后台线程中运行的主函数：捕获视频、推理并更新全局帧
    """
    global output_frame, lock

    print("[INFO] 正在加载模型...")
    try:
        model = InferSession(0, CFG['model_path'])
        print(f"✅ 模型加载成功: {CFG['model_path']}")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}"); return

    print("[INFO] 正在打开摄像头...")
    cap = cv2.VideoCapture(CFG['camera_index'])
    if not cap.isOpened():
        print(f"❌ 无法打开摄像头（索引: {CFG['camera_index']}）"); return
    print(f"✅ 摄像头打开成功，推理开始...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] 无法获取摄像头帧，正在重试...")
            time.sleep(1)
            continue
        
        original_shape = frame.shape
        
        # 预处理 & 推理
        img_input = preprocess_image(frame, CFG)
        output = model.infer([img_input])[0]
        
        # 解析输出并绘制
        boxes, confs, cids = parse_yolo_output(output, CFG['conf_thres'], original_shape, CFG['input_shape'])
        frame_with_detections = draw_on_frame(frame, boxes, confs, cids)

        # 使用线程锁安全地更新全局帧
        with lock:
            output_frame = frame_with_detections.copy()
            
    # 释放资源 (虽然在无限循环中，但保留是好习惯)
    cap.release()

def generate_video_stream():
    """
    一个生成器函数，用于从全局变量中读取帧并将其作为MJPEG流发送
    """
    global output_frame, lock
    while True:
        with lock:
            if output_frame is None:
                # 如果还没有帧，就跳过此次循环
                continue
            
            # 编码为JPEG
            (flag, encoded_image) = cv2.imencode(".jpg", output_frame, [cv2.IMWRITE_JPEG_QUALITY, CFG['jpeg_quality']])
            if not flag:
                continue

        # 以multipart/x-mixed-replace格式产生字节流
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encoded_image) + b'\r\n')

@app.route("/")
def index():
    """主页，显示视频流"""
    # 返回一个简单的HTML页面，其中img标签的src指向我们的视频流路由
    return f"""
    <html>
        <head>
            <title>YOLOv8 Web Stream</title>
        </head>
        <body>
            <h1>实时YOLOv8检测画面</h1>
            <img src="/video_feed" width="{CFG['input_shape'][1]}" height="{CFG['input_shape'][0]}">
        </body>
    </html>
    """

@app.route("/video_feed")
def video_feed():
    """视频流路由，返回一个multipart响应"""
    return Response(generate_video_stream(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
    print("=" * 60)
    print(" YOLOv8 Web Streamer 启动")
    for key, value in CFG.items():
        print(f" - {key:<20}: {value}")
    print("=" * 60)

    # 启动后台线程进行模型推理
    inference_thread = threading.Thread(target=run_inference)
    inference_thread.daemon = True
    inference_thread.start()

    # 启动Flask web服务器
    # host='0.0.0.0' 让服务器可以从网络中的任何IP地址访问
    print(f"\n✅ Web服务器已启动！")
    print(f"请在浏览器中打开 http://<davinci-mini的IP>:{CFG['web_server_port']}")
    print("按 Ctrl+C 退出脚本")
    app.run(host='0.0.0.0', port=CFG['web_server_port'], debug=False, threaded=True)