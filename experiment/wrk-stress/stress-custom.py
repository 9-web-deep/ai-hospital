import sys
import subprocess
import time
import matplotlib.pyplot as plt
import re

def run_stress_test(url, lua_script, output_png):
    duration_total = 30  # 总时长 20s
    interval = 1       # 采样分辨率 1s
    threads = 12
    connections = 100
    
    times = []
    qps_values = []
    
    start_time = time.time()
    print(f"开始压测: {url}, 预计时长: {duration_total}s")

    # 循环执行，直到达到总时长
    current_elapsed = 0
    while current_elapsed < duration_total:
        loop_start = time.time()
        
        # 构造 wrk 命令
        cmd = [
            "wrk", 
            f"-t{threads}", 
            f"-c{connections}", 
            f"-d{interval}s", 
            "-s", lua_script, 
            url
        ]
        

        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            print(f'!!!{result.stdout}')
            # 使用正则提取 Requests/sec
            match = re.search(r"Requests/sec:\s+(\d+\.?\d*)", result.stdout)
            if match:
                qps = float(match.group(1))
            else:
                qps = 0.0

            error_match = re.search(r"Non-2xx or 3xx responses:\s+(\d+)", result.stdout)
            if error_match:
                qps = 0.0
        except Exception:
            qps = 0.0
        
        times.append(current_elapsed)
        qps_values.append(qps)
        
        actual_loop_duration = time.time() - loop_start
        sleep_time = max(0, interval - actual_loop_duration)
        time.sleep(sleep_time)
        
        current_elapsed = round(time.time() - start_time, 2)
        print(f"[{output_png}] Time: {current_elapsed}s, QPS: {qps}")

    # 绘制折线图
    plt.figure(figsize=(10, 5))
    plt.plot(times, qps_values, marker='o', linestyle='-', color='b')
    plt.title(f"Stress Test QPS: {url}")
    plt.xlabel("Time (s)")
    plt.ylabel("Requests per Second (QPS)")
    plt.grid(True)
    plt.savefig(output_png)
    print(f"图表已保存至: {output_png}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python stress-custom.py <url> <lua_script> <output_png>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    script_path = sys.argv[2]
    image_name = sys.argv[3]
    
    run_stress_test(target_url, script_path, image_name)