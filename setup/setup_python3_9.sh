version=3.9.5

mkdir ~/temp
wget -O ~/temp/Python-$version.tar.xz https://www.python.org/ftp/python/$version/Python-$version.tar.xz

cd ~/temp

tar xf Python-$version.tar.xz

cd Python-$version

./configure --enable-optimizations --enable-shared
make -j -l 4

sudo make altinstall
sudo ldconfig

echo add "alias python3=/usr/local/bin/python3.9" to bashrc
