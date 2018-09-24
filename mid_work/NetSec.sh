mkdir /tmp/NetSec
cd /tmp/NetSec
virtualenv -p python3 PyEnv
./PyEnv/bin/pip3 install pandas
./PyEnv/bin/pip3 install dnsPython
git init
git clone https://github.cs.huji.ac.il/tomn96/ProjectDNS.git
git checkout feature/dns
