'''
Created on Mar 8, 2014

@author: as
'''
import os
from pocketsphinx import Decoder
import sphinxbase


class SphinxHelper(object):
    '''
    classdocs
    '''

    #MODELDIR = "../models"
    MODELDIR = "/home/as/src/speech/sphinx/lt-pocketsphinx-tutorial/impl/models"

    decoder = None
    config = None
    previousVadState = 0
    currentVadState = 0

    def __init__(self):
        '''
        Constructor
        '''

    def prepareDecoder(self, pGramma):
        '''
        Initial point where sphinx decoder is initialized or grammar updated
        '''
        if self.decoder is None:
            self.config = self.createConfig(pGramma);
            self.decoder = Decoder(self.config);
        else:
            self.updateGrammar(self.decoder, pGramma);

    def createConfig(self,pGramma):
        '''
        Create configuration with acoustic model path, grammar and dictionary
        '''
        print ("[createConfig]+++")
        config = Decoder.default_config()
        config.set_string('-hmm', os.path.join(self.MODELDIR, 'hmm/lt.cd_cont_200/'))
        config.set_string('-fsg', os.path.join("../resource/", pGramma+'.fsg'))
        #config.set_string('-jsgf', os.path.join("../resource/", pGramma+'.gram'))
        config.set_string('-dict', os.path.join("../resource/", 'service.dict'))
        print ("[createConfig]---")
        return config;

    def updateGrammar(self,pGramma):
        '''
        Update decoder language model from fsg file
        '''
        print ("[updateGrammar]+++" + pGramma)
        logmath = self.decoder.get_logmath();
        fsg = sphinxbase.FsgModel(os.path.join("../resource/", pGramma+'.fsg'), logmath, 7.5)
        #pDecoder.readfile(os.path.join("../resource/", pGramma+'.fsg'), logmath)
        self.decoder.set_fsg("default",fsg);
        self.decoder.set_search("default");
        print ("[updateGrammar]---")

    def startListening(self):
        self.decoder.start_utt(None)


    def stopListening(self):
        self.decoder.end_utt()


    def process_raw(self, data):
        #print("process_raw...\n")
        self.decoder.process_raw(data, False, False)
        self.previousVadState = self.currentVadState
        self.currentVadState = self.decoder.get_vad_state();
        #print("process_raw", self.currentVadState and True, self.previousVadState and True)

    def calculateHypothesis(self):
        return self.decoder.hyp();

    def calculateVadState(self):
        return self.decoder.get_vad_state;

    def isVoiceStarted(self):
        '''
        silence -> speech transition,
        '''
        return self.currentVadState and not self.previousVadState

    def isVoiceEnded(self):
        '''
        speech -> silence transition,
        '''
        return not self.currentVadState and self.previousVadState