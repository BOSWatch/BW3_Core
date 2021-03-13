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

@file:        routerManager.py
@date:        04.03.2019
@author:      Bastian Schroll
@description: Class for the BOSWatch packet router manager class
"""

# todo think about implement threading for routers and the plugin calls (THREAD SAFETY!!!)
import logging
import importlib
import time
from boswatch.configYaml import ConfigYAML
from boswatch.router.router import Router
from boswatch.router.route import Route

logging.debug("- %s loaded", __name__)


class RouterManager:
    """!Class to manage all routers"""

    def __init__(self):
        """!Create new router"""
        self._routerDict = {}
        self._startTime = int(time.time())

    # if there is an error, router list would be empty (see tmp variable)
    def buildRouters(self, config):
        """!Initialize Routers from given config file

        @param config: instance of ConfigYaml class
        @return True or False"""
        self._routerDict = {}  # all routers and instances of modules/plugins would be destroyed
        routerDict_tmp = {}
        logging.debug("build routers")

        # first we have to init all routers
        # because a router can be a valid target and we need his reference
        for router in config.get("router"):
            if router.get("name") is None or router.get("route") is None:
                logging.error("name or route not found in router: %s", router)
                return False
            if router.get("name") in self._routerDict:
                logging.error("duplicated router name: %s", router.get("name"))
                return False
            routerDict_tmp[router.get("name")] = Router(router.get("name"))

        for router in config.get("router"):
            routerName = router.get("name")

            for route in router.get("route"):
                routeType = route.get("type")
                routeRes = route.get("res")
                routeName = route.get("name", default=routeRes)

                routeConfig = route.get("config", default=ConfigYAML())  # if no config - build a empty

                if routeType is None or routeRes is None:
                    logging.error("type or name not found in route: %s", route)
                    return False

                try:
                    if routeType == "plugin":
                        importedFile = importlib.import_module(routeType + "." + routeRes)
                        loadedClass = importedFile.BoswatchPlugin(routeConfig)
                        routerDict_tmp[routerName].addRoute(Route(routeName,
                                                                  loadedClass._run,
                                                                  loadedClass._getStatistics,
                                                                  loadedClass._cleanup))

                    elif routeType == "module":
                        importedFile = importlib.import_module(routeType + "." + routeRes)
                        loadedClass = importedFile.BoswatchModule(routeConfig)
                        routerDict_tmp[routerName].addRoute(Route(routeName,
                                                                  loadedClass._run,
                                                                  loadedClass._getStatistics,
                                                                  loadedClass._cleanup))

                    elif routeType == "router":
                        routerDict_tmp[routerName].addRoute(Route(routeName, routerDict_tmp[routeRes].runRouter))

                    else:
                        logging.error("unknown type '%s' in %s", routeType, route)
                        return False

                except ModuleNotFoundError:
                    logging.exception("%s not found: %s", route.get("type"), route.get("res"))
                    return False

        logging.debug("finished building routers")
        self._routerDict = routerDict_tmp
        self._showRouterRoute()
        return True

    def runRouters(self, routerRunList, bwPacket):
        """!Run given Routers

        @param routerRunList: string or list of router names in string form
        @param bwPacket: instance of Packet class"""
        if type(routerRunList) is str:  # convert single string name to list
            routerRunList = [routerRunList]

        for routerName in routerRunList:
            if routerName in self._routerDict:
                self._routerDict[routerName].runRouter(bwPacket)
            else:
                logging.warning("unknown router: %s", routerName)

        if self.config.get('server.logging', False):
            self._saveStats()  # write stats to stats file

    def cleanup(self):
        """!Run cleanup routines for all loaded route points"""
        for name, routerObject in self._routerDict.items():
            logging.debug("Start cleanup for %s", name)
            for routePoint in routerObject.routeList:
                if routePoint.cleanup:
                    routePoint.cleanup()

    def _showRouterRoute(self):
        """!Show the routes of all routers"""
        for name, routerObject in self._routerDict.items():
            logging.debug("Route for %s", name)
            counter = 0
            for routePoint in routerObject.routeList:
                counter += 1
                logging.debug(" %d. %s", counter, routePoint.name)

    def _saveStats(self):
        """!Save current statistics to file"""
        lines = []
        for name, routerObject in self._routerDict.items():
            lines.append("[" + name + "]")
            lines.append(" - Route points:    " + str(len(routerObject.routeList)))
            lines.append(" - Runs:            " + str(routerObject._getStatistics()['runCount']))
            for routePoint in routerObject.routeList:
                lines.append("[+] " + routePoint.name)
                if routePoint.statistics:
                    if routePoint.statistics()['type'] == "module":
                        lines.append(" - Runs:            " + str(routePoint.statistics()['runCount']))
                        lines.append(" - Run errors:      " + str(routePoint.statistics()['moduleErrorCount']))
                    elif routePoint.statistics()['type'] == "plugin":
                        lines.append(" - Runs:            " + str(routePoint.statistics()['runCount']))
                        lines.append(" - Setup errors:    " + str(routePoint.statistics()['setupErrorCount']))
                        lines.append(" - Alarm errors:    " + str(routePoint.statistics()['alarmErrorCount']))
                        lines.append(" - Teardown errors: " + str(routePoint.statistics()['teardownErrorCount']))
            lines.append("")

        with open("stats_" + str(self._startTime) + ".txt", "w") as stats:
            for line in lines:
                stats.write(line + "\n")
