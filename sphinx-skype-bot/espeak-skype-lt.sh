#!/bin/bash
#Create temp dir
DIR=`mktemp -d`
#call TTS espeak with lithuanian speech
espeak -vlt -w $DIR/tts22kHz.wav "$*" 
# transform from 22 to 16 kHz
sox $DIR/tts22kHz.wav -b 16 $DIR/tts16kHz.wav rate 16000 dither -s
to_mswav.py $DIR/tts16kHz.wav
mv $DIR/tts16kHz-ms.wav /tmp/skype.wav
#delete temp dir
rm -rf "$DIR"

