import SocketServer
import subprocess
import time
import os
from SphinxWrapper import SphinxWrapper
from Artificialintelligence import Artificialintelligence
import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.info("Skypebot ASR up and running", )

class BotAsrServer(SocketServer.BaseRequestHandler):
    exitapp = False
    CHUNK = 4096
    TTS_PATH = "./espeak-skype-lt.sh"
    #TTS_PATH = "/home/as/bin/tts-skype-lt"

    ai = Artificialintelligence()

    lockFile = "/tmp/skype.wav"
    killFile = "/tmp/killDialog.txt"



    def handle(self):
        """
        The RequestHandler class for our server.

        It is instantiated once per connection to the server, and must
        override the handle() method to implement communication to the
        client.
        """
        # self.request is the TCP socket connected to the client
        print "[handle]+++";


        #Create Sphinx instance
        sphinxWrapper = SphinxWrapper()
        #Initialize Sphinx with "code" grammar
        sphinxWrapper.prepareDecoder("code")
        #Initialize Artificial Intelligence context
        aiContext = self.ai.createContext();
        # invoke AI engine for the first time: welcome
        self.processAsrText(aiContext, None);
        # start waiting for speech segment
        sphinxWrapper.startListening()

        while True:
            #read skype data from socket in chunks
            data = self.request.recv(self.CHUNK)
            # skype does not sending data, stop listening
            if not data: break

            # do not need procced to fast. each 100ms is enough. Data buffering is organized in socket logic
            time.sleep (0.100)

        # feed received data to sphinx decoder
            sphinxWrapper.process_raw(data)
        # speech segment found.
            if sphinxWrapper.isVoiceStarted():
            #silence -> speech transition,
            #let user know that we heard
            logging.info("Listening...\n")
        # speech segment endend
            if sphinxWrapper.isVoiceEnded():
            logging.info("Recognised...\n")
            #speech -> silence transition,
            #time to start new utterance
                sphinxWrapper.stopListening();
                hypothesis = sphinxWrapper.calculateHypothesis();
            if hypothesis is not None:
                logging.info ('Best hypothesis: %s %s %s', hypothesis.uttid, hypothesis.best_score, hypothesis.hypstr)
                # get text from ASR in U
                messageSaid = hypothesis.hypstr.decode('utf-8')
                # feed ASR text to AI
                    if self.processAsrText(aiContext, messageSaid) is None:
                        break;
                    if aiContext.state == aiContext.STATE_THANKS:
                    with open(self.killFile, 'a') as the_file:
                        the_file.write('Bye\n')
                    if aiContext.state in aiContext.GRAM:
                    # if state is bound to grammar update ASR
                        sphinxWrapper.updateGrammar(aiContext.GRAM[aiContext.state])
                sphinxWrapper.startListening()


        logging.info("[handle]---");

    def finish(self):
        print('{} disconnected'.format(*self.client_address))
        #with open(self.killFile, 'a') as the_file:
        #    the_file.write('Bye\n')

    def processAsrText(self, aiContext, message):
        '''
        Process what was said by AI and announce response
        '''
        logging.info ("[said]+++ %s", message)

        aiContext = self.ai.onMessageSaid(message, aiContext)
        print ('AI response: ',  aiContext.state, aiContext.response)


        self.geneareSpeechResponse(aiContext.response)
        if aiContext.state == aiContext.STATE_FINISH:
            with open(self.killFile, 'a') as the_file:
                the_file.write('Bye\n')
            return None
        if aiContext.interactiveStep is False :
            self.processAsrText(aiContext, message);
        logging.info ("[said]--- %s", message)
        return aiContext

    def geneareSpeechResponse(self, text):
        '''
        Invoke text-to-speech to generate wav file
        '''
        logging.info("geneareSpeechResponse+++ '%s'", text)
        #Invoke command file text-to-speech to generate Lithuanian language response for skype
        generateCommand = ["/home/as/bin/tts-skype-lt", text]
        logging.info("[geneareSpeechResponse] generateCommand: %s", generateCommand)
        p = subprocess.Popen(generateCommand, stdout=subprocess.PIPE)
        #wait till it is generated
        generateFile = p.stdout.readline().rstrip()
        logging.info("[geneareSpeechResponse] generateFile '%s'", generateFile)
        #we have things to say. Does not listen
        logging.info ("[geneareSpeechResponse] lock exists %s", os.path.exists(self.lockFile))
        #wait till skype will announce the fail to user
        while os.path.exists(self.lockFile):
            time.sleep(.100)
            logging.info ("[geneareSpeechResponse] lock not exists %s", os.path.exists(self.lockFile))
        time.sleep(.100)


        logging.info("geneareSpeechResponse--- '%s'", text)


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    print ("Started", HOST, PORT)
        # Create the server, binding to localhost on port 8080
        server = SocketServer.TCPServer((HOST, PORT), BotAsrServer)

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
