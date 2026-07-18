import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox # 💡 加上 messagebox 导入
import serial
import serial.tools.list_ports
import threading
import time
from collections import deque
import random

# 🔍 加上详细报错打印，看看它到底被什么卡住了！
try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
    print("Matplotlib 导入成功！")
except Exception as e: # 💡 改成 Exception，把所有隐藏错误都打印出来
    MATPLOTLIB_AVAILABLE = False
    print(f"❌ Matplotlib 导入失败，原因极其离谱: {e}")

# --- 解决 Matplotlib 中文显示乱码 ---
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'DejaVu Sans'] # 💡 指定中文字体优先级
plt.rcParams['axes.unicode_minus'] = False  # 💡 解决负号 '-' 显示为方块的问题

class JointMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("机械臂关节实时监控终端")
        self.root.geometry("1200x700") # 调整窗口大小以容纳更多内容

        # --- 变量定义 ---
        self.serial_port = None
        self.is_reading = False
        self.read_thread = None

        # 实时位置数据存储：{关节ID: Position_StringVar}
        self.joint_position_vars = {i: tk.StringVar(value="----") for i in range(6)}
        self.joint_history_data = {i: deque(maxlen=100) for i in range(6)}
        self.x_data = deque(maxlen=100)
        self.data_count = 0

        # --- 界面布局 ---
        self.create_widgets()

    def create_widgets(self):
        # 1. 顶部控制栏
        control_frame = ttk.LabelFrame(self.root, text="串口设置", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        # 串口号选择
        ttk.Label(control_frame, text="端口:").grid(row=0, column=0, padx=5, pady=2)
        self.port_combo = ttk.Combobox(control_frame, width=15)
        self.refresh_ports()
        self.port_combo.grid(row=0, column=1, padx=5, pady=2)

        # 波特率
        ttk.Label(control_frame, text="波特率:").grid(row=0, column=2, padx=5, pady=2)
        self.baud_combo = ttk.Combobox(control_frame, values=[9600, 19200, 38400, 57600, 115200, 256000, 512000, 921600], width=10)
        self.baud_combo.set("115200")
        self.baud_combo.grid(row=0, column=3, padx=5, pady=2)

        # 按钮
        self.btn_connect = ttk.Button(control_frame, text="连接串口", command=self.toggle_connection)
        self.btn_connect.grid(row=0, column=4, padx=10, pady=2)

        self.btn_refresh = ttk.Button(control_frame, text="刷新端口", command=self.refresh_ports)
        self.btn_refresh.grid(row=0, column=5, padx=5, pady=2)

        # 2. 主内容区 (左右分栏)
        main_content_frame = ttk.Frame(self.root)
        main_content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 左侧：实时数据显示框
        left_frame = ttk.LabelFrame(main_content_frame, text="关节实时位置", padding=10)
        left_frame.pack(side="left", fill="y", padx=(0, 10), pady=5)

        self.position_labels = []
        self.position_entries = []
        for i in range(6):
            label = ttk.Label(left_frame, text=f"关节 {i} 位置:")
            label.grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(left_frame, textvariable=self.joint_position_vars[i], state="readonly", width=15, font=("Helvetica", 14))
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.position_labels.append(label)
            self.position_entries.append(entry)

        # 右侧：图表显示区
        if MATPLOTLIB_AVAILABLE:
            right_frame = ttk.Frame(main_content_frame)
            right_frame.pack(side="right", fill="both", expand=True, pady=5)

            self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100) # 调整图表大小
            self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
            self.canvas_widget = self.canvas.get_tk_widget()
            self.canvas_widget.pack(fill="both", expand=True)

            self.ax.set_title("实时位置趋势")
            self.ax.set_xlabel("时间点")
            self.ax.set_ylabel("位置")
            self.ax.grid(True)

            self.lines = {} # 存储每条曲线的Line2D对象
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'] # 为每个关节设置不同颜色
            for i in range(6):
                line, = self.ax.plot([], [], label=f'关节 {i}', color=colors[i])
                self.lines[i] = line
            self.ax.legend()
            self.canvas.draw()
        else:
            ttk.Label(main_content_frame, text="未安装 Matplotlib，无法显示曲线").pack(side="right", fill="both", expand=True)

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)

    def toggle_connection(self):
        if not self.is_reading:
            self.connect_serial()
        else:
            self.disconnect_serial()

    def connect_serial(self):
        port = self.port_combo.get()
        baudrate = int(self.baud_combo.get())
        print(f"尝试连接串口: {port} @ {baudrate}") # Add this line for debugging
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=0.1)
            self.is_reading = True
            self.btn_connect.config(text="断开连接", style="TButton")  # 可以加个红色样式
            #self.text_display.insert(tk.END, f"--- 已连接 {port} @ {baudrate} ---\n") # 不再需要这个日志输出

            # 清空历史数据和图表
            self.x_data.clear()
            for i in range(1, 7):
                self.joint_history_data[i].clear()
            self.data_count = 0
            if MATPLOTLIB_AVAILABLE:
                for i in range(1, 7):
                    self.lines[i].set_data([], [])
                self.ax.relim()
                self.ax.autoscale_view()
                self.canvas.draw_idle()

            # 开启后台读取线程
            self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
            self.read_thread.start()
        except Exception as e:
            tk.messagebox.showerror("错误", f"无法打开串口:\n{e}")

    def disconnect_serial(self):
        self.is_reading = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.btn_connect.config(text="连接串口")
        #self.text_display.insert(tk.END, "--- 已断开 ---\n") # 不再需要这个日志输出

    # --- 核心逻辑：后台读取循环 ---
    def read_loop(self):
        buffer = ""
        while self.is_reading:
            try:
                if self.serial_port.in_waiting > 0:
                    raw_data = self.serial_port.read(self.serial_port.in_waiting)
                    # 使用utf-8解码，忽略无法解码的字符
                    buffer += raw_data.decode('utf-8', errors='ignore')

                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            # 在主线程中调用UI更新，避免线程问题
                            self.root.after(0, self.parse_and_update, line)
                else:
                    time.sleep(0.001)  # 避免CPU空转，降低延时
            except Exception as e:
                print(f"读取错误或串口断开: {e}")
                # 如果读取错误，尝试断开连接
                self.root.after(0, self.disconnect_serial)
                break

    # --- 数据解析与更新 ---
    def parse_and_update(self, data_str):
        """
        协议解析：
        数据帧格式：五位，第一位是编号（1-6），后四位是实时位置。
        例如："11234" -> ID=1, Pos=1234
        """
        try:
            if len(data_str) == 5 and data_str[0].isdigit() and data_str[1:].isdigit():
                joint_id = int(data_str[0])
                position = int(data_str[1:])

                if 0 <= joint_id <= 5: # 确保关节ID在有效范围内 (0-5)
                    # 更新StringVar，从而更新Entry显示
                    self.joint_position_vars[joint_id].set(str(position))

                    # 更新绘图数据
                    self.joint_history_data[joint_id].append(position)

                    # 仅当处理ID为0的数据时，更新x轴计数，保证所有曲线x轴同步
                    if joint_id == 0:
                        self.data_count += 1
                        self.x_data.append(self.data_count)

                    # 立即更新图表
                    if MATPLOTLIB_AVAILABLE:
                        self.update_plot()

        except ValueError as e:
            print(f"数据解析错误: {data_str}, 错误: {e}")
            pass # 忽略解析错误的行

    def update_plot(self):
        if not MATPLOTLIB_AVAILABLE: return

        # 更新所有关节的曲线
        max_len = 0
        for i in range(6):
            x = list(self.x_data)[-len(self.joint_history_data[i]):]
            y = list(self.joint_history_data[i])
            self.lines[i].set_data(x, y)
            max_len = max(max_len, len(x))

        # 自动调整X轴范围
        if max_len > 0:
            self.ax.set_xlim(self.x_data[0], self.x_data[-1] + 1)

        # 自动调整Y轴范围 (考虑所有关节数据的min/max)
        all_y_data = []
        for i in range(6):
            all_y_data.extend(self.joint_history_data[i])

        if all_y_data:
            min_y = min(all_y_data) - 10 # 留一点边距
            max_y = max(all_y_data) + 10 # 留一点边距
            if max_y == min_y: # 避免y轴范围为0的情况
                min_y -= 1
                max_y += 1
            self.ax.set_ylim(min_y, max_y)

        self.canvas.draw_idle() # 优化绘图性能


if __name__ == "__main__":
    root = tk.Tk()
    app = JointMonitorGUI(root)
    root.mainloop()