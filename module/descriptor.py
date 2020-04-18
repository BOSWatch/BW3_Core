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

@file:        descriptor.py
@date:        27.10.2019
@author:      Bastian Schroll
@description: Module to add descriptions to bwPackets
"""
import logging
from module.moduleBase import ModuleBase

# ###################### #
# Custom plugin includes #

# ###################### #

logging.debug("- %s loaded", __name__)


class BoswatchModule(ModuleBase):
    """!Adds descriptions to bwPackets"""
    def __init__(self, config):
        """!Do not change anything here!"""
        super().__init__(__name__, config)  # you can access the config class on 'self.config'

    def onLoad(self):
        """!Called by import of the plugin"""
        for descriptor in self.config:
            if descriptor.get("wildcard", default=None):
                self.registerWildcard(descriptor.get("wildcard"), descriptor.get("descrField"))

    def doWork(self, bwPacket):
        """!start an run of the module.

        @param bwPacket: A BOSWatch packet instance"""
        for descriptor in self.config:
            if not bwPacket.get(descriptor.get("scanField")):
                break  # scanField is not available in this packet
            bwPacket.set(descriptor.get("descrField"), bwPacket.get(descriptor.get("scanField")))
            for description in descriptor.get("descriptions"):
                if str(description.get("for")) == bwPacket.get(descriptor.get("scanField")):
                    logging.debug("Description '%s' added in packet field '%s'",
                                  description.get("add"), descriptor.get("descrField"))
                    bwPacket.set(descriptor.get("descrField"), description.get("add"))
                    break  # this descriptor has found a description - run next descriptor
        return bwPacket

    def onUnload(self):
        """!Called by destruction of the plugin"""
        pass
