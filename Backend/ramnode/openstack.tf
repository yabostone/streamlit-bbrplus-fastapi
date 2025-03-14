# 配置 OpenStack Provider
terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
    random = {
      source = "hashicorp/random"
    }
  }
}

# OpenStack Provider 配置
# OpenStack Provider 配置
provider "openstack" {
  auth_url            = var.openstack_auth_url
  user_name           = var.openstack_user_name
  password            = var.openstack_password
  tenant_name         = var.openstack_tenant_name
  tenant_id           = var.openstack_project_id  # 使用 project_id
  region              = var.openstack_region
  
  # 添加额外的认证参数
  user_domain_id      = "default"
  project_domain_id   = "default"
  #endpoint_type       = "publicURL"
  #interface           = "publicURL"

   # 添加 API 版本设置
  #identity_api_version = "3"
  #auth_version         = "3" 
}

# 添加新的变量定义
variable "openstack_project_id" {
  description = "OpenStack Project ID"
  type        = string
  sensitive   = true
}

# 定义变量
variable "openstack_auth_url" {
  description = "OpenStack 认证URL"
  type        = string
}

variable "openstack_user_name" {
  description = "OpenStack 用户名"
  type        = string
}

variable "openstack_password" {
  description = "OpenStack 密码"
  type        = string
}

variable "openstack_tenant_name" {
  description = "OpenStack 项目名称"
  type        = string
}

variable "openstack_region" {
  description = "OpenStack 区域"
  type        = string
}

# 生成随机密码
resource "random_string" "password" {
  length  = 12
  special = false
  upper   = true
  lower   = true
  numeric = true
}

# 创建 OpenStack 实例
resource "openstack_compute_instance_v2" "instance" {
  name            = "openstack-instance"
  image_id        = "c240700e-311a-46a1-9362-87191e709334"  # 需要替换为实际的镜像ID
  flavor_id       = "0bf3ee53-4f19-4a44-84a2-556dcf549362"  # 需要替换为实际的配置ID  MKVM  de66d027-1845-4f3e-9128-20d252dbf48a
  # 1G SKVM 0bf3ee53-4f19-4a44-84a2-556dcf549362   512MB 255c765c-23fb-4fd8-879a-83efff782776  SKVM
  # 1G MKVM e9ec0a3c-7dd0-4cf8-8668-3486050307f6
  admin_pass      = random_string.password.result
  
  # 安全设置
  security_groups = ["all"]
}

output "instance_id" {
  value = openstack_compute_instance_v2.instance.id
}

output "instance_name" {
  value = openstack_compute_instance_v2.instance.name
}

output "instance_status" {
  value = openstack_compute_instance_v2.instance.power_state
}

output "instance_ipv4" {
  value = openstack_compute_instance_v2.instance.access_ip_v4
  description = "实例的IPv4地址"
}

output "instance_ipv6" {
  value = openstack_compute_instance_v2.instance.access_ip_v6
  description = "实例的IPv6地址"
}

output "instance_username" {
  value = "root"  # 或其他默认用户名，取决于您使用的镜像
  description = "实例的默认用户名"
}

output "instance_password" {
  value     = random_string.password.result
  sensitive = true
  description = "实例的管理员密码"
}

output "connection_info" {
  value = {
    ipv4     = openstack_compute_instance_v2.instance.access_ip_v4
    ipv6     = openstack_compute_instance_v2.instance.access_ip_v6
    username = "root"  # 根据实际镜像调整
    password = random_string.password.result
  }
  sensitive = true
  description = "实例的完整连接信息"
}