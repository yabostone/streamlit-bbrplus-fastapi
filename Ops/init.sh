sudo apt install -y python3
sudo apt install -y python3-pip
sudo apt install -y python3-xyz

###创建虚拟环境
python3 -m venv ./venv

### activate
cd venv/bin/
bash activate
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

./pip3.12 install prefect

## ansible
sudo apt install ansible

## terraform
sudo snap install terraform --classic



