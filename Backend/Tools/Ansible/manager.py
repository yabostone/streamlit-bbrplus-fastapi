from commands import AnsibleCommands
from config import AnsibleConfig
from infrastructure import InfrastructureManager
from wsl import WSLExecutor

class AnsibleManager:
    def __init__(self):
        self.wsl = WSLExecutor(timeout=300)
        self.infra = InfrastructureManager()
        self.config = AnsibleConfig()
        self.commands = AnsibleCommands()

    def setup_environment(self):
        tf_output = self.infra.get_terraform_output()
        if not tf_output:
            raise Exception("无法获取实例信息")
        
        tf_output['username'] = 'ubuntu'
        inventory_path = self.infra.create_inventory(tf_output)
        return tf_output, inventory_path

    def run_initialization(self, inventory_path, tf_output):
        playbook_paths = self.config.get_playbook_paths()
        command = self.commands.get_init_command(
            inventory_path, 
            playbook_paths["init"], 
            tf_output['password']
        )
        return self.wsl.execute_ansible(command)

    def install_services(self, inventory_path, playbook_name):
        playbook_paths = self.config.get_playbook_paths()
        print(f"playbook_name: {playbook_name}")
        command = self.commands.get_service_command(
            inventory_path,
            playbook_paths[playbook_name]
        )
        return self.wsl.execute_ansible(command)

    def get_v2ray_info(self, inventory_path):
        command = self.commands.get_v2ray_info_command(inventory_path)
        return self.wsl.execute_ansible(command)

