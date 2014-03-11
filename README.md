Sphinx-skype-bot
================

Skype integration with robot Lithuanian language with sphinx and espeak.


### Instructions for Ubuntu 

#### Preconditions for pocketsphinx

    #install git to checkout code
    sudo apt-get install git
    #istall bunch of stuff to compile pocketsphinx
    sudo apt-get install autoconf libtool automake bison swig python-dev

#### Compile pocketsphinx

Compile sphinx base

    mkdir sphinx-bot
    cd sphinx-bot
    git clone https://github.com/mondhs/pocketsphinx
    cd pocketsphinx/
    cd sphinxbase/
    ./autogen.sh
    make
    sudo make install

Compile pocketsphinx

    cd ../pocketsphinx/
    ./autogen.sh
    make
    sudo make install
    cd ../..

#### Compile espeak

    sudo apt-get install libpulse-dev libportaudio-dev
    git clone https://github.com/mondhs/espeak
    cd espeak/src
    make
    sudo make install

#### Compile skype4py

    sudo apt-get install python-setuptools sox
    git clone https://github.com/mondhs/skype4py
    cd skype4py
    sudo python setup.py develop

#### Compile sphinx-skype-bot

    cd ..
    git clone https://github.com/mondhs/lt-pocketsphinx-tutorial/
    git clone https://github.com/mondhs/Sphinx-skype-bot

#### Run skype

    sudo apt-get install skype
    echo username password | skype --pipelogin


### Run Bot

    python sphinx-skype-bot/BotAsrServer.py
    python sphinx-skype-bot/SkypeBot.py
    # agree to control skype bot 


