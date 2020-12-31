'''
Created on May 10, 2020

@author: delpi
'''


import json

import os.path
from os import path
import copy



class DatabaseHandler():
    
    def __init__(self, pTemplate, p, gTemplate, g):
        
        self.pTemplateFile = pTemplate
        self.gTemplateFile = gTemplate
        
        self.pFile = p
        self.gFile = g
        self.profiles = {}
        self.games = []
        self.nextGameID = 1
        
        self.profileTemplate = self.loadData(pTemplate)
    
        self.gameTemplate = self.loadData(gTemplate)
        
        if path.exists(self.pFile):
            self.profiles = self.loadData(self.pFile)
        else:
            self.profiles["Template_Profile"] = self.profileTemplate
            self.writeData(self.pFile, self.profiles)

        if path.exists(self.gFile):
            self.games = self.loadData(self.gFile)
            self.nextGameID = len(self.games) + 1
        
    def loadData(self, file):
        with open(file, "r") as read_file:
            return json.load(read_file)
        
    def writeData(self, file, dict):
        result = False
        try:
            with open(file, 'w') as json_file:  
                json.dump(dict, json_file, indent=4)
            result = True
        except:
            result = False
        return result
    
    def getProfileNameList(self):
        nameList = ['-']
        
        for name in self.profiles:
            nameList.append(name)
        
        return nameList

    
    def getShortProfileText(self):
        txt = ""
        
        for name in self.profiles:
            txt += "[b][size=32][color=00A0FF]{}[/color][/size][/b]\n".format(name)
            txt += "  X01 avg: {}\n".format(round(self.profiles[name]["Stats"]["X01"]["OverallAvg"],2))
            
        return txt
    
    def getProfile(self, name):
        
        profile = copy.deepcopy(self.profiles[name])
        
        return profile
    
    def updateProfile(self, profiles2Update):
        
        for prof in profiles2Update:
            if prof['Name'] in self.profiles.keys():
                self.profiles[prof['Name']] = copy.deepcopy(prof)
        
        self.writeData(self.pFile, self.profiles)
        
    def addProfile(self, name):
        
        if "Template_Profile" in self.profiles:    
            del self.profiles["Template_Profile"]
        
        if name in self.profiles:
            print("Profile already exists with name: ", name)
            return False
        else:
            profileToAdd = copy.deepcopy(self.profileTemplate)
            profileToAdd["Name"] = name
            self.profiles[name] = profileToAdd
            self.writeData(self.pFile, self.profiles)
            return True
    
    def addGame(self, gameToAdd):
        self.games.append(gameToAdd)
        
        self.writeData(self.gFile, self.games)
        self.nextGameID = len(self.games) + 1
        
    def getGame(self, ID):
        pass
    
    def getGameShortText(self):
        pass
    
    def getGameIDList(self):
        pass
    