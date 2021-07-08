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

@file:        updater.py
@date:        08.03.2019
@author:      Bastian Schroll
@description: Class for a BOSWatch automated updates
"""
import logging
import urllib.request
import re
from boswatch import version

logging.debug("- %s loaded", __name__)


class Updater:
    def __init__(self, branch):
        self._clientVersion = None
        self._serverVersion = None
        self._date = None
        self._branch = branch

    def _getOnlineVersion(self):
        data = urllib.request.urlopen("https://raw.githubusercontent.com/BOSWatch/BW3-Core/" + self._branch + "/boswatch/version.py")
        for line in data:
            content = str(line, "utf8")

            if "client = " in content:
                data = re.findall("(\d+)", content)
                self._clientVersion = {"major": int(data[0]), "minor": int(data[1]), "patch": int(data[2])}

            if "server = " in content:
                data = re.findall("(\d+)", content)
                self._serverVersion = {"major": int(data[0]), "minor": int(data[1]), "patch": int(data[2])}

            if "date = " in content:
                data = re.findall("(\d+)", content)
                self._date = {"day": int(data[0]), "month": int(data[1]), "year": int(data[2])}

            if "branch = " in content:
                data = re.findall("(?:branch)(?:[ =\"]+)(\w*)", content)
                self._branch = data[0]

    def checkClientUpdate(self):
        logging.debug("checking for client update")
        self._getOnlineVersion()
        if version.client["major"] < self._clientVersion["major"] or \
                version.client["minor"] < self._clientVersion["minor"] or \
                version.client["patch"] < self._clientVersion["patch"]:
            logging.info("There is a client update from available: %d.%d.%d (%d.%d.%d) -> %d.%d.%d (%d.%d.%d)",
                         version.client["major"], version.client["minor"], version.client["patch"],
                         version.date["day"], version.date["month"], version.date["year"],
                         self._clientVersion["major"], self._clientVersion["minor"], self._clientVersion["patch"],
                         self._date["day"], self._date["month"], self._date["year"])
            return False
        else:
            logging.debug("client is up to date")
            return True

    def checkServerUpdate(self):
        logging.debug("checking for server update")
        self._getOnlineVersion()
        if version.server["major"] < self._serverVersion["major"] or \
                version.server["minor"] < self._serverVersion["minor"] or \
                version.server["patch"] < self._serverVersion["patch"]:
            logging.info("There is a server update from %d.%d.%d available: %d.%d.%d -> %d.%d.%d",
                         version.date["day"], version.date["month"], version.date["year"],
                         version.server["major"], version.server["minor"], version.server["patch"],
                         self._serverVersion["major"], self._serverVersion["minor"], self._serverVersion["patch"])
            return False
        else:
            logging.debug("server is up to date")
            return True

    def doUpdate(self):
        pass
