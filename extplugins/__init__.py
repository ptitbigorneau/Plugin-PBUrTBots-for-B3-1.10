# -*- coding: utf-8 -*-
#
# PBUrTBots For Urban Terror plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2015 PtitBigorneau - www.ptitbigorneau.fr
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

__author__  = 'PtitBigorneau www.ptitbigorneau.fr'
__version__ = '1.1.0'

import b3, re
import b3.plugin
import b3.events
import random
from b3 import clients
import b3.cron
from b3.functions import getCmd

def fexist(fichier):

    try:

        file(fichier)

        return True

    except:

        return False

class PburtbotsPlugin(b3.plugin.Plugin):

    _adminPlugin = None
    _active = True
    _cronTab = None
    _listmapsbots = "listmapsbots.txt"
    _mapcyclebots = "mapcyclebots.txt"
    _mapcycle =  "mapcycle.txt"
    _minplayers = 8
    _test = None
    _players = 0
    _spec = 0
    _red = 0
    _blue = 0
    _bots = 0
    _testbots = 'nobots'
    _testnext = None

    def onLoadConfig(self):

        self._mapcyclebots = self.getSetting('settings', 'mapcyclebots', b3.STRING, self._mapcyclebots)
        self._listmapsbots = self.getSetting('settings', 'listmapsbots', b3.STRING, self._listmapsbots)
        self._mapcycle = self.getSetting('settings', 'mapcycle', b3.STRING, self._mapcycle)
        self._minplayers = self.getSetting('settings', 'minplayers', b3.INT, self._minplayers)
        self._active = self.getSetting('settings', 'active', b3.BOOLEAN, self._active)

    def onStartup(self):

        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:

            self.error('Could not find admin plugin')
            return False

        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = getCmd(self, cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)

        self.registerEvent('EVT_CLIENT_AUTH', self.onClientAuth)
        self.registerEvent('EVT_GAME_MAP_CHANGE', self.onGameMapChange)
        self.registerEvent('EVT_STOP', self.onStop)

        self.console.write('bot_minplayers "0"')
        self.console.write('kick allbots')

        self.listemapsbots()

        if self._active:

            if self._testbots != None:

                if self.console.game.mapName not in self._mapsbots:

                   self.console.write('bot_minplayers "0"')
                   self.console.write('g_mapcycle "%s"'%self._mapcycle)
                   self._test = None

                else:

                   self.console.write('bot_minplayers "%s"'%self._minplayers)
                   self.console.write('g_mapcycle "%s"'%self._mapcyclebots)
                   self._test = "bots"
                   self._testbots = None

        self._cronTab = b3.cron.PluginCronTab(self, self.control, minute='*/1')
        self.console.cron + self._cronTab

    def onGameMapChange(self,  event):

        self._testnext = None

    def onClientAuth(self,  event):

        if not self._active:
            return

        client = event.client

        if self.console.game.mapName not in self._mapsbots:

            self.console.write('bot_minplayers "0"')
            self.console.write('kick allbots')

        self.debug("%s"%event.client.bot)

    def onStop(self,  event):

        self.console.write('g_mapcycle "%s"'%self._mapcycle)
        self.console.write("kick allbots")

    def randomgear(self):

        n = 0

        for y in self._listgears:

            n = n + 1

        ngear = random.randint(0, n-1)

        x = ngear
        self.gear = self._listgears[int(x)]

        return

    def control(self):

        if not self._active:
            return

        self.nbplayers()

        if self._testbots == 'nobots' and self._players == 0:

            self._testbots = None

        if self._testbots == 'nobots' and self._players != 0:

            return

        if self.console.game.mapName not in self._mapsbots:

            if self._players < self._minplayers:

                nmaps = len(self._cyclebots)
                n = random.randint(0, nmaps-1)

                if self._cyclebots[int(n)] == self.console.game.mapName:

                    n = n + 1
                if self._testnext != "ok":
                    self.console.write('g_nextmap "%s"'%self._cyclebots[int(n)])
                    self._testnext = "ok"

                self.console.write('g_mapcycle "%s"'%self._mapcyclebots)
                self._test = "bots"

                if self._players == 0:

                    self.console.write('cyclemap')

            if self._players >= self._minplayers:

                self.console.write('bot_minplayers "0"')
                self.console.write('kick allbots')
                self.console.write('g_mapcycle "%s"'%self._mapcycle)
                self._test = None

        else:

            if self._players - self._spec < self._minplayers:

                self.console.write('bot_minplayers "%s"'%self._minplayers)
                self.console.write('g_mapcycle "%s"'%self._mapcyclebots)
                self._test = "bots"

            if self._players - self._bots - self._spec >= self._minplayers:

                self.console.write('bot_minplayers "0"')
                self.console.write('kick allbots')
                self.console.write('g_mapcycle "%s"'%self._mapcycle)
                self._test = None

    def listemapsbots(self):

        homepath = self.console.getCvar('fs_homepath').getString()
        basepath = self.console.getCvar('fs_basepath').getString()
        gamepath = self.console.getCvar('fs_game').getString()

        self._mapsbots = []

        listmapsbotstxt = self._listmapsbots

        if fexist(listmapsbotstxt) == False:

            listmapsbotstxt = homepath + "/" + gamepath + "/" + listmapsbotstxt

        fichier = open(listmapsbotstxt, "r")

        contenu = fichier.readlines()
        fichier.close()

        for ligne in contenu:

            ligne = ligne.replace("\n", "")
            ligne = ligne.replace("\r", "")
            ligne = ligne.replace(" ", "")

            if ligne != "":

                if self._test == None:

                    if "{" in ligne:

                        self._test = "test"
                        continue

                    else:

                        self._mapsbots.append(ligne)

                    if self._test != None:

                        if "}" in ligne:

                            self._test = None

        self._test = None

        self._cyclebots = []

        mapcyclebotstxt = self._mapcyclebots

        mapcyclefile = basepath + "/" + gamepath + "/" + mapcyclebotstxt

        if fexist(mapcyclefile) == False:

            mapcyclefile = homepath + "/" + gamepath + "/" + mapcyclebotstxt

        fichier = open(mapcyclefile, "r")

        contenu2 = fichier.readlines()
        fichier.close()

        for ligne2 in contenu2:

            ligne2 = ligne2.replace("\n", "")
            ligne2 = ligne2.replace("\r", "")
            ligne2 = ligne2.replace(" ", "")

            if ligne2 != "":

                if self._test == None:

                    if "{" in ligne2:

                        self._test = "test"
                        continue

                    else:

                        self._cyclebots.append(ligne2)

                    if self._test != None:

                        if "}" in ligne2:

                            self._test = None

        return

    def nbplayers(self):

        self._players = 0
        self._spec = 0
        self._red = 0
        self._blue = 0
        self._bots = 0

        for x in self.console.clients.getList():
            self._players += 1

            if x.ip == '0.0.0.0' or "BOT" in x.guid:

                self._bots += 1

            if x.team == 1:

                self._spec += 1

            if x.team == 2:

                self._red += 1

            if x.team == 3:

                self._blue += 1

        return

    def cmd_kickbots(self, data, client, cmd=None):

        """\
        kick allbots
        """
        self._active = False
        self.console.write('kick allbots')
        self._testbots = 'nobots'
        self._test = None
        self.console.write('bot_minplayers "0"')
        self.console.write('g_mapcycle "%s"'%self._mapcycle)
        client.message('^7You ^1kicked ^7all bots in the server')
        client.message('^7Use ^2!addbots ^7to add them')

    def cmd_addbots(self, data, client, cmd=None):

        """\
        add bots
        """

        self._active = True

        if self._testbots == None and self._test == "bots":

            client.message('^7There are already bots on the server')
            return

        self.nbplayers()
        self._testbots == None

        if self._players >= self._minplayers:

            client.message('^7There are too many players to add bots')

            return

        else:

            self.listemapsbots()
            self.console.write('g_mapcycle "%s"'%self._mapcyclebots)

            nmaps = len(self._cyclebots)
            n = random.randint(0, nmaps-1)

            if self._cyclebots[int(n)] == self.console.game.mapName:

                n = n + 1

            self.console.write('g_nextmap "%s"'%self._cyclebots[int(n)])

            if self.console.game.mapName not in self._mapsbots:

                client.message('^3%s ^7does not support bots'%self.console.game.mapName)
                client.message('^7Bots will be added to the next map')

            else:

                self.console.write('bot_minplayers "%s"'%self._minplayers)
                self._test = "bots"
