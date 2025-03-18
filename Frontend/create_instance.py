#!/bin/env python

## 说明： 使用各个云厂商的服务，创建spot_instance,  尽量价格最低。
## 可以创建windows 的环境，只要注意存储的量不要太大就好。
## 生成标准格式的json。便于后面的ansible等用途。

## 很多应用都可以创建类似的Apps，用于短时间的使用。

import streamlit as st
import os
import subprocess

def main():
    st.title("VPS创建小软件")

    if 'page' not in st.session_state:
        st.session_state.page = 0
    if st.session_state.page == 0:
        page0()
    elif st.session_state.page == 1:
        page1()
    elif st.session_state.page == 2:
        page2()

def page0():

    st.header("检查本地基础环境,关键目的是检查留存记录，哪些被使用了。")
    ## docker 中 安装好 ansible，准备好terraform，pip-boto3,准备好python3.12
    ## 准备好prefect的环境，准备好fastapi/django也可以，就是django配置复杂些。
    st.write("说明：其实在这种小项目的情况下，不需要考虑terraform这种管理状态等复杂操作，使用scw，使用aliyun，使用aws 这种命令就好，进一步封装环境和状态")


    def check_command(command, name):
        try:
            subprocess.run(command, check=True, shell=True, capture_output=True)
            st.success(f"{name} 已安装")
            return True
        except subprocess.CalledProcessError:
            st.error(f"{name} 未安装")
            return False
        except FileNotFoundError:
            st.error(f"{name} 未安装 (命令未找到)")
            return False


    check_command("docker -v", "Docker")
    check_command("ansible --version", "Ansible")
    check_command("terraform -v", "Terraform")
    check_command("python3.12 -c 'import boto3'", "boto3 (Python 3.12)")
    check_command("python3.12 -V", "Python 3.12")

    # 检查 Prefect (假设 Prefect 已通过 pip 安装)
    check_command("python3.12 -c 'import prefect'", "Prefect")

    # 检查 FastAPI (假设 FastAPI 已通过 pip 安装)
    check_command("python3.12 -c 'import fastapi'", "FastAPI")

     # 检查 Django (假设 Django 已通过 pip 安装)
    check_command("python3.12 -c 'import django'", "Django-暂时无影响")
    check_command("openstack --version","openstackclient")
    check_command("scw","scw")
    check_command("aws --version","aws_spotinstance")

    if st.button("开始配置token"):
        st.session_state.page = 1 # 跳转到第二页
        st.rerun() # 重新运行streamlit，以显示第二页  

def page1():
    st.header("选择一个云服务商进行创建")
    st.write("使用多个云厂商，ramnode，scaleway，aliyun-spot，qcloud-spot")
    st.write("上面都是选国外")
    st.write("国内的就是选择aliyun,qcloud")

    # 使用radio按钮来选择区域
    region = st.radio(
        "请选择区域",
        ["国外", "国内"],
        horizontal=True
    )
    
    # 根据区域选择显示不同的云服务商选项
    if region == "国外":
        provider = st.selectbox(
            "请选择云服务商",
            ["ramnode", "scaleway", "aliyun-spot", "qcloud-spot"],
            help="国外区域可用的云服务商"
        )
    else:  # 国内
        provider = st.selectbox(
            "请选择云服务商",
            ["aliyun", "qcloud"],
            help="国内区域可用的云服务商"
        )
    
    # 显示选择的结果
    st.write(f"您选择了: {region} - {provider}")
    
    # 这里可以添加创建实例的具体逻辑
    if st.button("开始创建实例"):
        st.info("创建实例的功能正在开发中...")

def page2():
    pass


if __name__ == "__main__":
    main()
