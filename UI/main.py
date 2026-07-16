import tkinter as tk
from tkinter import ttk, scrolledtext
import serial
import serial.tools.list_ports
import threading
import time
from collections import deque
import random  # 仅用于模拟演示，实际使用时删除

# 尝试导入matplotlib，如果没有安装则提示
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class JointMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("机械臂关节实时监控终端")
        self.root.geometry("1000x700")

        # --- 变量定义 ---
        self.serial_port = None
        self.is_reading = False
        self.read_thread = None

        # 数据存储：{关节ID: {"pos": 0, "volt": [], "temp": []}}
        self.joint_data = {}
        # 曲线历史数据限制长度（例如保留最近50个点）
        self.max_history = 50

        # --- 界面布局 ---
        self.create_widgets()

        # 初始化图表
        if MATPLOTLIB_AVAILABLE:
            self.init_chart()

    def create_widgets(self):
        # 1. 顶部控制栏
        control_frame = ttk.LabelFrame(self.root, text="串口设置", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        # 串口号选择
        ttk.Label(control_frame, text="端口:").grid(row=0, column=0)
        self.port_combo = ttk.Combobox(control_frame, width=10)
        self.refresh_ports()
        self.port_combo.grid(row=0, column=1, padx=5)

        # 波特率
        ttk.Label(control_frame, text="波特率:").grid(row=0, column=2)
        self.baud_combo = ttk.Combobox(control_frame, values=[9600, 115200, 256000, 512000,921600], width=10)
        self.baud_combo.set("115200")
        self.baud_combo.grid(row=0, column=3, padx=5)

        # 按钮
        self.btn_connect = ttk.Button(control_frame, text="连接串口", command=self.toggle_connection)
        self.btn_connect.grid(row=0, column=4, padx=10)

        self.btn_refresh = ttk.Button(control_frame, text="刷新端口", command=self.refresh_ports)
        self.btn_refresh.grid(row=0, column=5)

        # 2. 中间数据显示区 (左右分栏)
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 左侧：关节数字信息
        left_frame = ttk.LabelFrame(main_frame, text="关节实时状态 (位置/电压/温度)", width=300)
        left_frame.pack(side="left", fill="y", padx=(0, 5))
        self.text_display = scrolledtext.ScrolledText(left_frame, width=40, height=30)
        self.text_display.pack(padx=5, pady=5)

        # 右侧：曲线图
        if MATPLOTLIB_AVAILABLE:
            right_frame = ttk.Frame(main_frame)
            right_frame.pack(side="right", fill="both", expand=True)
            self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
            self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            self.ax.set_title("电压/温度趋势 (示例)")
            self.ax.set_xlabel("时间")
            self.line, = self.ax.plot([], [])  # 初始化一条线

        else:
            ttk.Label(main_frame, text="未安装 Matplotlib，无法显示曲线").pack()

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
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=0.1)
            self.is_reading = True
            self.btn_connect.config(text="断开连接", style="TButton")  # 可以加个红色样式
            self.text_display.insert(tk.END, f"--- 已连接 {port} @ {baudrate} ---\n")

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
        self.text_display.insert(tk.END, "--- 已断开 ---\n")

    # --- 核心逻辑：后台读取循环 ---
    def read_loop(self):
        buffer = ""
        while self.is_reading:
            try:
                if self.serial_port.in_waiting > 0:
                    # 读取数据并解码
                    raw_data = self.serial_port.read(self.serial_port.in_waiting)
                    buffer += raw_data.decode('utf-8', errors='ignore')

                    # 处理粘包/断包：按换行符分割
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            self.parse_and_update(line)
                else:
                    time.sleep(0.01)  # 避免CPU空转
            except Exception as e:
                print(f"读取错误: {e}")
                break

    # --- 数据解析与更新 ---
    def parse_and_update(self, data_str):
        """ 
        协议解析： 
        假设数据格式如截图所述："11234" -> ID=1, Pos=1234 
        为了演示，这里也随机生成了电压和温度，实际需等待协议确定 
        """
        try:
            # === 真实解析逻辑开始 ===
            # 假设收到的是纯字符串，如 "11234"
            if len(data_str) >= 5:
                joint_id = data_str[0]  # 第一位：关节编号
                position = int(data_str[1:5])  # 后四位：位置

                # TODO: 待协议确定后，在这里解析电压和温度
                # 目前为了演示曲线功能，我生成一些随机波动数据
                voltage = 12.0 + random.uniform(-0.5, 0.5)
                temperature = 45.0 + random.uniform(-1, 1)

                # 更新内存数据
                self.joint_data[joint_id] = {
                    "pos": position,
                    "volt": voltage,
                    "temp": temperature
                }

                # 更新UI (必须在主线程调用)
                self.root.after(0, self.update_ui, joint_id, position, voltage, temperature)
            # === 真实解析逻辑结束 ===

        except ValueError:
            pass  # 忽略解析错误的行

    def update_ui(self, j_id, pos, volt, temp):
        # 1. 更新文本显示
        log = f"[关节 {j_id}] 位置: {pos} | 电压: {volt:.2f}V | 温度: {temp:.1f}℃\n"
        self.text_display.insert(tk.END, log)
        self.text_display.see(tk.END)  # 自动滚动到底部

        # 2. 更新曲线 (简单演示：绘制所有关节的平均电压)
        if MATPLOTLIB_AVAILABLE:
            # 这里简化处理，只画一条线代表“当前最新电压”
            # 实际项目中应该为每个关节画不同的线
            current_voltages = [d['volt'] for d in self.joint_data.values()]
            if current_voltages:
                avg_volt = sum(current_voltages) / len(current_voltages)

                # 更新图表数据
                x_data = list(range(len(self.line.get_xdata()) + 1))
                y_data = list(self.line.get_ydata()) + [avg_volt]

                # 保持窗口大小
                if len(x_data) > self.max_history:
                    x_data = x_data[-self.max_history:]
                    y_data = y_data[-self.max_history:]

                self.line.set_data(x_data, y_data)
                self.ax.relim()
                self.ax.autoscale_view()
                self.canvas.draw_idle()


if __name__ == "__main__":
    root = tk.Tk()
    app = JointMonitorGUI(root)
    root.mainloop()