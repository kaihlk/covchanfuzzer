#Update System
sudo apt update
sudo apt upgrade -y
sudo apt full-upgrade -y
sudo apt autoremove -y
cd ~
mkdir covchanfuzzer
cd covchanfuzzer
#Install Scapy
mkdir scapy
cd scapy
python3 -m venv scapy-env 
source scapy-env/bin/activate
pip install -U  matplotlib
pip install -U pyx
sudo apt install graphviz
pip install -U cryptograpy
pip install -U scapy
pip freeze > requirements.txt
deactivate
cd ~
#Install Wireshark
sudo apt install wireshark
sudo usermod -a -G wireshark kai
#Install boofuzz
cd ~/covchanfuzzer
mkdir boofuzz
cd boofuzz
python3 -m venv boofuzz-env 
source boofuzz-env/bin/activate
pip install -U boofuzz
pip freeze > requirements.txt
deactivate
cd ~

