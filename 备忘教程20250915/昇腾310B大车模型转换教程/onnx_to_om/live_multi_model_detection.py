# -*- coding: utf-8 -*-

import cv2
import os
from ultralytics import YOLO
import numpy as np
import multiprocessing as mp
import time
from queue import Empty # 导入Empty异常

def frame_producer(q_in):
    """
    进程1: 帧生产者。
    负责从视频流抓取帧，并放入输入队列。
    """
    stream_url = "http://192.168.5.100:8080/stream"
    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print("[Producer] ❌ 错误: 无法打开视频流。")
        return

    print("[Producer] ✅ 视频流连接成功。")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Producer] 🟡 视频流中断，正在尝试重连...")
            time.sleep(1)
            cap.release()
            cap = cv2.VideoCapture(stream_url)
            continue
        
        # --- 修正后的逻辑 ---
        # 目标：确保队列里只有最新的帧。
        # 先尝试非阻塞地清空队列，如果队列本身是空的，就忽略异常。
        try:
            q_in.get_nowait()
        except Empty:
            pass
        # 然后放入最新的帧。
        q_in.put(frame)
        # --- 修正结束 ---

def inference_consumer(q_in, q_out):
    """
    进程2: 推理消费者。
    从输入队列获取帧，进行多模型推理，然后将结果放入输出队列。
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
        (0, 255, 255), (255, 0, 255), (192, 192, 192), (128, 0, 128)
    ]

    model_paths = [f for f in os.listdir(current_dir) if f.endswith('.pt')]
    if not model_paths:
        print("[Consumer] ❌ 错误: 未找到任何 .pt 模型文件。")
        return

    models = {}
    print("[Consumer] 🔍 正在加载模型...")
    for i, model_name in enumerate(model_paths):
        try:
            models[model_name] = {
                "model": YOLO(os.path.join(current_dir, model_name)),
                "color": colors[i % len(colors)]
            }
            print(f"[Consumer]   ✅ 已加载: {model_name}")
        except Exception as e:
            print(f"[Consumer]   ❌ 加载失败: {model_name}, 错误: {e}")

    if not models:
        print("[Consumer] ❌ 错误: 没有任何模型被成功加载。")
        return

    while True:
        frame = q_in.get() # 从输入队列获取帧
        if frame is None: # 结束信号
            break

        # 对帧进行推理和绘制
        for model_name, model_info in models.items():
            model, color = model_info["model"], model_info["color"]
            results = model(frame, verbose=False, conf=0.4)
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf, cls_id = float(box.conf[0]), int(box.cls[0])
                    label = f'{model_name}: {model.names[cls_id]} {conf:.2f}'
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.rectangle(frame, (x1, y1 - 20), (x1 + len(label) * 10, y1), color, -1)
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # 绘制图例
        legend_y = 20
        for model_name, model_info in models.items():
            color = model_info["color"]
            legend_text = f"- {model_name}"
            cv2.putText(frame, legend_text, (10, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
            cv2.putText(frame, legend_text, (10, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, model_info["color"], 2)
            legend_y += 25
        
        if q_out.full():
            q_out.get_nowait() # 丢弃旧的已处理帧
        q_out.put(frame)

if __name__ == "__main__":
    # 在Windows上使用多进程，建议加上这句
    mp.set_start_method('spawn', force=True)

    input_queue = mp.Queue(maxsize=1)
    output_queue = mp.Queue(maxsize=1)

    producer_process = mp.Process(target=frame_producer, args=(input_queue,))
    consumer_process = mp.Process(target=inference_consumer, args=(input_queue, output_queue,))

    producer_process.start()
    consumer_process.start()

    print("[Main] ✅ 主程序启动，等待处理后的帧...")
    print("[Main] 按 'q' 键退出。")

    while True:
        try:
            frame = output_queue.get(timeout=5) # 增加超时时间以应对模型加载
            cv2.imshow('Live Multi-Model Detection (Optimized)', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Empty:
            if not consumer_process.is_alive() or not producer_process.is_alive():
                print("[Main] 🟡 一个或多个子进程已停止，程序退出。")
                break
            print("[Main] 🟡 等待处理结果超时...")
            continue

    print("[Main] 正在关闭...")
    producer_process.terminate()
    consumer_process.terminate()
    producer_process.join()
    consumer_process.join()
    cv2.destroyAllWindows()