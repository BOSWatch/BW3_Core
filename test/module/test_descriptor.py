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

@file:        test_descriptor.py
@date:        14.04.2020
@author:      Bastian Schroll
@description: Unittests for BOSWatch. File have to run as "pytest" unittest
"""
# problem of the pytest fixtures
# pylint: disable=redefined-outer-name
import logging
import pytest
from boswatch.utils import paths

from boswatch.configYaml import ConfigYAML
from boswatch.packet import Packet
from module.descriptor import BoswatchModule as Descriptor


def setup_method(method):
    logging.debug("[TEST] %s.%s", method.__module__, method.__name__)


@pytest.fixture
def makeDescriptor():
    """!Build a descriptor object with loaded configuration"""
    config = ConfigYAML()
    assert config.loadConfigFile(paths.TEST_PATH + "test_config.yaml") is True
    descriptor = Descriptor(config.get("descriptor_test"))
    return descriptor


@pytest.fixture
def makePacket():
    """!Build a BW Packet object"""
    packet = Packet()
    return packet


def test_descriptorFoundFirst(makeDescriptor, makePacket):
    """!Run descriptor on the first entry in list"""
    makePacket.set("tone", "12345")
    makePacket = makeDescriptor.doWork(makePacket)
    assert makePacket.get("description") == "Test 12345"


def test_descriptorFoundSecond(makeDescriptor, makePacket):
    """!Run descriptor on the second entry in list"""
    makePacket.set("tone", "23456")
    makePacket = makeDescriptor.doWork(makePacket)
    assert makePacket.get("description") == "Test 23456"


def test_descriptorNotFound(makeDescriptor, makePacket):
    """!Run descriptor no matching data found"""
    makePacket.set("tone", "99999")
    makePacket = makeDescriptor.doWork(makePacket)
    assert makePacket.get("description") == "99999"


def test_descriptorScanFieldNotAvailable(makeDescriptor, makePacket):
    """!Run descriptor on a non existent scanField"""
    makePacket = makeDescriptor.doWork(makePacket)
    assert makePacket.get("description") is None
