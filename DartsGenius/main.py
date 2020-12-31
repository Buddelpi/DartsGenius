'''
Created on Mar 22, 2020

@author: delpi
'''


from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty,\
ObjectProperty,StringProperty,ListProperty, BooleanProperty, DictProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.lang import Builder 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

import re

import game as GameHandler
import databaseHandler as DH
import dartsStatVisLib as dsl
import sectorLib

import json

# import matplotlib
# matplotlib.use("Qt5Agg")
# import matplotlib.pyplot as plt


PROFILE_TEMPLATE  = "Database/Profile_Template.json"
PROFILES  = "Database/Profiles.json"
GAME_TEMPLATE  = "Database/Game_Template.json"
GAMES  = "Database/Games.json"

class HomeScreen(Screen):
    pass

class GameScreen(Screen):
    currDart = NumericProperty(1)
    

class SettingsScreen(Screen):
    pass
    

class GameStatsScreen(Screen):
    statText = StringProperty('')
    
class StatsScreen(Screen):
    pass
    
class ProfilePopup(BoxLayout):
    
    popupText = StringProperty("Now you can create a new profile or press ESC to dismiss")
    
    def createProfile(self):
        print(self.ids.ProfileName.text)
        
        if self.ids.ProfileName.text:
            if App.get_running_app().dh.addProfile(str.strip(self.ids.ProfileName.text)):
                self.popupText = "New profile created: {}\n\nNow you can create a new profile or press ESC to dismiss".format(self.ids.ProfileName.text)
                Clock.schedule_once(self.changeTextBack, 5)
            else:
                self.popupText = "A profile with this name already exists: {}\n\nNow you can create a new profile or press ESC to dismiss".format(self.ids.ProfileName.text)
                Clock.schedule_once(self.changeTextBack, 5)

    def changeTextBack(self,dt):
        self.popupText = "Now you can create a new profile or press ESC to dismiss"
        return True
    
    
class DartsGame(Widget):
    
    
    def show_popup(self):
        App.get_running_app().show_ProfilePopup()
        
      
        
class DartsApp(App):
    
    index = NumericProperty(-1)
    screen_names = ListProperty([])
    
    isHandicapMode = BooleanProperty(False)
    
    dh = DH.DatabaseHandler(PROFILE_TEMPLATE, PROFILES, GAME_TEMPLATE, GAMES)
    
    selectedPlayerList = ListProperty(["-","-","-","-"])
    
    availablePlayerList = ListProperty(dh.getProfileNameList())
    
    profileShortInfoText = StringProperty(dh.getShortProfileText())
    gameStatsText = StringProperty('')
    currStatIndex = NumericProperty(0)
    
    gameCanStart = BooleanProperty(False)
    
    gameType = StringProperty('501')
    gameLegNum = NumericProperty(1)
    gameFirstTo = NumericProperty(1)
    gameRandOrd = BooleanProperty(True)
    
    gameIsOn = BooleanProperty(False)
    confNeeded = BooleanProperty(False)
    
    currGame = ObjectProperty(None)
    
    currGameStat = DictProperty({})
    
    playerText = ListProperty(['','','',''])
    playerTextColor = ListProperty([[0, .7, .1, 1],[0, .3, .1, 1],[0, .3, .1, 1],[0, .3, .1, 1]])
    
    def updateSM(self,dt):
        if self.gameIsOn:

            for index in range(self.currGame.numPlayers):
                self.playerText[index] = "[b]{}\n{}[/b][size=32]\nS: {} L: {}\nLegAvg: {}  GameAvg: {}[/size]".format( \
                                                                self.currGame.playerList[index].name, \
                                                                self.currGame.playerList[index].currentScoreToShow, \
                                                                self.currGame.playerList[index].setsWon, \
                                                                self.currGame.playerList[index].legsWon, \
                                                                round(self.currGame.playerList[index].legAvg,2), \
                                                                round(self.currGame.playerList[index].gameAvg,2))
                if self.currGame.currPlayerIndex == index:
                    self.playerTextColor[index] = [0, .7, .1, 1]
                else:
                    self.playerTextColor[index] = [0, .3, .1, 1]
            
            if self.currGame.waitForConfirm != 'NoConfirmNeeded':
                self.confNeeded = True
            else:
                self.confNeeded = False
             
            self.getCurrDart()
                
            if self.currGame.gameState == 'GameEnd':
                self.gameIsOn = False
                self.dh.addGame(self.currGame.gameStats)
                
                profList = []
                for pl in self.currGame.playerList:
                    profList.append(pl.playerDB)
                self.dh.updateProfile(profList)
                
                self.currGame.gameState = 'DBCopiedAfterGameEnd'
                
#                 dartList = []
#                 for dartStat in self.currGame.playerList[0].playerDB['Stats']['X01']['OverallDartStats'].keys():
#                     for i in range(self.currGame.playerList[0].playerDB['Stats']['X01']['OverallDartStats'][dartStat]):
#                         dartList.append(int(dartStat))
#                 dartList.sort()
#                 
#                 x_range = (0,60) 
#                 bins = 60
                #plotting a histogram 
                #plt.hist(dartList,bins, color = 'green', histtype = 'bar', rwidth = 0.8) 
                  
                # x-axis label 
                #plt.xlabel('Dart Score') 
                # frequency label 
                #plt.ylabel('Thrown #') 
                # plot title 
                #plt.title('Overall Dart Stats') 
                  
                # function to show the plot 
                #plt.savefig('Images/plot.png') 
                #plt.show()
                
                self.root.ids.ScrnMngr.current = 'Game Statistics'
            
            if self.currGame.gameState == 'DBCopiedAfterGameEnd':
                self.currGameStat = self.currGame.playerList[self.currStatIndex].playerCurrentStats['X01']
                
                self.updateSectorStatScreen(self.currGameStat['OverallSectorStats'])
                self.gameStatsText = dsl.getGameStatText(self.selectedPlayerList[self.currStatIndex], 'X01', self.currGameStat)
                
        if self.profileShortInfoText != self.dh.getShortProfileText():
            self.profileShortInfoText = self.dh.getShortProfileText()
            self.updatePlayerLists()
    
    def get_color_from_hex(self,s):
        '''Transform a hex string color to a kivy'''
        
        if s.startswith('#'):
            return self.get_color_from_hex(s[1:])
        value = [int(x, 16) / 255. for 
            x in re.split('([0-9a-f]{2})', s.lower()) if x !='']
        if len(value) == 3:
            value.append(1)
        return value
            
    def updateSectorStatScreen(self, DB):
        
        limitList = dsl.createLimitList(DB)
        
        for sector in range(1,21):
            
            upperStr = '{}U'.format(sector)
            lowerStr = '{}L'.format(sector)
            tripleStr = '{}T'.format(sector)
            doubleStr = '{}D'.format(sector)
            
            if upperStr in DB.keys():
                color = dsl.getColor4Rate(limitList, DB[upperStr])
            else:
                color = dsl.colorPalette[0]
            self.root.ids.gss.ids['stat{}'.format(sector)].upperSectorColor = self.get_color_from_hex(color)   
            
            if lowerStr in DB.keys():
                color = dsl.getColor4Rate(limitList, DB[lowerStr])
            else:
                color = dsl.colorPalette[0]
            self.root.ids.gss.ids['stat{}'.format(sector)].lowerSectorColor = self.get_color_from_hex(color)   
            
            if tripleStr in DB.keys():
                color = dsl.getColor4Rate(limitList, DB[tripleStr])
            else:
                color = dsl.colorPalette[0]
            self.root.ids.gss.ids['stat{}'.format(sector)].tripleColor = self.get_color_from_hex(color)   
                
            if doubleStr in DB.keys():
                color = dsl.getColor4Rate(limitList, DB[doubleStr])
            else:
                color = dsl.colorPalette[0]
            self.root.ids.gss.ids['stat{}'.format(sector)].doubleColor = self.get_color_from_hex(color)   
         
        if 'M' in DB.keys():
                color = dsl.getColor4Rate(limitList, DB['M'])
        else:
            color = dsl.colorPalette[0]
        self.root.ids.gss.ids['statBL'].blackColor = self.get_color_from_hex(color)   
        
        if 'B' in DB.keys():
                color = dsl.getColor4Rate(limitList, DB['B'])
        else:
            color = dsl.colorPalette[0]
        self.root.ids.gss.ids['statBU'].bullColor = self.get_color_from_hex(color)        
        
        if 'DB' in DB.keys():
                color = dsl.getColor4Rate(limitList, DB['DB'])
        else:
            color = dsl.colorPalette[0]
        self.root.ids.gss.ids['statBU'].bullsEyeColor = self.get_color_from_hex(color)   
            
    def build(self):
        
        game = DartsGame()
        self.title = 'DartsGenius'
        Clock.schedule_interval(self.updateSM, 1 / 60.)
        
        return game

    def on_pause(self):
        return True

    def on_resume(self):
        pass


    def load_screen(self, index):
        if index in self.screens:
            return self.screens[index]
        screen = Builder.load_file(self.available_screens[index])
        self.screens[index] = screen
        return screen

    def loadData(self, file):
        with open(file, "r") as read_file:
            return json.load(read_file)

    def show_ProfilePopup(self):
        show = ProfilePopup()
    
        popupWindow = Popup(title="Create Profile", content=show, size_hint=(None,None),size=(600,600))
    
        popupWindow.open()
        
        
    def evaluatePlayerSpinners(self, playerSelected, listPosition):
        self.selectedPlayerList[listPosition] = playerSelected
        
        
        if playerSelected == '-':
            for index in range(listPosition,4):
                self.selectedPlayerList[index] = '-'
        
        self.updatePlayerLists()
        print(self.selectedPlayerList)


    def updatePlayerLists(self):
        self.availablePlayerList = self.dh.getProfileNameList()
        
        for selectedName in self.selectedPlayerList:
            if (selectedName != '-') and (selectedName in self.availablePlayerList):
                self.availablePlayerList.remove(selectedName)
                
                
        if self.selectedPlayerList[0] != '-':
            self.gameCanStart = True
        else:
            self.gameCanStart = False
    
    def createPlayerObjects(self):  
        
        playerObjectList = []
        
        for selectedName in self.selectedPlayerList:
            if (selectedName != '-'):
                playerObjectList.append(GameHandler.Player(self.dh.getProfile(selectedName)))
        return playerObjectList
        
    def startGame(self):
        
        playerList = self.createPlayerObjects()
        print(self.dh.nextGameID)
        self.currGame = GameHandler.Game(playerList,self.gameType,self.gameFirstTo,self.gameLegNum,self.dh.nextGameID)
        self.gameIsOn = True      
        
    
    def switchPlayerStats(self):
        self.currStatIndex += 1
        
        if self.currStatIndex == self.currGame.numPlayers:
            self.currStatIndex = 0
              
        self.currGameStat = self.currGame.playerList[self.currStatIndex].playerCurrentStats['X01']
                
        self.updateSectorStatScreen(self.currGameStat['OverallSectorStats'])
        self.gameStatsText = dsl.getGameStatText(self.selectedPlayerList[self.currStatIndex], 'X01', self.currGameStat)
    
    def getCurrDart(self):
   
        try:
            currDart = self.currGame.currDart
            currRound = self.currGame.currRound
            wfc = self.currGame.waitForConfirm
        except:
            currDart = 1
            currRound = 1
            wfc = ''
        
        if (wfc=='Win' or wfc=='Bust') and currDart < 3:
            currDart += 1
        
        if currDart == 1:
            self.root.ids.game_screen.ids.dart1.opacity = 1
        else:
            self.root.ids.game_screen.ids.dart1.opacity = 0   
        
        if currDart < 3:
            self.root.ids.game_screen.ids.dart2.opacity = 1
        else:
            self.root.ids.game_screen.ids.dart2.opacity = 0
                        
        if wfc == 'Normal' or (currDart==3 and (wfc=='Win' or wfc=='Bust')):
            self.root.ids.game_screen.ids.dart3.opacity = 0
        else:
            self.root.ids.game_screen.ids.dart3.opacity = 1
   
        self.root.ids.game_screen.ids.game_info.text = 'Round {}'.format(currRound)
            

if __name__ == '__main__':
    DartsApp().run()