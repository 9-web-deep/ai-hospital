import subprocess
import re
import time
import matplotlib.pyplot as plt

# --- 配置区 ---
TARGET_URL = "http://localhost:8082/api/nurse/infusion/start"
LUA_SCRIPT = "infusion_start.lua"  # 确保你有之前创建的 Lua 脚本
DURATION_PER_SAMPLE = 2       # 每次采样持续时间（秒）
TOTAL_SAMPLES = 10            # 总共采样次数
THREADS = 4
CONNECTIONS = 50
# --------------

times = []
qps_values = []

print(f"开始压测采样，预计耗时 {DURATION_PER_SAMPLE * TOTAL_SAMPLES} 秒...")

for i in range(TOTAL_SAMPLES):
    # 执行 wrk 命令 (wrk 或 wrk2 均可)
    cmd = f"wrk -t{THREADS} -c{CONNECTIONS} -d{DURATION_PER_SAMPLE}s -s {LUA_SCRIPT} {TARGET_URL}"
    result = subprocess.check_output(cmd, shell=True).decode('utf-8')
    
    # 使用正则提取 Requests/sec
    match = re.search(r"Requests/sec:\s+(\d+\.?\d*)", result)
    if match:
        qps = float(match.group(1))
        qps_values.append(qps)
        times.append(i * DURATION_PER_SAMPLE)
        print(f"进度: {i+1}/{TOTAL_SAMPLES} | 当前 QPS: {qps}")

# 绘制折线图
plt.figure(figsize=(10, 5))
plt.plot(times, qps_values, marker='o', linestyle='-', color='b')
plt.title('Real-time QPS (Requests per Second)')
plt.xlabel('Time (seconds)')
plt.ylabel('QPS')
plt.grid(True)
plt.savefig('qps_chart.png') # 保存为图片
print("压测完成！折线图已保存为 qps_chart.png")
plt.show()