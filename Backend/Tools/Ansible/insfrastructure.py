import os
from .config import AnsibleConfig

class InfrastructureManager:
    def __init__(self):
        self.config = AnsibleConfig()
        
    def get_terraform_output(self):
        # ... 移动现有的 get_terraform_output 函数到这里 ...
        
    def create_inventory(self, tf_output):
        inventory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'inventory.ini'))
        inventory_content = self.config.get_inventory_template(tf_output)
        with open(inventory_path, 'w') as f:
            f.write(inventory_content)
        return inventory_path

    