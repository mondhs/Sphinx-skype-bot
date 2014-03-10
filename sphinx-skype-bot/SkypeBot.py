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
            Call.Answer()
        elif Status == Skype4Py.clsInProgress:
            self.ProcessCall(Call)
        elif Status == Skype4Py.clsFinished:
            self.Skype.SendMessage(Call.PartnerHandle, "Dėkui")

    def ProcessCall(self, Call):
        """ Process call and emulate conversation """
        Call.MarkAsSeen()
        logging.info("ProcessCall '%s'", Call)
        #Send audio stream to 8080 port of localhost.
        Call.OutputDevice(Skype4Py.callIoDeviceTypePort, "8080")
        # eternal cycle for monitoring AI work in background
        while True:
            time.sleep(.100)
            #if AI created this file thats mean conversation should be ended
            if os.path.exists(self.killFile):
                #release lock and finish conversation
                logging.info("[ProcessCall] kill file exist. Bye!")
                os.remove(self.killFile);
                break;
            # if AI TTS created this wav file thats mean we need playback to user
            if os.path.exists(self.lockFile):
                # set file as playback in skype
                Call.InputDevice(Skype4Py.callIoDeviceTypeFile, self.lockFile)
                logging.info("Saying+++")
                # pause thread execution while bot is speaking
                while not Call.InputDevice(Skype4Py.callIoDeviceTypeFile) == None:
                    time.sleep(.100)
                logging.info("Saying---")
                #release lock
                os.remove(self.lockFile);

        # terminate speech recording
        Call.OutputDevice(Skype4Py.callIoDeviceTypePort, None)
        time.sleep(3)
        Call.Finish()



    def AttachmentStatus(self, status):
        print '7. API attachment status:'+self.Skype.Convert.AttachmentStatusToText(status)
        if status == Skype4Py.apiAttachAvailable:
            self.Skype.Attach()



if __name__ == "__main__":
    skypeBot = SkypeBot()

    while 1:
            time.sleep(1)
