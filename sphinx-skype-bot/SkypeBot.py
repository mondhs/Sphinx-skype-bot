#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Skype Auto Answer is to Answer the Skype incoming call automatically

Base on:
http://code.google.com/p/skypeautoanswer/source/browse/trunk/SkypeRecv.py?r=2
https://code.google.com/p/mindcollapse-com-blog-source/source/browse/small_projects/SkypeBot/__init__.py

auto run skype: echo username password | skype --pipelogin

@license: GPL License (see the accompanying LICENSE file for more information)


'''
import os
import subprocess
import time
import Skype4Py
import logging as logging





class SkypeBot:

    Skype = None # Skype4Py
    lockFile = "/tmp/skype.wav"
    killFile = "/tmp/killDialog.txt"

    def __init__(self):
        self.Skype = Skype4Py.Skype()
        self.Skype.Attach()
        logging.getLogger('Skype4Py').setLevel(logging.INFO)
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.info("Skypebot connected with login %s", self.Skype.CurrentUser.Handle)
        self.Skype.OnAttachmentStatus = self.AttachmentStatus
        self.Skype.OnMessageStatus = self.MessageStatus
        self.Skype.OnCallStatus = self.CallStatus
        self.Skype.OnCallInputStatusChanged = self.CallInputStatusChanged


    def MessageStatus(self, Message, Status):
        """ Event handler for Skype chats """
        logging.info("Message Status %s", Status)
        if Status == Skype4Py.cmsSent:
            # iteration trough Message.Users does not work here for unknown reasons
            # that is we are using chat members loop
            for User in Message.Chat.Members:
                if not User == self.Skype.CurrentUser:
                    logging.info("Message '%s' was sent to user %s", Message.Body, User.Handle)
        elif Status == Skype4Py.cmsReceived:
            logging.info("Message '%s' received from user %s", Message.Body, Message.FromHandle)
            Message.MarkAsSeen()
            self.ProcessMessage(Message)

    def ProcessMessage(self, Message):
        """ Process chat message """
        # if we don't know buddy's name - take it from Skype Profile
        #if self.AI.getPredicate("name", Message.FromHandle) == "":
        #    self.AI.setPredicate("name", Message.FromDisplayName, Message.FromHandle)
        #Message.Chat.SendMessage(self.AI.respond(Message.Body, Message.FromHandle))
        Message.Chat.SendMessage("Labas")



    def CallInputStatusChanged(self, Call, Active):
        """ Unset output file after it finished playing """
        logging.info("CallInputStatusChanged '%s'", Active)
        if not Active:
            Call.InputDevice(Skype4Py.callIoDeviceTypeFile, None)

    def CallStatus(self, Call, Status):
        """ Event handler for Skype calls """
        logging.info("CallStatus '%s'", Status)
        if Status == Skype4Py.clsRinging:
            #time.sleep(1)
            Call.Answer()
        elif Status == Skype4Py.clsInProgress:
            self.ProcessCall(Call)
        elif Status == Skype4Py.clsFinished:
            self.Skype.SendMessage(Call.PartnerHandle, "Dėkui")

    def ProcessCall(self, Call):
        """ Process call and emulate conversation """
        Call.MarkAsSeen()
        logging.info("ProcessCall '%s'", Call)
        #self.SayByVoice(Call, "Labas")
        # record wav file with buddy's speech
        #TemporaryFileWAV = tempfile.NamedTemporaryFile(prefix= Call.PartnerHandle +"_record_", suffix=".wav", delete=False)
        #logging.info("TemporaryFileWAV.name '%s'", TemporaryFileWAV.name)
        #TemporaryFileWAV.close()
        #Call.OutputDevice(Skype4Py.callIoDeviceTypeFile, TemporaryFileWAV.name)

        Call.OutputDevice(Skype4Py.callIoDeviceTypePort, "8080")

        while True:
            time.sleep(.100)
            if os.path.exists(self.killFile):
                logging.info("[ProcessCall] kill file exist. Bye!")
                os.remove(self.killFile);
                break;
            if os.path.exists(self.lockFile):
                Call.InputDevice(Skype4Py.callIoDeviceTypeFile, self.lockFile)
                logging.info("Saying+++")
                # pause thread execution while bot is speaking
                while not Call.InputDevice(Skype4Py.callIoDeviceTypeFile) == None:
                    time.sleep(.100)
                logging.info("Saying---")
                #release lock
                os.remove(self.lockFile);

        # terminate speech recording
        #self.SayByVoice(Call, "Viso gero")
        Call.OutputDevice(Skype4Py.callIoDeviceTypePort, None)
        time.sleep(1)
        Call.Finish()


    def SayByVoice(self, Call, Text):
        # output file to buddy's ears
        logging.info("SayByVoice+++ '%s'", Text)
        logging.info("SayByVoice+++ InputDevice()'%s'", Call.InputDevice())

        generateCommand = ["/home/as/bin/tts-win-lt", Text]
        logging.info("[SayByVoice] generateCommand: %s", generateCommand)
        #subprocess.call(ConvertCommand)
        p = subprocess.Popen(generateCommand, stdout=subprocess.PIPE)
        generateFile = p.stdout.readline().rstrip()
        #generateFile = p.communicate()[0]
        #Call.InputDevice(Skype4Py.callIoDeviceTypeFile, "/tmp/tmp.EyuEMu1vFp/0.wav")
        logging.info("[SayByVoice] generateFile '%s'", generateFile)
        Call.InputDevice(Skype4Py.callIoDeviceTypeFile, generateFile)

        # pause thread execution while bot is speaking
        while not Call.InputDevice(Skype4Py.callIoDeviceTypeFile) == None:
            time.sleep(1)
        logging.info("SayByVoice--- '%s'", Text)


    def AttachmentStatus(self, status):
        print '7. API attachment status:'+self.Skype.Convert.AttachmentStatusToText(status)
        if status == Skype4Py.apiAttachAvailable:
            self.Skype.Attach()



if __name__ == "__main__":
    skypeBot = SkypeBot()


    while 1:
        time.sleep(1)
