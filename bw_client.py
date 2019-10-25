#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    ____  ____  ______       __      __       __       _____
   / __ )/ __ \/ ___/ |     / /___ _/ /______/ /_     |__  /
  / __  / / / /\__ \| | /| / / __ `/ __/ ___/ __ \     /_ <
 / /_/ / /_/ /___/ /| |/ |/ / /_/ / /_/ /__/ / / /   ___/ /
/_____/\____//____/ |__/|__/\__,_/\__/\___/_/ /_/   /____/
                German BOS Information Script
                     by Bastian Schroll

@file:        bw_client.py
@date:        09.12.2017
@author:      Bastian Schroll
@description: BOSWatch client application
"""
# pylint: disable=wrong-import-position
# pylint: disable=wrong-import-order
from boswatch.utils import paths

if not paths.makeDirIfNotExist(paths.LOG_PATH):
    print("cannot find/create log directory: %s", paths.LOG_PATH)
    exit(1)

import logging.config
logging.config.fileConfig(paths.CONFIG_PATH + "logger_client.ini")
logging.debug("")
logging.debug("######################## NEW LOG ############################")
logging.debug("BOSWatch client has started ...")


logging.debug("Import python modules")
import argparse
logging.debug("- argparse")
import threading
logging.debug("- threading")
import queue
logging.debug("- queue")
import time
logging.debug("- time")

logging.debug("Import BOSWatch modules")
from boswatch.configYaml import ConfigYAML
from boswatch.network.client import TCPClient
from boswatch.network.broadcast import BroadcastClient
from boswatch.processManager import ProcessManager
from boswatch.decoder.decoder import Decoder
from boswatch.utils import header
from boswatch.utils import misc

header.logoToLog()
header.infoToLog()

# With -h or --help you get the Args help
parser = argparse.ArgumentParser(prog="bw_client.py",
                                 description="""BOSWatch is a Python Script to receive and
                                 decode german BOS information with rtl_fm and multimon-NG""",
                                 epilog="""More options you can find in the extern client.ini
                                 file in the folder /config""")
parser.add_argument("-c", "--config", help="Name to configuration File", required=True)
parser.add_argument("-t", "--test", help="Start Client with testdata-set", action="store_true")
args = parser.parse_args()

bwConfig = ConfigYAML()
if not bwConfig.loadConfigFile(paths.CONFIG_PATH + args.config):
    logging.error("cannot load config file")
    exit(1)

# ========== CLIENT CODE ==========
mmThread = None
bwClient = None

try:
    ip = bwConfig.get("server", "ip", default="127.0.0.1")
    port = bwConfig.get("server", "port", default="8080")

    if bwConfig.get("client", "useBroadcast", default=False):
        broadcastClient = BroadcastClient()
        if broadcastClient.getConnInfo():
            ip = broadcastClient.serverIP
            port = broadcastClient.serverPort

    # ========== INPUT CODE ==========
    def handleSDRInput(dataQueue, sdrConfig, decoderConfig):  # todo exception handling inside
        sdrProc = ProcessManager(str(sdrConfig.get("rtlPath", default="rtl_fm")))
        sdrProc.addArgument("-d " + str(sdrConfig.get("device", default="0")))     # device id
        sdrProc.addArgument("-f " + sdrConfig.get("frequency"))                    # frequencies
        sdrProc.addArgument("-p " + str(sdrConfig.get("error", default="0")))      # frequency error in ppm
        sdrProc.addArgument("-l " + str(sdrConfig.get("squelch", default="1")))    # squelch
        sdrProc.addArgument("-g " + str(sdrConfig.get("gain", default="100")))     # gain
        sdrProc.addArgument("-M fm")                                               # set mode to fm
        sdrProc.addArgument("-E DC")                                               # set DC filter
        sdrProc.addArgument("-s 22050")                                            # bit rate of audio stream
        sdrProc.setStderr(open(paths.LOG_PATH + "rtl_fm.log", "a"))
        sdrProc.start()
        # sdrProc.skipLinesUntil("Output at")

        mmProc = ProcessManager(str(sdrConfig.get("mmPath", default="multimon-ng")), textMode=True)
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
        mmProc.setStdin(sdrProc.stdout)
        mmProc.setStderr(open(paths.LOG_PATH + "multimon-ng.log", "a"))
        mmProc.start()
        # mmProc.skipLinesUntil("Available demodulators:")

        logging.info("start decoding")
        while inputThreadRunning:
            if not sdrProc.isRunning:
                logging.warning("rtl_fm was down - try to restart")
                sdrProc.start()
                # sdrProc.skipLinesUntil("Output at")  # last line form rtl_fm before data
            elif not mmProc.isRunning:
                logging.warning("multimon was down - try to restart")
                mmProc.start()
                # mmProc.skipLinesUntil("Available demodulators:")  # last line from mm before data
            elif sdrProc.isRunning and mmProc.isRunning:
                line = mmProc.readline()
                if line:
                    dataQueue.put_nowait((line, time.time()))
                    logging.debug("Add data to queue")
                    print(line)
        logging.debug("stopping thread")
        mmProc.stop()
        sdrProc.stop()
    # ========== INPUT CODE ==========

    inputQueue = queue.Queue()

    if not args.test:
        inputThreadRunning = True
        mmThread = threading.Thread(target=handleSDRInput, name="mmReader",
                                    args=(inputQueue, bwConfig.get("inputSource", "sdr"), bwConfig.get("decoder")))
        mmThread.daemon = True
        mmThread.start()
    else:
        logging.warning("STARTING TESTMODE!")
        logging.debug("reading testdata from file")
        testFile = open("test/testdata.list", mode="r", encoding="utf-8")
        for testData in testFile:
            if (len(testData.rstrip(' \t\n\r')) > 1) and ("#" not in testData[0]):
                logging.info("Testdata: %s", testData.rstrip(' \t\n\r'))
                inputQueue.put_nowait((testData.rstrip(' \t\n\r'), time.time()))
        logging.debug("finished reading testdata")

    bwClient = TCPClient()
    bwClient.connect(ip, port)
    while 1:

        if not bwClient.isConnected:
            reconnectDelay = bwConfig.get("client", "reconnectDelay", default="3")
            logging.warning("connection to server lost - sleep %d seconds", reconnectDelay)
            time.sleep(reconnectDelay)
            bwClient.connect(ip, port)

        elif not inputQueue.empty():
            data = inputQueue.get()
            logging.info("get data from queue (waited %0.3f sec.)", time.time() - data[1])
            logging.debug("%s packet(s) still waiting in queue", inputQueue.qsize())

            bwPacket = Decoder.decode(data[0])
            inputQueue.task_done()

            if bwPacket is None:
                continue

            bwPacket.printInfo()
            misc.addClientDataToPacket(bwPacket, bwConfig)

            for sendCnt in range(bwConfig.get("client", "sendTries", default="3")):
                bwClient.transmit(str(bwPacket))
                if bwClient.receive() == "[ack]":
                    logging.debug("ack ok")
                    break
                sendDelay = bwConfig.get("client", "sendDelay", default="3")
                logging.warning("cannot send packet - sleep %d seconds", sendDelay)
                time.sleep(sendDelay)

        else:
            if args.test:
                break
            time.sleep(0.1)  # reduce cpu load (wait 100ms)
            # in worst case a packet have to wait 100ms until it will be processed


except KeyboardInterrupt:  # pragma: no cover
    logging.warning("Keyboard interrupt")
except SystemExit:  # pragma: no cover
    logging.error("BOSWatch interrupted by an error")
except:  # pragma: no cover
    logging.exception("BOSWatch interrupted by an error")
finally:
    logging.debug("Starting shutdown routine")
    if bwClient:
        bwClient.disconnect()
    inputThreadRunning = False
    if mmThread:
        mmThread.join()
    logging.debug("BOSWatch client has stopped ...")
