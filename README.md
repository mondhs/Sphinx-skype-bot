Sphinx-skype-bot
================

Skype integration with sphinx




sudo apt-get install git
sudo apt-get install autoconf libtool automake bison swig python-dev
mkdir sphinx-bot
cd sphinx-bot
git clone https://github.com/mondhs/pocketsphinx
cd pocketsphinx/
cd sphinxbase/
./autogen.sh
make
sudo make install
cd ../pocketsphinx/
./autogen.sh
make
sudo make install
cd ../..

sudo apt-get install libpulse-dev libportaudio-dev
git clone https://github.com/mondhs/espeak
cd espeak/src
make
sudo make install


sudo apt-get install python-setuptools sox
git clone https://github.com/mondhs/skype4py
cd skype4py
sudo python setup.py develop

cd ..
git clone https://github.com/mondhs/lt-pocketsphinx-tutorial/
git clone https://github.com/mondhs/Sphinx-skype-bot


sudo apt-get install skype
echo username password | skype --pipelogin
# agree to control skype bot 
