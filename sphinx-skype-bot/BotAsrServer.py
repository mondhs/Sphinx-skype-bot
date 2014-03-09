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

    CHUNK = 4096
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

        sphinxWrapper = SphinxWrapper()
        sphinxWrapper.prepareDecoder("code")
        aiContext = self.ai.createContext();
        self.said(aiContext, None);

        #print "{} wrote:".format(self.client_address[0])

        sphinxWrapper.startListening()

        while True:
            data = self.request.recv(self.CHUNK)
            if not data: break
            time.sleep (0.100)

            sphinxWrapper.process_raw(data)
            if sphinxWrapper.isVoiceStarted():
                #silence -> speech transition,
                #let user know that we heard
                print("Listening...\n")
            #if not vad_state and cur_vad_state:
            if sphinxWrapper.isVoiceEnded():
                print("Recognised...\n")
                #speech -> silence transition,
                #time to start new utterance
                sphinxWrapper.stopListening();
                hypothesis = sphinxWrapper.calculateHypothesis();
                if hypothesis is not None:
                    print ('Best hypothesis: ', hypothesis.uttid, hypothesis.best_score, hypothesis.hypstr)
                    logging.info ('Best hypothesis: %s %s %s', hypothesis.uttid, hypothesis.best_score, hypothesis.hypstr)
                    saidText = hypothesis.hypstr.decode('utf-8')
                    if self.said(aiContext, saidText) is None:
                        break;
                    if aiContext.state == aiContext.STATE_THANKS:
                        with open(self.killFile, 'a') as the_file:
                            the_file.write('Bye\n')
                    if aiContext.state in aiContext.GRAM:
                        sphinxWrapper.updateGrammar(aiContext.GRAM[aiContext.state])
                sphinxWrapper.startListening()


        logging.info("[handle]---");

    def finish(self):
        print('{} disconnected'.format(*self.client_address))
        #with open(self.killFile, 'a') as the_file:
        #    the_file.write('Bye\n')

    def said(self, aiContext, text):
        '''
        Process what was said by AI and announce response
        '''
        logging.info ("[said]+++ %s", text)

        aiContext = self.ai.said(text, aiContext)
        print ('AI response: ',  aiContext.state, aiContext.response)

        self.speak(aiContext.response)
        if aiContext.state == aiContext.STATE_FINISH:
            with open(self.killFile, 'a') as the_file:
                the_file.write('Bye\n')
            return None
        if aiContext.interactiveStep is False :
            self.said(aiContext, text);
        logging.info ("[said]--- %s", text)
        return aiContext

    def speak(self, text):
        # output file to buddy's ears
        logging.info("SayByVoice+++ '%s'", text)
        generateCommand = ["/home/as/bin/tts-win-lt", text]
        logging.info("[SayByVoice] generateCommand: %s", generateCommand)
        p = subprocess.Popen(generateCommand, stdout=subprocess.PIPE)
        generateFile = p.stdout.readline().rstrip()
        logging.info("[SayByVoice] generateFile '%s'", generateFile)
                    #we have things to say. Does not listen
        logging.info ("[speak] lock exists %s", os.path.exists(self.lockFile))
        while os.path.exists(self.lockFile):
            time.sleep(.100)
        logging.info ("[speak] lock not exists %s", os.path.exists(self.lockFile))
        time.sleep(.100)

        logging.info("SayByVoice--- '%s'", text)


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    print ("Started", HOST, PORT)

    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), BotAsrServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()