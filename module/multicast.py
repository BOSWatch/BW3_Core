#!/usr/bin/python
# -*- coding: utf-8 -*-
"""!
    ____  ____  ______       __      __       __       _____
   / __ )/ __ \/ ___/ |     / /___ _/ /______/ /_     |__  /
  / __  / / / /\__ \| | /| / / __ `/ __/ ___/ __ \     /_ <
 / /_/ / /_/ /___/ /| |/ |/ / /_/ / /_/ /__/ / / /   ___/ /
/_____/\____//____/ |__/|__/\__,_/\__/\___/_/ /_/   /____/
                German BOS Information Script
                     by Bastian Schroll

@file:        multicast.py
@date:        02.05.2021
@author:      Thierry Fredrich
@description: Implements multicast alarms

structure of a multicast alarm 
# 1 ) network delimiter without text 
# 2 ) alarm ric without text 
# 3 ) text ric with message 
# 4 ) network delimiter ric message <BS>
"""
import logging
from module.moduleBase import ModuleBase


logging.debug("- %s loaded", __name__)


class BoswatchModule(ModuleBase):
    """!Description of the Module"""
    # initializing with empty list
    
    textRics = []
    delimiterRic = 42
    delimiterSubric = 42
    ignoreTime = 42
    ### to be cleared
    receivedAlarmRic = 42
    receivedAlarmSubric = 42
    bufferListFormingAMulticastAlarm = []
    initialDelimiterReceived = False
    alarmReceived = False
    textRicReceived = False
    textRicMessage = ''
    def initStorage(self):
        self.receivedAlarmRic = 42
        self.receivedAlarmSubric = 42
        self.bufferListFormingAMulticastAlarm = []
        self.initialDelimiterReceived = False
        self.alarmReceived = False
        self.textRicReceived = False
        self.textRicMessage = ''
    
    def __init__(self, config):
        """!Do not change anything here!"""
        super().__init__(__name__, config)  # you can access the config class on 'self.config'
        logging.debug("starting multicast module")
        logging.debug("multicastAlarm_delimiterRic is: %i" % self.config.get("multicastAlarm_delimiterRic"))
        logging.debug("multicastAlarm_delimiterSubric is: %i" % self.config.get("multicastAlarm_delimiterSubric"))
        logging.debug("multicastAlarm_ignore_time is: %i" % self.config.get("multicastAlarm_ignore_time"))
        logging.debug("multicastAlarm_textRics is: %s" % self.config.get("multicastAlarm_textRics"))
        self.delimiterRic = int(self.config.get("multicastAlarm_delimiterRic"))
        self.delimiterSubric = int(self.config.get("multicastAlarm_delimiterSubric"))
        self.ignoreTime = int(self.config.get("multicastAlarm_ignore_time"))
        for aTextRic in self.config.get("multicastAlarm_textRics").split(','):
            self.textRics.append(int(aTextRic))
        self.initStorage()

    def onLoad(self):
        """!Called by import of the plugin
        Remove if not implemented"""
        pass

    def doWork(self, bwPacket):
        """!start an run of the module.

        @param bwPacket: A BOSWatch packet instance"""
        thisRic = int(bwPacket.get("ric"))
        thisSubric = int(bwPacket.get("subric"))-1
        thisMessage = bwPacket.get("message")
        if bwPacket.get("mode") == "pocsag":
            pass
        else:
            logging.error("multicast module only works with pocsag")
            raise NameError('multicast module only works with pocsag')
        
        '''delimiter received'''
        if self.delimiterRic == thisRic and self.delimiterSubric == thisSubric:
            ''' is it the initial delimiter?'''
            if not self.initialDelimiterReceived and \
            not self.alarmReceived and \
            not self.textRicReceived:
                self.bufferListFormingAMulticastAlarm.append(bwPacket)
                self.initialDelimiterReceived = True
                return False
            ''' is it the closeing delimiter?'''
            if self.initialDelimiterReceived and \
            self.alarmReceived and self.textRicReceived:
                self.bufferListFormingAMulticastAlarm.append(bwPacket) # deliting list here?
                logging.debug("modify bwPacket" )
                bwPacket.set('message',self.textRicMessage)
                #bwPacket.update({'message':'bla'})
                logging.debug("multicast completed... clearing storage")
                self.initStorage()
                return bwPacket

        '''alarm ric recceived'''
        if thisRic != self.delimiterRic and thisRic not in self.textRics:
            if self.initialDelimiterReceived:
                self.bufferListFormingAMulticastAlarm.append(bwPacket)
                self.receivedAlarmRic = thisRic
                self.receivedAlarmSubric = thisSubric
                logging.debug("hoping %i is a valid alarm ric" % thisRic)
                logging.debug("with subric %i " % thisSubric)
                self.alarmReceived = True
                return False
        
        '''text ric received''' 
        if thisRic in self.textRics:
            if self.initialDelimiterReceived and self.alarmReceived:
                self.bufferListFormingAMulticastAlarm.append(bwPacket)
                self.textRicReceived = True
                self.textRicMessage = thisMessage
                logging.debug("multicast text is: %s" % thisMessage )
                return False
        return False

    def onUnload(self):
        """!Called by destruction of the plugin
        Remove if not implemented"""
        pass
        
