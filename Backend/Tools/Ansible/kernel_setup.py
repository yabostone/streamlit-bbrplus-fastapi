#!/usr/bin/env python3
import pexpect
import sys
import time

def install_kernel():
    try:
        # 启动安装脚本
        child = pexpect.spawn('/bin/bash /opt/setup/scripts/install_kernel.sh', encoding='utf-8')
        time.sleep(5)
        child.logfile = sys.stdout  # 输出日志到控制台，这样我们能看到实际输出
        
        # 1. 选择中文界面 - 使用更宽松的匹配模式
        i = child.expect(['Please input.*number.*', 'Please input.*language.*'], timeout=30)
        #print(f"Matched pattern index: {i}")  # 调试输出
        child.sendline('2')
        time.sleep(5)
        
        ### 出现了newer kernel的ok选择
        child.sendline("\r")

        # 2. 选择安装 BBR Plus 内核 6.6 - 同样使用更宽松的匹配
        i = child.expect(['Please input.*number.*', 'Please.*choose.*'], timeout=30)
        #print(f"Matched pattern index: {i}")  # 调试输出
        child.sendline('68')
        time.sleep(10)
        


        
        # 3. 确认删除原有内核
        print("请输入Y确认删除原有内核")
        child.expect(r'.*\[Y/n\].*', timeout=500)  # 使用原始字符串 r'...'
        child.sendline('Y')
        child.sendline('\r')
        
        print("等待可能的内核删除提示...")
        i = child.expect([
            'Abort kernel removal',  # 模式0：出现删除提示
            r'.*\[Y/n\].*',         # 模式1：直接到下一步
            pexpect.TIMEOUT         # 模式2：超时
        ], timeout=500)

        if i == 0:
            # 如果出现了 直接回车默认删除内核
            print("请输入回车默认删除内核==")
            child.sendline('Y')
            child.sendline('\r')
            time.sleep(30)
            child.expect('Abort kernel removal', timeout=150)
            child.sendline('\x1b[C')  # 发送右方向键
            child.sendline('\r')      # 发送回车
        elif i == 1:
            print("没有出现这个内容？")
            # 如果直接到了下一个确认提示
            child.sendline('Y')
        elif i == 2:
            print("等待超时")
            sys.exit(1)

        # 等待内核安装（较长时间）
        child.expect(r'.*\[Y/n\].*', timeout=2400)  # 20分钟超时
        child.sendline('Y')
        child.sendline('\r')
        
        # 确认重启
        child.expect(r'.*\[Y/n\].*', timeout=30)
        child.sendline('N')
        child.sendline('\r')

        # 等待最终完成
        index = child.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=30)
        if index == 0:
            print("Installation completed successfully")
            return True
        else:
            print("Installation timed out")
            return False
            
    except pexpect.TIMEOUT:
        print("Error: Installation timed out")
        return False
    except pexpect.EOF:
        print("Error: Installation terminated unexpectedly")
        return False
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = install_kernel()
    sys.exit(0 if success else 1)