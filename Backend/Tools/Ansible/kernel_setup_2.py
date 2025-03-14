#!/usr/bin/env python3
import pexpect
import sys
import time

def install_kernel():
    try:
        # 第二轮：配置 BBR
        print("=== 第二轮：开始配置 BBR ===")
        child = pexpect.spawn('/bin/bash /opt/setup/scripts/install_kernel.sh', encoding='utf-8')
        time.sleep(5)
        child.logfile = sys.stdout

        # 2. 选择 BBR 配置选项
        i = child.expect(['Please input.*number.*', 'Please.*choose.*'], timeout=30)
        child.sendline('3')  # 选择 BBR 配置
        time.sleep(20)

        # 3. 确认配置
        child.expect(r'.*选择队列算法.*', timeout=30)
        child.sendline('4')
        time.sleep(2)

        # 4. 再次确认
        child.expect(r'.*\[Y/n\].*', timeout=30)
        child.sendline('Y')
        time.sleep(2)

        # 等待最终完成
        index = child.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=30)
        if index == 0:
            print("BBR Configuration completed successfully")
            return True
        else:
            print("Configuration timed out")
            return False

    except pexpect.TIMEOUT:
        print("Error: Process timed out")
        return False
    except pexpect.EOF:
        print("Error: Process terminated unexpectedly")
        return False
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = install_kernel()
    sys.exit(0 if success else 1)