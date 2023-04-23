#Update System
sudo apt update
sudo apt upgrade -y
sudo apt full-upgrade -y
sudo apt autoremove -y
#cd ~
#mkdir covchanfuzzer
#cd covchanfuzzer
#Install Scapy
#mkdir scapy
#cd scapy
#python3 -m venv scapy-env 
#source scapy-env/bin/activate

#install anaconda
conda activate env-scapy

conda install  matplotlib
conda install pyx
sudo apt install graphviz
conda install cryptograpy
conda install  scapy
conda list --export  > requirements.txt
deactivate
cd ~
#Install Wireshark
sudo apt install wireshark
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

