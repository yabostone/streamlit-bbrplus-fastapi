import streamlit as st
import os
import subprocess

def main():
    st.title("隧道创建小软件")

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
    st.header("页面 1: VPS 信息上传")
    st.write("这是一个用于创建 tunnel 隧道的 docker 小软件。")
    st.write("目前只支持 OpenStack-ramnode 虚拟机。请确保您已准备好 OpenStack 配置文件，并放置到指定位置。")
    st.write("这是需要准备rc文件。并且放置在docker指定的位置,当然也可以选择使用terraform，那么准备好相关额链接就好")
    st.subheader("上传 OpenStack 配置文件")
    uploaded_file = st.file_uploader("选择一个 OpenStack RC 文件", type=["sh", "rc"]) # 假设是 shell 脚本文件
    if uploaded_file is not None:
        # 指定保存路径
        save_path = os.path.expanduser("~/.openstack/openrc")

        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # 保存文件
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"文件已保存到 {save_path}")        

    # 虚拟机位置选择 (目前只支持 OpenStack)
    st.subheader("选择虚拟机位置")
    vm_location = st.selectbox("虚拟机位置", ["OpenStack"]) # 可以在这里添加更多选项

    if vm_location == "OpenStack":
        st.info("您选择了 OpenStack 虚拟机。")
        # 这里可以添加 OpenStack 配置文件的上传或选择功能

    if st.button("开始部署"):
        st.session_state.page = 2 # 跳转到第二页
        st.rerun() # 重新运行streamlit，以显示第二页


def page2():
    st.header("页面 2: V2Ray 安装")
    st.write("此页面用于配置和安装 V2Ray。")

    st.subheader("V2Ray 配置")
    use_bbrplus = st.checkbox("配置 BBRplus (用于更大流量的应用)")
    st.write("这个操作可能失败，同时可能耗时极长，需要注意定时检测是否成功")

    if st.button("开始安装 V2Ray"):
        st.write("正在安装 V2Ray...")
        # 这里可以添加 V2Ray 安装的逻辑
        if use_bbrplus:
            st.write("已选择配置 BBRplus。")
            # 添加 BBRplus 配置逻辑
        st.subheader("准备开始连接并且进行v2ray的安装")
        st.success("V2Ray 安装完成！")
        st.subheader("V2Ray 链接")
        # 这里可以输出 V2Ray 链接，可以是多个
        st.code("v2ray://your_v2ray_link_1", language="text")
        st.code("v2ray://your_v2ray_link_2", language="text") # 可以添加更多链接
        st.subheader("V2ray订阅链接")
        st.code("这里是订阅链接的内容")

if __name__ == "__main__":
    main()