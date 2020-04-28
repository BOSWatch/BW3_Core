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

@file:        lienInInput.py
@date:        18.04.2020
@author:      Philipp von Kirschbaum
@description: Input source for line-in with alsa
"""
import logging
from boswatch.utils import paths
from boswatch.processManager import ProcessManager
from boswatch.inputSource.inputBase import InputBase

logging.debug("- %s loaded", __name__)


class LineInInput(InputBase):
    """!Class for the line-in input source"""

    def _runThread(self, dataQueue, lineInConfig, decoderConfig):
        lineInProc = None
        mmProc = None
        try:
            lineInProc = ProcessManager("arecord")
            lineInProc.addArgument("-q ")                                         # supress any other outputs
            lineInProc.addArgument("-f S16_LE")                                   # set output format (16bit)
            lineInProc.addArgument("-r 22050")                                    # set output sampling rate (22050Hz)
            lineInProc.addArgument("-D plughw:" +
                                   str(lineInConfig.get("card", default="1")) +
                                   "," +
                                   str(lineInConfig.get("device", default="0")))  # device id
            lineInProc.setStderr(open(paths.LOG_PATH + "asla.log", "a"))
            lineInProc.start()

            mmProc = ProcessManager(str(lineInConfig.get("mmPath", default="multimon-ng")), textMode=True)
            if decoderConfig.get("fms", default=0):
                mmProc.addArgument("-a FMSFSK")
            if decoderConfig.get("zvei", default=0):
                mmProc.addArgument("-a ZVEI1")
            if decoderConfig.get("poc512", default=0):
                mmProc.addArgument("-a POCSAG512")
            if decoderConfig.get("poc1200", default=0):
                mmProc.addArgument("-a POCSAG1200")
            if decoderConfig.get("poc2400", default=0):
                mmProc.addArgument("-a POCSAG2400")
            mmProc.addArgument("-f alpha")
            mmProc.addArgument("-t raw -")
            mmProc.setStdin(lineInProc.stdout)
            mmProc.setStderr(open(paths.LOG_PATH + "multimon-ng.log", "a"))
            mmProc.start()

            logging.info("start decoding")
            while self._isRunning:
                if not lineInProc.isRunning:
                    logging.warning("asla was down - try to restart")
                    lineInProc.start()
                elif not mmProc.isRunning:
                    logging.warning("multimon was down - try to restart")
                    mmProc.start()
                elif lineInProc.isRunning and mmProc.isRunning:
                    line = mmProc.readline()
                    if line:
                        self.addToQueue(line)
        except:
            logging.exception("error in lineIn input routine")
        finally:
            mmProc.stop()
            lineInProc.stop()
