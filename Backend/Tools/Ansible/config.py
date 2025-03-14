import os
from dataclasses import dataclass
from typing import Optional

class AnsibleConfig:

    inventory_template: str = """
    [local]
    localhost ansible_connection=local ansible_python_interpreter=/usr/bin/python3
    
    [all]
    {public_ip} ansible_user={username} ansible_password={password} \
    ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' \
    ansible_sudo_pass={password}
    """

    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        
    def get_playbook_paths(self):
        return {
            'init': os.path.abspath(os.path.join(self.base_path, "playbooks", "00_init.yaml")),
            'docker': os.path.abspath(os.path.join(self.base_path, "playbooks", "10_install_docker.yaml")),
            'v2ray': os.path.abspath(os.path.join(self.base_path, "playbooks", "12_install_v2ray.yaml")),
            'kernel': os.path.abspath(os.path.join(self.base_path, "playbooks", "22_setup_kernel.yaml"))
        }
    
    def get_inventory_template(self, tf_output: dict) -> str:
        return self.inventory_template.format(**tf_output)