import SocketServer
import time
from SphinxHelper import SphinxHelper

class MyTCPHandler(SocketServer.BaseRequestHandler):

    CHUNK = 4096

    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        print "[handle]+++";
        sphinxHelper = SphinxHelper()
        sphinxHelper.prepareDecoder("code")

        #print "{} wrote:".format(self.client_address[0])

        sphinxHelper.startListening()

        while True:
            data = self.request.recv(self.CHUNK)
            if not data: break
            time.sleep (0.100)
            sphinxHelper.process_raw(data)
            if sphinxHelper.isVoiceStarted():
                #silence -> speech transition,
                #let user know that we heard
                print("Listening...\n")
            #if not vad_state and cur_vad_state:
            if sphinxHelper.isVoiceEnded():
                print("Recognised...\n")
                #speech -> silence transition,
                #time to start new utterance
                sphinxHelper.stopListening();
                hypothesis = sphinxHelper.calculateHypothesis();
                if hypothesis is not None:
                    print ('Best hypothesis: ', hypothesis.uttid, hypothesis.best_score, hypothesis.hypstr)
                sphinxHelper.startListening()


        print "[handle]---";

    def finish(self):
        print('{}:{} disconnected'.format(*self.client_address))




if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    print ("Started", HOST, PORT)

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()