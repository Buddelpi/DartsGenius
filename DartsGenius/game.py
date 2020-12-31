'''
Created on Mar 24, 2020

@author: delpi
'''

import copy
import datetime as dt

profileTemp = {
"Name" : "Template_Profile",
"Games" : {
    "X01" : [],
    "Cricket" : [],
    "Bobs27" : [],
    "Sector" : [] 
    },
"Stats" : {
    "X01" : {
        "DartsThrown" : 0,
        "DartsForCheckout" : 0,
        "GamesPlayed" : 0,
        "GamesWon" : 0,
        "LegsPlayed" : 0,
        "LegsWon" : 0,
        "60+" : 0,
        "100+" : 0,
        "140+" : 0,
        "180" : 0,
        "OverallAvg" : 0,
        "First9Avg" : 0,
        "BestGameAvg" : 0,
        "BestLegAvg" : 0,
        "OverallSectorStats" : {
        },
        "OverallDartStats" : {
        },
        "OverallRoundStats" : {
        }
        }
    }
}

gameTemp = {
    "ID" : "",
    "DateTime" : "",
    "Players" : [],
    "GameType" : "",
    "Winner" : "",
    "PlayerAVG" : [],
    "PlayByPlay" : []
    }

legTemp = {
    "Leg" : "",
    "Winner" : "",
    "RoundsInLeg" : 0,
    "StarterOfLeg": "",
    "PbP" : []
    }

class Game():
    
    
    def __init__(self, playerList, gameType, numOfSets, numOfLegs, gameID):
        
        self.possibleGameStates = ["GameOn", "GameEnd", "DBCopiedAfterGameEnd"]
        self.gameState = "GameOn"
        self.gameType = gameType
        self.numOfLegs = numOfLegs
        self.numOfSets = numOfSets
        self.playerList = playerList
        self.gameID = "ID_{}".format(str(int(gameID)))
        self.numPlayers = len(self.playerList)
        
        self.currRound = 1
        self.currSet = 1
        self.currLeg = 1
        self.currDart = 1
        self.currPlayerIndex = 0
        self.currStarterIndex = 0
        
        self.currRoundPbP = []
        self.currLegPbP = []
        
        self.gameStats = copy.deepcopy(gameTemp)
        self.gameStats["ID"] = self.gameID
        self.gameStats["DateTime"] = dt.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        self.gameStats["GameType"] = "{}_S{}_L{}".format(self.gameType,int(self.numOfSets),int(self.numOfLegs))
        for player in self.playerList:
            self.gameStats["Players"].append(player.name)
        
        self.legStats = copy.deepcopy(legTemp)
        
        self.waitForConfirm = 'NoConfirmNeeded'
        
        
    def pushForwardGame(self, scoreToAdd, sect):
        if self.gameType == '501':
            
            if self.gameState == "GameOn" and self.waitForConfirm == 'NoConfirmNeeded':
                
                if self.currDart <= 3:
                    
                    throwResult = self.checkRule(scoreToAdd, sect)
                    
                    if throwResult == 'Normal':
                    
                        self.currDart += 1
                        
                        if (self.currDart > 3):
                            self.currDart = 3
                            self.waitForConfirm = 'Normal'
                        else:
                            pass
                        
                    elif throwResult == 'Bust':
                        self.waitForConfirm = 'Bust'
                        
                    else: #win
                        self.waitForConfirm = 'Win'

                        
                    
    def nextPlayer(self):
        self.currPlayerIndex += 1
        self.currDart = 1
        if self.currPlayerIndex > self.numPlayers-1:
            self.currPlayerIndex = 0
            
        if self.currPlayerIndex == self.currStarterIndex:
            self.currRound += 1
            self.currLegPbP.append(copy.deepcopy(self.currRoundPbP))

            
    def nextLeg(self):
        if self.gameType == '501':
            
            self.currLegPbP.append(copy.deepcopy(self.currRoundPbP))
            self.appendGameLegStats()
            self.currRoundPbP.clear()
            self.currLegPbP.clear()
            
            self.currRound = 1
            self.currDart = 1
            self.currLeg += 1
            self.resetAllPlayersScore()
            
            self.playerList[self.currPlayerIndex].legsWon += 1
            
            for index in range(self.numPlayers):
                if index == self.currPlayerIndex:
                    self.playerList[index].legUpdateStats(True)
                else:
                    self.playerList[index].legUpdateStats(False)    
                self.playerList[index].legAvg = 0
                self.playerList[index].legDT = 0
                
            if self.playerList[self.currPlayerIndex].legsWon == self.numOfLegs:
                
                self.resetAllPlayersLegs()
                
                self.playerList[self.currPlayerIndex].setsWon += 1
                self.currSet += 1
                print('WINNER of Set is {}'.format(self.playerList[self.currPlayerIndex].name ))
                
                if self.playerList[self.currPlayerIndex].setsWon == self.numOfSets:
                    print('WINNER of Game is {}'.format(self.playerList[self.currPlayerIndex].name ))
                    
                    for index in range(self.numPlayers):
                        if index == self.currPlayerIndex:
                            self.playerList[index].gameUpdateStats(True)
                        else:
                            self.playerList[index].gameUpdateStats(False)    
                        
                        self.playerList[index].updatePlayerDB(self.gameID)
                        
                    self.finalizeGameStats(self.playerList[self.currPlayerIndex].name )
                    self.gameState = 'GameEnd'
                    
            self.updateStarterOfLeg()
    
    def resetAllPlayersScore(self):
        for player in self.playerList:
            player.gameScore += player.currentScoreToShow
            player.currentScore = 0
            player.currentScoreToShow = 0
            player.flushScore()
     
    def resetAllPlayersLegs(self):
        for player in self.playerList:
            player.legsWon = 0   
        self.currLeg = 1  
    
    def updateStarterOfLeg(self):
        self.currStarterIndex +=1 
                    
        if self.currStarterIndex == self.numPlayers:
            self.currStarterIndex = 0
        
        self.currPlayerIndex = self.currStarterIndex
        
            
    def checkRule(self, scoreToAdd,sector):
        
        self.playerList[self.currPlayerIndex].currentRoundScore.append(scoreToAdd)
        self.playerList[self.currPlayerIndex].currentRoundSectorScore.append(sector)
        self.playerList[self.currPlayerIndex].currentScoreToShow += scoreToAdd        
        if self.gameType == '501':
            if self.playerList[self.currPlayerIndex].currentScoreToShow > 501 or self.playerList[self.currPlayerIndex].currentScoreToShow == 500:
                
                for ind in range(len(self.playerList[self.currPlayerIndex].currentRoundSectorScore)):
                    self.playerList[self.currPlayerIndex].currentRoundSectorScore[ind] = 'M'
                    self.playerList[self.currPlayerIndex].currentRoundScore[ind] = 0
                print('BUST - to much ')
                return 'Bust'
            else:
                
                print('Player is {}, dart {} in round {}, leg {}, set {}, score: {}, {}'.format(self.playerList[self.currPlayerIndex].name, \
                                                                self.currDart, self.currRound, self.currLeg, self.currSet, scoreToAdd,\
                                                                self.playerList[self.currPlayerIndex].currentScoreToShow))
    
                
                if self.playerList[self.currPlayerIndex].currentScoreToShow == 501:
                    
                    if 'D' in sector:
                        print('WINNER of Leg is {}'.format(self.playerList[self.currPlayerIndex].name ))
                        return 'Win'
                    else:
                        for ind in range(len(self.playerList[self.currPlayerIndex].currentRoundSectorScore)):
                            self.playerList[self.currPlayerIndex].currentRoundSectorScore[ind] = 'M'
                            self.playerList[self.currPlayerIndex].currentRoundScore[ind] = 0
                        print('BUST - Not double')
                        return 'Bust'
                
                else:
                    return 'Normal'
                    
           
    def undoLastThrow(self):
        
        if self.waitForConfirm == 'NoConfirmNeeded':
            if self.currDart > 1:
                self.currDart -= 1
                scoreToUndo = self.playerList[self.currPlayerIndex].currentRoundScore.pop()
                self.playerList[self.currPlayerIndex].currentRoundSectorScore.pop()
                self.playerList[self.currPlayerIndex].currentScoreToShow -= scoreToUndo
    
        else:
            scoreToUndo = self.playerList[self.currPlayerIndex].currentRoundScore.pop()
            self.playerList[self.currPlayerIndex].currentRoundSectorScore.pop()
            self.playerList[self.currPlayerIndex].currentScoreToShow -= scoreToUndo
            self.waitForConfirm = 'NoConfirmNeeded'

        
    def confirmThrow(self):      
        
        self.playerList[self.currPlayerIndex].roundUpdateStats(self.waitForConfirm, self.currDart) 
        self.currRoundPbP.append(self.playerList[self.currPlayerIndex].currentRoundSectorScore)
        
        if self.waitForConfirm == 'Normal':
            self.playerList[self.currPlayerIndex].currentScore += self.playerList[self.currPlayerIndex].flushScore()
            self.playerList[self.currPlayerIndex].currentScoreToShow = self.playerList[self.currPlayerIndex].currentScore
            self.playerList[self.currPlayerIndex].checkRoundForCheckout()
            self.playerList[self.currPlayerIndex].legDT += 3
            self.playerList[self.currPlayerIndex].legAvg = self.playerList[self.currPlayerIndex].currentScore / self.playerList[self.currPlayerIndex].legDT
            self.playerList[self.currPlayerIndex].gameDT += 3
            self.playerList[self.currPlayerIndex].gameAvg = (self.playerList[self.currPlayerIndex].gameScore + self.playerList[self.currPlayerIndex].currentScore )/ self.playerList[self.currPlayerIndex].gameDT
            self.nextPlayer()

            
        elif self.waitForConfirm == 'Bust':
            self.playerList[self.currPlayerIndex].flushScore()
            self.playerList[self.currPlayerIndex].legDT += self.currDart
            self.playerList[self.currPlayerIndex].legAvg = self.playerList[self.currPlayerIndex].currentScore / self.playerList[self.currPlayerIndex].legDT
            self.playerList[self.currPlayerIndex].gameDT += self.currDart
            self.playerList[self.currPlayerIndex].gameAvg = (self.playerList[self.currPlayerIndex].gameScore + self.playerList[self.currPlayerIndex].currentScore )/ self.playerList[self.currPlayerIndex].gameDT
            self.nextPlayer()
            
        elif self.waitForConfirm == 'Win':        
              
            self.playerList[self.currPlayerIndex].checkRoundForCheckout()
            self.playerList[self.currPlayerIndex].legDT += self.currDart
            self.playerList[self.currPlayerIndex].legAvg = 501 / self.playerList[self.currPlayerIndex].legDT
            self.playerList[self.currPlayerIndex].gameDT += self.currDart
            self.playerList[self.currPlayerIndex].gameAvg = (self.playerList[self.currPlayerIndex].gameScore + 501 )/ self.playerList[self.currPlayerIndex].gameDT
            
            self.nextLeg()
            self.playerList[self.currPlayerIndex].flushScore()
        
        self.waitForConfirm = 'NoConfirmNeeded'
    
    def appendGameLegStats(self):
        
        self.legStats["Leg"] = "S{}_L{}".format(int(self.currSet),int(self.currLeg))
        self.legStats["Winner"] = self.playerList[self.currPlayerIndex].name
        self.legStats["RoundsInLeg"] = self.currRound
        self.legStats["StarterOfLeg"] = self.playerList[self.currStarterIndex].name
        self.legStats["PbP"] =  self.currLegPbP
        
        self.gameStats["PlayByPlay"].append(copy.deepcopy(self.legStats))
    
    def finalizeGameStats(self,winner):
        
        gameAvg = []
        
        for player in self.playerList:
            playerAvg = []
            playerAvg.append(player.playerCurrentStats['X01']['First9Avg'])
            playerAvg.append(player.playerCurrentStats['X01']['OverallAvg'])
            gameAvg.append(playerAvg)
        
        self.gameStats["PlayerAVG"] = gameAvg
        self.gameStats["Winner"] = winner
        
class Player():

    
    def __init__(self, playerProfile):
            self.playerDB = playerProfile
            self.playerCurrentStats = copy.deepcopy(profileTemp['Stats'])
            self.name = playerProfile['Name']
            
            self.currentScore = 0
            self.gameScore = 0
            self.currentScoreToShow = 0
            self.isRoundForCheckout = False
            self.currentRoundScore = []
            self.currentRoundSectorScore = []
            self.legsWon = 0
            self.setsWon = 0
            
            self.legAvg = 0
            self.legDT = 0
            self.gameAvg = 0
            self.gameDT = 0
            self.totalScore = 0
            self.totalF9Score = 0
            self.totalF9DT = 0
    
    def roundUpdateStats(self, confirmType, dart):  
        
        #Darts Thrown, Darts For Checkout
        roundSum = 0
        for dartScore in self.currentRoundScore:
            roundSum += dartScore
            
        if confirmType == 'Normal':
            self.playerCurrentStats['X01']['DartsThrown'] += 3 
            if self.isRoundForCheckout:
                self.playerCurrentStats['X01']['DartsForCheckout'] += 3 
        elif confirmType == 'Bust':
            roundSum = 0
            self.playerCurrentStats['X01']['DartsThrown'] += dart
            if self.isRoundForCheckout:
                self.playerCurrentStats['X01']['DartsForCheckout'] += dart 
        elif confirmType == 'Win':
            self.playerCurrentStats['X01']['DartsThrown'] += dart
            if self.isRoundForCheckout:
                self.playerCurrentStats['X01']['DartsForCheckout'] += dart 
        else:
            pass
    
    
        #60+, 100+, 140+, 180
        if roundSum == 180:
            self.playerCurrentStats['X01']['180'] += 1
        elif roundSum >= 140:
            self.playerCurrentStats['X01']['140+'] += 1
        elif roundSum >= 100:
            self.playerCurrentStats['X01']['100+'] += 1
        elif roundSum >= 60:
            self.playerCurrentStats['X01']['60+'] += 1
        else:
            pass
        
        # Overall Avg, First 9 Avg  
        if (self.legDT + dart) <= 9:
            self.totalF9Score += roundSum
            self.totalF9DT += 3
            self.playerCurrentStats['X01']['First9Avg'] = self.totalF9Score / self.totalF9DT
        
        self.totalScore += roundSum
        self.playerCurrentStats['X01']['OverallAvg'] = self.totalScore / self.playerCurrentStats['X01']['DartsThrown']
        
        
        
        # OverallSectorStats
        for sect in self.currentRoundSectorScore:
            if str(sect) in self.playerCurrentStats['X01']['OverallSectorStats'].keys():
                self.playerCurrentStats['X01']['OverallSectorStats'][str(sect)] += 1
            else: 
                self.playerCurrentStats['X01']['OverallSectorStats'][str(sect)] = 1
        
        # OverallDartStats  
        for dart in self.currentRoundScore:
            if str(dart) in self.playerCurrentStats['X01']['OverallDartStats'].keys():
                self.playerCurrentStats['X01']['OverallDartStats'][str(dart)] += 1
            else: 
                self.playerCurrentStats['X01']['OverallDartStats'][str(dart)] = 1
            
        # OverallRoundStats
        if str(roundSum) in self.playerCurrentStats['X01']['OverallRoundStats'].keys():
            self.playerCurrentStats['X01']['OverallRoundStats'][str(roundSum)] += 1
        else: 
            self.playerCurrentStats['X01']['OverallRoundStats'][str(roundSum)] = 1 
               
    def checkRoundForCheckout(self):
        if (self.currentScore >= 331) and (self.currentScore not in [332,333,335,336,338,339,342]):
            self.isRoundForCheckout = True
        else:
            self.isRoundForCheckout = False
    
    def legUpdateStats(self, isWon):
        
        # legsPlayed, legsWon, bestLegAvg
        
        self.playerCurrentStats['X01']['LegsPlayed'] += 1
        
        if isWon:
            self.playerCurrentStats['X01']['LegsWon'] += 1
        else:
            pass
        
        if self.legAvg > self.playerCurrentStats['X01']['BestLegAvg']:
            self.playerCurrentStats['X01']['BestLegAvg'] = self.legAvg
        
    
    def gameUpdateStats(self,isWon):
        
        #gamesPlayed
        self.playerCurrentStats['X01']['GamesPlayed'] += 1
        
        #GamesWon
        if isWon:
            self.playerCurrentStats['X01']['GamesWon'] += 1
        else:
            pass
        
        #bestGameAvg
        if self.gameAvg > self.playerCurrentStats['X01']['BestGameAvg']:
            self.playerCurrentStats['X01']['BestGameAvg'] = self.gameAvg 
    
    def updatePlayerDB(self,gameID):
        
        oldDT = self.playerDB['Stats']['X01']['DartsThrown']
        oldDTf9 = self.playerDB['Stats']['X01']['LegsPlayed'] * 9
        
        #Add game ID
        self.playerDB['Games']['X01'].append(gameID)
        
        #DT
        self.playerDB['Stats']['X01']['DartsThrown'] += self.playerCurrentStats['X01']['DartsThrown']
        
        #DT for Checkout
        self.playerDB['Stats']['X01']['DartsForCheckout'] += self.playerCurrentStats['X01']['DartsForCheckout']
        
        #GamesPlayed
        self.playerDB['Stats']['X01']['GamesPlayed'] += self.playerCurrentStats['X01']['GamesPlayed']
        
        #GamesWon
        self.playerDB['Stats']['X01']['GamesWon'] += self.playerCurrentStats['X01']['GamesWon']
        
        #LegsPlayed
        self.playerDB['Stats']['X01']['LegsPlayed'] += self.playerCurrentStats['X01']['LegsPlayed']
        
        #LegsWon
        self.playerDB['Stats']['X01']['LegsWon'] += self.playerCurrentStats['X01']['LegsWon']
        
        #60+, 100+, 140+, 180
        self.playerDB['Stats']['X01']['60+'] += self.playerCurrentStats['X01']['60+']
        self.playerDB['Stats']['X01']['100+'] += self.playerCurrentStats['X01']['100+']
        self.playerDB['Stats']['X01']['140+'] += self.playerCurrentStats['X01']['140+']
        self.playerDB['Stats']['X01']['180'] += self.playerCurrentStats['X01']['180']
        
        #OverallAvg
        self.playerDB['Stats']['X01']['OverallAvg'] = (self.playerDB['Stats']['X01']['OverallAvg'] * oldDT + self.gameScore) / self.playerDB['Stats']['X01']['DartsThrown']
        
        #First9Avg
        self.playerDB['Stats']['X01']['First9Avg'] = (self.playerDB['Stats']['X01']['First9Avg'] * oldDTf9 + self.totalF9Score) / (oldDTf9 + self.totalF9DT)
        
        #BestGameAvg
        if self.playerCurrentStats['X01']['BestGameAvg'] > self.playerDB['Stats']['X01']['BestGameAvg']:
            self.playerDB['Stats']['X01']['BestGameAvg'] = self.playerCurrentStats['X01']['BestGameAvg']
            
        #BestLegAvg
        if self.playerCurrentStats['X01']['BestLegAvg'] > self.playerDB['Stats']['X01']['BestLegAvg']:
            self.playerDB['Stats']['X01']['BestLegAvg'] = self.playerCurrentStats['X01']['BestLegAvg']
            
            
        #OverallSectorStats
        
        for sectorStat in self.playerCurrentStats['X01']['OverallSectorStats'].keys():
            if sectorStat in self.playerDB['Stats']['X01']['OverallSectorStats']:
                self.playerDB['Stats']['X01']['OverallSectorStats'][sectorStat] += self.playerCurrentStats['X01']['OverallSectorStats'][sectorStat]
            else:
                self.playerDB['Stats']['X01']['OverallSectorStats'][sectorStat] = self.playerCurrentStats['X01']['OverallSectorStats'][sectorStat]
                
        #OverallDartStats
        for dartStat in self.playerCurrentStats['X01']['OverallDartStats'].keys():
            if dartStat in self.playerDB['Stats']['X01']['OverallDartStats']:
                self.playerDB['Stats']['X01']['OverallDartStats'][dartStat] += self.playerCurrentStats['X01']['OverallDartStats'][dartStat]
            else:
                self.playerDB['Stats']['X01']['OverallDartStats'][dartStat] = self.playerCurrentStats['X01']['OverallDartStats'][dartStat]
        
        #OverallRoundStats
        for roundStat in self.playerCurrentStats['X01']['OverallRoundStats'].keys():
            if roundStat in self.playerDB['Stats']['X01']['OverallRoundStats']:
                self.playerDB['Stats']['X01']['OverallRoundStats'][roundStat] += self.playerCurrentStats['X01']['OverallRoundStats'][roundStat]
            else:
                self.playerDB['Stats']['X01']['OverallRoundStats'][roundStat] = self.playerCurrentStats['X01']['OverallRoundStats'][roundStat]
        
            
    def flushScore(self):
        roundSum = 0
        
        for scr in self.currentRoundScore:
            roundSum += scr
            
        self.currentRoundScore = []
        self.currentRoundSectorScore = []
        self.currentScoreToShow = self.currentScore
        return roundSum
    
    
    