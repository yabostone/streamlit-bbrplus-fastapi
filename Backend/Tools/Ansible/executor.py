import json
from manager import AnsibleManager
import os
class AnsibleExecutor:
    def __init__(self):
        self.ansible_manager = AnsibleManager()

    def initialize_environment(self):
        """初始化环境"""
        ##print("\n开始初始化环境...")
        ##tf_output, inventory_path = self.ansible_manager.setup_environment()
        ##success, result = self.ansible_manager.run_initialization(inventory_path, tf_output)
        
        ##if not success:
        ##    raise Exception(f"初始化环境失败: {result}")
            
        ##return inventory_path
        inventory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'inventory.ini'))
        print(f"Inventory path: {inventory_path}")
        return inventory_path

    def setup_services(self, inventory_path, playbook_name: str):
        """安装和配置服务"""
        print(f"\n开始安装{playbook_name}...")
        success, result = self.ansible_manager.install_services(inventory_path, playbook_name)
        
        print(f"安装结果: {'成功' if success else '失败'}")
        print(f"详细信息:\n{result}")
        
        if not success:
            raise Exception("服务安装失败")

    def fetch_v2ray_config(self, inventory_path):
        """获取V2Ray配置信息"""
        print("\n获取v2ray信息...")
        success, result = self.ansible_manager.get_v2ray_info(inventory_path)
        
        if not success:
            raise Exception(f"获取v2ray信息失败: {result}")
            
        try:
            v2ray_info = json.loads(result)
            print("\nV2Ray配置信息:")
            print(json.dumps(v2ray_info, indent=2, ensure_ascii=False))
            return v2ray_info
        except json.JSONDecodeError:
            print("V2Ray信息输出:\n", result)
            return None