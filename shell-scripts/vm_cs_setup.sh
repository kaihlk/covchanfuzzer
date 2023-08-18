#Update System
sudo apt update
sudo apt upgrade -y
#Python Environment
sudo apt install python3.8-venv
mkdir covchannfuzzer
sudo install pip
pip install matplotlib
pip install pyx
sudo apt install graphiviz



#Wireshark
supo apt install wireshark

pip install scapy


#sudo apt full-upgrade -y
#sudo apt autoremove -y
#cd ~
#mkdir git/covchanfuzzer
#cd covchanfuzzer
#Install Scapy
#mkdir scapy
#cd scapy
#python3 -m venv ccfuzz 
#source ccfuzz/bin/activate
pip install wheel
pip install  matplotlib
pip install pyx
sudo apt install graphviz
pip install cryptography
#Install Wireshark
sudo apt install wireshark
##yes to dumpcapk



#install anaconda
conda activate env-scapy

conda install  scapy
conda list --export  > requirements.txt
deactivate
cd ~
sudo usermod -a -G wireshark kai
#Install boofuzz

##cd ~/covchanfuzzer
##mkdir boofuzz
##cd boofuzz
##python3 -m venv boofuzz-env 
conda activate env-boofuzz
conda install boofuzz
pip freezeconda list --export  > requirements.txt
deactivate
cd ~

