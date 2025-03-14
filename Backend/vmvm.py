from fastapi import FastAPI, HTTPException
import subprocess
import json
import time
import os
from pydantic import BaseModel

app = FastAPI()

class VMCreateRequest(BaseModel):
    server_name: str
    image_name: str
    flavor_name: str
    security_group_name: str
    password: str
    rc_file_path: str

class IPResponse(BaseModel):
    ip_address: str

class InventoryResponse(BaseModel):
    inventory_path: str



class ConnectionResponse(BaseModel):
    ipv4: str
    ipv6: str
    password: str
    username: str

class VMInfo(BaseModel):
    id: str
    name: str
    status: str
    ipv4: str = None  # 允许 IPv4 地址为空
    ipv6: str = None

class PingResponse(BaseModel):
    reachable: bool

def run_command(command):
    """运行 shell 命令并返回输出、错误和返回码"""
    try:
        process = subprocess.run(["bash","-c",command], check=True, capture_output=True, text=True)
        return process.stdout, process.stderr, process.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode
    except FileNotFoundError:
        return "", "Command not found", 127 # 127 通常表示命令未找到

@app.get("/openstack/terraform/list_vms/", response_model=ConnectionResponse)
async def list_vms():
    """列出由 Terraform 创建的虚拟机"""
    os.chdir("./ramnode")
    # 获取 Terraform 状态
    state_command = "terraform output -json connection_info"
    state_stdout, state_stderr, state_returncode = run_command(state_command)
    print(state_stdout)
    if state_returncode != 0:
        raise HTTPException(status_code=500, detail=f"获取 Terraform 状态失败: {state_stderr}")

    return json.loads(state_stdout)


@app.post("/openstack/terraform/create_vm/", response_model=ConnectionResponse)
async def create_vm(vm_request: VMCreateRequest):
    """创建 OpenStack 虚拟机并返回 IP 地址，使用 Terraform"""
    # 切换到包含 openstack.tf 的目录
    os.chdir("./ramnode")

    # 初始化 Terraform (如果需要)
    init_stdout, init_stderr, init_returncode = run_command("terraform init")
    if init_returncode != 0:
        raise HTTPException(status_code=500, detail=f"Terraform 初始化失败: {init_stderr}")
    plan_command = (
        f"terraform plan  "
        f" -var-file=openstack.tfvars  "
        )

    # 使用传入的参数构建 apply 命令
    apply_command = (
        f"terraform apply -auto-approve "
        f" -var-file=openstack.tfvars  "
    )
    plan_stdout, plan_stderr , plan_returncode = run_command(plan_command)
    apply_stdout, apply_stderr, apply_returncode = run_command(apply_command)

    if apply_returncode != 0:
        raise HTTPException(status_code=500, detail=f"Terraform 应用失败: {apply_stderr}")

    # 获取 Terraform 输出中的 IP 地址
    connection_info_command = "terraform output -json connection_info"
#{"ipv4":"168.235.104.4","ipv6":"[2604:180:f4::7a]","password":")r#=IN5tRMyZ","username":"root"}
    count = 0
    while True:
        count+=1 
        output_stdout, output_stderr, output_returncode = run_command(connection_info_command)

        if output_returncode != 0:
            raise HTTPException(status_code=500, detail=f"获取IP地址失败: {output_stderr}")

        try:
            connection_info = json.loads(output_stdout)
            ip_address = connection_info.get("ipv4")
            if ip_address:
                return connection_info

        except json.JSONDecodeError:
            pass  # 解析失败，继续循环

        time.sleep(5)  # 等待5秒
        if count >= 15:
            break

@app.post("/openstack/create_vm/", response_model=IPResponse)
async def create_vm(vm_request: VMCreateRequest):
    """创建 OpenStack 虚拟机并返回 IP 地址，，，目前的环境问题，先放一下"""
    # 构建 OpenStackClient 命令
    command = (
        f"source {vm_request.rc_file_path} && "
        f"openstack server create "
        f"--image {vm_request.image_name} "
        f"--flavor {vm_request.flavor_name} "
        f"--security-group {vm_request.security_group_name} "
        f"--password {vm_request.password} "
        f"{vm_request.server_name} --wait -f json" #wait等待创建完成，json返回创建信息
    )

    stdout, stderr, returncode = run_command(command)

    if returncode != 0:
        raise HTTPException(status_code=500, detail=f"虚拟机创建失败: {stderr}")

    # 解析创建好的虚拟机的输出，拿到ip地址。
    try:
        server_info = json.loads(stdout)
        for network_name, addresses in server_info["addresses"].items():
            for addr in addresses:
                if addr["version"] == 4:
                    ip_address = addr["addr"]
                    return {"ip_address": ip_address}
    except (json.JSONDecodeError, KeyError) as e:
        raise HTTPException(status_code=500, detail=f"解析虚拟机信息失败: {str(e)}")

    raise HTTPException(status_code=500, detail="无法获取虚拟机 IP 地址")

@app.post("/ansible/gen_inventory/",response_model=InventoryResponse)
## 不使用jinja，和template，然后在api中直接生成inventory_ini的信息
## 这里的内容需要有输入，输入就是ConnectionResponse
@app.post("/ansible/gen_inventory/",response_model=InventoryResponse)
## 不使用jinja，和template，然后在api中直接生成inventory_ini的信息
## 这里的内容需要有输入，输入就是ConnectionResponse
async def gen_inventory(conn_response: ConnectionResponse):

    local_inventory_content = f"""[local]
localhost ansible_connection=local ansible_python_interpreter=/usr/bin/python3

[tunnel]
{conn_response.ipv4} ansible_user={conn_response.username} ansible_password="{conn_response.password}" ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' ansible_sudo_pass="{conn_response.password}"
"""
    # 确定inventory文件的路径
    inventory_path = "./inventory.ini"
    inventory_path = os.path.join(os.getcwd(),"inventory.ini")
    # 将内容写入文件
    with open(inventory_path, "w") as f:
        f.write(local_inventory_content)

    inventoryRes = {"inventory_path": inventory_path}
    return inventoryRes

@app.get("/get_ip/{server_name}", response_model=IPResponse)
async def get_server_ip(server_name: str, rc_file_path: str):
    """获取指定虚拟机的 IP 地址"""
    command = f"source {rc_file_path} && openstack server show {server_name} -f json"
    stdout, stderr, returncode = run_command(command)

    if returncode != 0:
        raise HTTPException(status_code=500, detail=f"获取 IP 地址失败: {stderr}")

    try:
        server_info = json.loads(stdout)
        for network_name, addresses in server_info["addresses"].items():
            for addr in addresses:
                if addr["version"] == 4:
                    return {"ip_address": addr["addr"]}
    except (json.JSONDecodeError, KeyError) as e:
        raise HTTPException(status_code=500, detail=f"解析虚拟机信息失败: {str(e)}")

    raise HTTPException(status_code=404, detail="未找到虚拟机或 IP 地址")

@app.get("/ping/{ip_address}", response_model=PingResponse)
async def ping_ip(ip_address: str):
    """检查指定的 IP 地址是否可达"""
    command = ["ping", "-c", "3", ip_address]
    stdout, stderr, returncode = run_command(" ".join(command)) #这里不能使用shell=true

    if returncode == 0:
        return {"reachable": True}
    else:
        return {"reachable": False}
