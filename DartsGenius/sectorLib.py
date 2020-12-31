'''
Created on Jun 8, 2020

@author: delpi
'''

from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty,\
ObjectProperty,StringProperty,ListProperty, BooleanProperty, DictProperty
from kivy.clock import Clock
import math
from functools import partial


mouseoverUpperLineRatio = 120/144
normalUpperLineRatio = 134/144

mouseoverTripleLineRatio = 96/144
normalTripleLineRatio = 84/144

handicapLowerLineRatio = 72/144
normalLowerLineRatio = 74/144

handicapBullLineRatio = 48/144
normalBullLineRatio = 20/144

handicapBullsEyeLineRatio = 24/144
normalBullsEyeLineRatio = 10/144

class LabelB(Label):
    bcolor = ListProperty([1,1,1,1])


class Sector(Widget):
    baseAngle = NumericProperty(0)
    score = NumericProperty(0)
    
    lowerSectorColor = ListProperty([0,0,0,1])
    upperSectorColor = ListProperty([0,0,0,1])
    doubleColor = ListProperty([.9,0,0,.9])
    tripleColor = ListProperty([.9,0,0,.9])
    
    isLowerSectorPressed = BooleanProperty(False)
    isUpperSectorPressed = BooleanProperty(False)
    isTriplePressed = BooleanProperty(False)
    isDoublePressed = BooleanProperty(False)
    
    pressTime = NumericProperty(0.25)
    
    windowBoardRatio = NumericProperty(0.8)
    
    boardLineRatio = NumericProperty(1)
    upperLineRatio = NumericProperty(134/144)
    tripleLineRatio = NumericProperty(84/144)
    lowerLineRatio = NumericProperty(74/144)
    bullLineRatio = NumericProperty(20/144)
    
    boardDia = NumericProperty(0)
    
    
    def resetPress(self, boolVar, *largs):
        if boolVar == 0:
            self.isLowerSectorPressed = False
            self.isUpperSectorPressed = False
        elif boolVar == 1:
            self.isDoublePressed = False
        elif boolVar == 2:
            self.isTriplePressed = False
        else:
            pass
        
        return True
    
    def determineScore(self, dist, angle):
        score = -1
        boardSize = min(self.parent.width, self.parent.height)/2*self.windowBoardRatio
        
        if dist <= boardSize and dist > boardSize*self.bullLineRatio:
            
            if angle <= self.baseAngle+9 and angle > self.baseAngle-9:
                score = self.score          
            elif angle > 351 and (self.baseAngle-9)<0:
                score = self.score          
            else:
                pass
            
            if score >= 0:
                if dist >= boardSize*self.upperLineRatio:
                    score *= 2
                    self.isDoublePressed = True
                    Clock.schedule_once(partial(self.resetPress,1), self.pressTime)
                    App.get_running_app().currGame.pushForwardGame(score,'{}D'.format(self.score))
                elif dist <= boardSize*self.tripleLineRatio and dist > boardSize*self.lowerLineRatio:
                    score *=3
                    self.isTriplePressed = True
                    Clock.schedule_once(partial(self.resetPress,2), self.pressTime)
                    App.get_running_app().currGame.pushForwardGame(score,'{}T'.format(self.score))
                else:
                    
                    if dist > boardSize*self.tripleLineRatio:
                        self.isUpperSectorPressed = True
                        App.get_running_app().currGame.pushForwardGame(score,'{}U'.format(self.score))
                    else:
                        self.isLowerSectorPressed = True
                        App.get_running_app().currGame.pushForwardGame(score,'{}L'.format(self.score))
                    Clock.schedule_once(partial(self.resetPress,0), self.pressTime)
            
            
            else:
                pass
                
        return score
    
    def on_touch_down(self, touch):
        xpos = touch.x - self.parent.center_x
        ypos = touch.y - self.parent.center_y
        dist = math.sqrt((self.parent.center_x - touch.x)**2 + (self.parent.center_y - touch.y)**2)
        
        if xpos != 0:
            angle = math.atan(ypos/xpos)*180/math.pi 
            
            if xpos>0:
                angle = 90 - angle
            else:
                angle = 270 - angle
                
        else:
            if ypos>0:
                angle = 0
            else:
                angle = 180
                
        
                
        self.determineScore(dist, angle)
     
            
        return Widget.on_touch_down(self, touch)
    
class BullSector(Widget):
    windowBoardRatio = NumericProperty(0.8)
    
    bullLineRatio = NumericProperty(20/144)
    bullsEyeLineRatio = NumericProperty(10/144)
    
    bullColor = ListProperty([.9,0,0,.9])
    bullsEyeColor = ListProperty([.9,0,0,.9])
    
    isBullPressed = BooleanProperty(False)
    isBullsEyePressed = BooleanProperty(False)
    
    pressTime = NumericProperty(0.25)
    
    def resetPress(self, boolVar, *largs):
        if boolVar == 0:
            self.isBullPressed = False
        elif boolVar == 1:
            self.isBullsEyePressed = False

        else:
            pass
        
        return True
    
    def on_touch_down(self, touch):
        boardSize = min(self.parent.width, self.parent.height)/2*self.windowBoardRatio
        dist = math.sqrt((self.parent.center_x - touch.x)**2 + (self.parent.center_y - touch.y)**2)
        
        if dist <= boardSize*self.bullLineRatio and dist > boardSize*self.bullsEyeLineRatio:     
                self.isBullPressed = True
                App.get_running_app().currGame.pushForwardGame(25,'B')
                Clock.schedule_once(partial(self.resetPress,0), self.pressTime)   
                
        elif dist <= boardSize*self.bullsEyeLineRatio:  
                self.isBullsEyePressed = True
                App.get_running_app().currGame.pushForwardGame(50,'DB')
                Clock.schedule_once(partial(self.resetPress,1), self.pressTime)         
        else:
            pass
        
        return Widget.on_touch_down(self, touch)

class BlackSector(Widget):
    windowBoardRatio = NumericProperty(0.8)
    
    blackColor = ListProperty([0,0,0,.9])
    
    isBlackPressed = BooleanProperty(False)
    
    pressTime = NumericProperty(0.25)
    
    def resetPress(self, dt):
        self.isBlackPressed = False
        
        return True
    
    def on_touch_down(self, touch):
        boardSize = min(self.parent.width, self.parent.height)/2*self.windowBoardRatio
        dist = math.sqrt((self.parent.center_x - touch.x)**2 + (self.parent.center_y - touch.y)**2)
        
        if dist <= min(self.parent.width, self.parent.height)/2 and dist > boardSize:        
                self.isBlackPressed = True
                App.get_running_app().currGame.pushForwardGame(0,'M')
                Clock.schedule_once(self.resetPress, self.pressTime)         
        else:
            pass
        
        return Widget.on_touch_down(self, touch)


class StatsSector(Sector):
    
    
    def __init__(self, **kwargs):
        super(StatsSector, self).__init__(**kwargs) 
        Window.bind(mouse_pos=self.mouse_pos)

    def mouse_pos(self, window, pos):
        xpos = pos[0] - self.parent.center_x
        ypos = pos[1] - self.parent.center_y
        dist = math.sqrt((self.parent.center_x - pos[0])**2 + (self.parent.center_y - pos[1])**2)
        boardSize = min(self.parent.width, self.parent.height)/2*self.windowBoardRatio
        
        dart = ''
        dartRatio = ''
        dartNum = ''
        
        
        if xpos != 0:
            angle = math.atan(ypos/xpos)*180/math.pi 
            
            if xpos>0:
                angle = 90 - angle
            else:
                angle = 270 - angle      
        else:
            if ypos>0:
                angle = 0
            else:
                angle = 180
        
        try:
            numDoubles = App.get_running_app().currGameStat['OverallSectorStats']['{}D'.format(self.score)]
        except:
            numDoubles = 0   
            
        try:
            numTriples = App.get_running_app().currGameStat['OverallSectorStats']['{}T'.format(self.score)]
        except:
            numTriples = 0  
            
        try:
            numUppers = App.get_running_app().currGameStat['OverallSectorStats']['{}U'.format(self.score)]
        except:
            numUppers = 0  
            
        try:
            numLowers = App.get_running_app().currGameStat['OverallSectorStats']['{}L'.format(self.score)]
        except:
            numLowers = 0   
        
        try:
            dt = App.get_running_app().currGameStat['DartsThrown']
        except:
            dt = 1
        
        if ((angle <= self.baseAngle+9 and angle > self.baseAngle-9) or (angle > 351 and (self.baseAngle-9)<0)) and dist < boardSize :
            
            #Double sector
            if dist <= boardSize and dist > boardSize*134/144:
                dart = '[b]Double {}[/b]'.format(self.score)
                dartNum = str(numDoubles)
                dartRatio = '{}%'.format(round(100* numDoubles/dt ,1))
                
                self.boardLineRatio = 149/144
                self.upperLineRatio = 129/144
                self.tripleLineRatio = 84/144
                self.lowerLineRatio = 74/144
                self.doubleColor[3] = .8
            
            #Upper sector   
            elif dist <= boardSize*134/144 and dist > boardSize*84/144:
                dart = '[b]Upper {}[/b]'.format(self.score)
                dartNum = str(numUppers)
                dartRatio = '{}%'.format(round(100* numUppers/ dt,1))
                self.boardLineRatio = 1
                self.upperLineRatio = 139/144
                self.tripleLineRatio = 79/144
                self.lowerLineRatio = 74/144
                self.upperSectorColor[3] = .8
             
            #Triple sector   
            elif dist <= boardSize*84/144 and dist > boardSize*74/144:
                dart = '[b]Triple {}[/b]'.format(self.score)
                dartNum = str(numTriples)
                dartRatio = '{}%'.format(round(100* numTriples/ dt,1))
                self.boardLineRatio = 1
                self.upperLineRatio = 134/144
                self.tripleLineRatio = 89/144
                self.lowerLineRatio = 69/144
                self.tripleColor[3] = .8
            
            #Lower sector   
            elif dist <= boardSize*74/144 and dist > boardSize*20/144:
                dart = '[b]Lower {}[/b]'.format(self.score)
                dartNum = str(numLowers)
                dartRatio = '{}%'.format(round(100* numLowers/ dt,1))
                self.boardLineRatio = 1
                self.upperLineRatio = 134/144
                self.tripleLineRatio = 84/144
                self.lowerLineRatio = 79/144
                self.lowerSectorColor[3] = .8
                
            else:
                pass
            
            App.get_running_app().root.ids.gss.statText = dart + '\n' + dartNum + ' of ' + str(dt) + ' throws\n' + dartRatio
        
        else:
            self.boardLineRatio = 1
            self.upperLineRatio = 134/144
            self.tripleLineRatio = 84/144
            self.lowerLineRatio = 74/144
            self.doubleColor[3] = 1
            self.upperSectorColor[3] = 1
            self.tripleColor[3] = 1
            self.lowerSectorColor[3] = 1
         
            
class StatsBullSector(BullSector):
    def __init__(self, **kwargs):
        super(StatsBullSector, self).__init__(**kwargs)
        
        Window.bind(mouse_pos=self.mouse_pos)

    def mouse_pos(self, window, pos):
        boardSize = min(self.parent.width, self.parent.height)/2*self.windowBoardRatio
        dist = math.sqrt((self.parent.center_x - pos[0])**2 + (self.parent.center_y - pos[1])**2)
        dart = ''
        dartRatio = ''
        dartNum = ''
        
        try:
            numBulls = App.get_running_app().currGameStat['OverallSectorStats']['B']
        except:
            numBulls = 0   
            
        try:
            numBullseyes = App.get_running_app().currGameStat['OverallSectorStats']['DB']
        except:
            numBullseyes = 0  
            
        try:
            dt = App.get_running_app().currGameStat['DartsThrown']
        except:
            dt = 1
        
        if dist <= boardSize*20/144 and dist > boardSize*10/144:     
            dart = '[b]Bull[/b]'
            dartNum = str(numBulls)
            dartRatio = '{}%'.format(round(100* numBulls/ App.get_running_app().currGameStat['DartsThrown'],1))  
                
        elif dist <= boardSize*10/144:  
            dart = '[b]BullsEye[/b]'
            dartNum = str(numBullseyes)
            dartRatio = '{}%'.format(round(100* numBullseyes/ App.get_running_app().currGameStat['DartsThrown'],1))  
               
        else:
            pass
        
        if dist <= boardSize*20/144:
            App.get_running_app().root.ids.gss.statText = dart + '\n' + dartNum + ' of ' + str(dt) + ' throws\n' + dartRatio

class StatsBlackSector(BlackSector):
    def __init__(self, **kwargs):
        super(StatsBlackSector, self).__init__(**kwargs)
        
        Window.bind(mouse_pos=self.mouse_pos)

    def mouse_pos(self, window, pos):
        
        App.get_running_app().root.ids.gss.ids.statLabel.pos = [pos[0]-self.parent.center_x/2 + 100, pos[1]-self.parent.center_y - 90]
        
        boardSize = min(self.parent.width, self.parent.height)/2*self.windowBoardRatio
        dist = math.sqrt((self.parent.center_x - pos[0])**2 + (self.parent.center_y - pos[1])**2)
        
        try:
            numMisses = App.get_running_app().currGameStat['OverallSectorStats']['M']
        except:
            numMisses = 0
        
        try:
            dt = App.get_running_app().currGameStat['DartsThrown']
        except:
            dt = 1
            
        if dist <= min(self.parent.width, self.parent.height)/2 and dist > boardSize:  
            dart = '[b]Miss/Bust[/b]'      
            dartRatio = '{}%'.format(round(100* numMisses/ dt,1))
            App.get_running_app().root.ids.gss.statText = dart + '\n' + str(numMisses) + ' of ' + str(dt) + ' throws\n' + dartRatio
            App.get_running_app().root.ids.gss.ids.statLabel.bcolor = [1, 1, 1, .5]
                 
        elif dist > min(self.parent.width, self.parent.height)/2:
            App.get_running_app().root.ids.gss.statText = ''
            App.get_running_app().root.ids.gss.ids.statLabel.bcolor = [1, 1, 1, 0]
            
        else:
            pass
        
class StatsBoard(Widget):
    pass

