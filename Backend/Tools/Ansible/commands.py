class AnsibleCommands:
    @staticmethod
    def get_init_command(inventory_path, playbook_path, password):
        extra_vars = f"ansible_sudo_pass={password}"
        return f'ansible-playbook -i {inventory_path} {playbook_path} --extra-vars "{extra_vars}"'
    
    @staticmethod
    def get_service_command(inventory_path, playbook_path):
        return f'ansible-playbook -i {inventory_path} {playbook_path}'
    
    @staticmethod
    def get_v2ray_info_command(inventory_path):
        return f'ansible all -i {inventory_path} -m shell -a "docker exec v2ray bash -c \'v2ray info\'"'
        