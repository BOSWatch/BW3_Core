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

@file:        wildcard.py
@date:        15.01.2018
@author:      Bastian Schroll
@description: Functions to replace wildcards in stings
"""
import logging
import time

logging.debug("- %s loaded", __name__)

# todo check function - write an test

_additionalWildcards = {}


def registerWildcard(wildcard, bwPacketField):
    """!Register a new additional wildcard

    @param wildcard: New wildcard string with format: '{WILDCARD}'
    @param bwPacketField: Field of the bwPacket which is used for wildcard replacement"""
    if wildcard in _additionalWildcards:
        logging.error("wildcard always registered: %s", wildcard)
        return
    logging.debug("register new wildcard %s for field: %s", wildcard, bwPacketField)
    _additionalWildcards[wildcard] = bwPacketField


def replaceWildcards(message, bwPacket):
    """!Replace the wildcards in a given message

    @param message: Message in which wildcards should be replaced
    @param bwPacket: bwPacket instance with the replacement information
    @return Input message with the replaced wildcards"""
    _wildcards = {
        # formatting wildcards
        # todo check if br and par are needed - if not also change config
        "{BR}": "\r\n",
        "{LPAR}": "(",
        "{RPAR}": ")",
        "{TIME}": time.strftime("%d.%m.%Y %H:%M:%S"),

        # info wildcards
        # server
        "{SNAME}": bwPacket.get("serverName"),
        "{SVERS}": bwPacket.get("serverVersion"),
        "{SDATE}": bwPacket.get("serverBuildDate"),
        "{SBRCH}": bwPacket.get("serverBranch"),

        # client
        "{CNAME}": bwPacket.get("clientName"),
        "{CIP}": bwPacket.get("clientIP"),
        "{CVERS}": bwPacket.get("clientVersion"),
        "{CDATE}": bwPacket.get("clientBuildDate"),
        "{CBRCH}": bwPacket.get("clientBranch"),

        # boswatch wildcards
        "{INSRC}": bwPacket.get("inputSource"),
        "{TIMES}": bwPacket.get("timestamp"),
        "{FREQ}": bwPacket.get("frequency"),
        "{MODE}": bwPacket.get("mode"),

        # fms wildcards
        "{FMS}": bwPacket.get("fms"),
        "{SERV}": bwPacket.get("service"),
        "{COUNT}": bwPacket.get("country"),
        "{LOC}": bwPacket.get("location"),
        "{VEHC}": bwPacket.get("vehicle"),
        "{STAT}": bwPacket.get("status"),
        "{DIR}": bwPacket.get("direction"),
        "{DIRT}": bwPacket.get("directionText"),
        "{TACI}": bwPacket.get("tacticalInfo"),

        # pocsag wildcards
        "{BIT}": bwPacket.get("bitrate"),
        "{RIC}": bwPacket.get("ric"),
        "{SRIC}": bwPacket.get("subric"),
        "{SRICT}": bwPacket.get("subricText"),
        "{MSG}": bwPacket.get("message"),

        # zvei wildcards
        "{TONE}": bwPacket.get("tone"),

        # message for MSG packet is done in poc
    }
    for wildcard, field in _wildcards.items():
        if field is not None:
            message = message.replace(wildcard, field)

    for wildcard, fieldName in _additionalWildcards.items():
        field = bwPacket.get(fieldName)
        if field is not None:
            message = message.replace(wildcard, field)

    return message
