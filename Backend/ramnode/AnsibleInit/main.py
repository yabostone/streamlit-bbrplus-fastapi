import time
from ....Ansible.executor import AnsibleExecutor
#from coscloud.src.Ansible.executor import AnsibleExecutor



def main():
    executor = AnsibleExecutor()
    
    try:
        # 步骤1: 初始化环境
        inventory_path = executor.initialize_environment()
        
        # 步骤2: 安装服务
        executor.setup_services(inventory_path)
        
        # 等待服务启动
        time.sleep(10)
        
        # 步骤3: 获取配置信息
        v2ray_config = executor.fetch_v2ray_config(inventory_path)
        
    except Exception as e:
        print(f"执行过程中出现未预期的错误: {str(e)}")
    finally:
        executor.ansible_manager.wsl.close()

if __name__ == "__main__":
    main()