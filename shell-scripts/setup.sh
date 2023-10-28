#!/bin/sh

#Remember to chmod +x setup.sh

# Update System
sudo apt update
sudo apt upgrade -y

# Install Wireshark
sudo apt install wireshark

# Python Environment
sudo apt-get install libpcap-dev
sudo apt install graphviz
sudo apt install python3-pip  # Corrected package name for pip installation
pip install wheel
pip install matplotlib
pip install pyx
pip install cryptography
pip install scapy
pip install numpy
pip install pandas
pip install scipy
pip install beautifulsoup

# Wireshark User Group (replace 'username' with the actual username)
sudo usermod -a -G wireshark kaihlk

# Add /home/user/.local/bin to PATH (replace 'user' with the actual username)
echo 'export PATH=$PATH:/home/kaihlk/.local/bin' >> ~/.bashrc  # Use 'export' to set PATH

# Clone the Git repository
mkdir ~/git  # Use ~ for the home directory
cd ~/git
git clone https://github.com/kaihlk/covchanfuzzer
cd covchanfuzzer
git init



#Install Dropbox
cd ~ && wget -O - "https://www.dropbox.com/download?plat=lnx.x86_64" | tar xzf -
~/.dropbox-dist/dropboxd
mkdir ~/scripts
wget -O ~/scripts/dropbox.py "https://www.dropbox.com/download?dl=packages/dropbox.py"
chmod +x ~/scripts/dropbox.py
sudo ln -s ~/scripts/dropbox.py /usr/local/bin/dropbox

dropbox login
dropbox start
