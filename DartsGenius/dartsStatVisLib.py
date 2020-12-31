'''
Created on Jun 3, 2020

@author: delpi
'''

colorPalette = ['#00876c','#3d9c73','#63b179','#88c580','#aed987','#d6ec91','#ffff9d','#fee17e','#fcc267','#f7a258','#ef8250','#e4604e','#d43d51']


def createLimitList(sectorDict):
    
    '''
    The Vehicle object contains a lot of vehicles

    Args:
        arg (str): The arg is used for...
        *args: The variable arguments are used for...
        **kwargs: The keyword arguments are used for...

    Attributes:
        arg (str): This is where we store arg,
    '''
    
    limits = []
    highest = 0
    
    # Get the highest number - most throws on a sector
    for keys in sectorDict:
        if sectorDict[keys] > highest:
            highest = sectorDict[keys]
    
    colorRange = len(colorPalette)
    for index in range(colorRange):
        limits.append(highest/colorRange*index)
    return limits


def getColor4Rate(limitList, occuranceRate):
    
    for ind in range(len(limitList)):
        if limitList[ind] > occuranceRate:
            break
        
    return colorPalette[ind]


def getGameStatText(name,gameType,db):
    txt = ''
    
    if gameType == 'X01':
        txt += '[b][size=32][color=00A0FF]{}[/color][/size][/b]\n'.format(name)
        txt += '[b]Darts thrown:[/b] {}\n'.format(db['DartsThrown'])
        txt += '[b]Darts for checkout:[/b] {}\n'.format(db['DartsForCheckout'])
        txt += '[b]Legs played:[/b] {}\n'.format(db['LegsPlayed'])
        txt += '[b]Legs won:[/b] {}\n'.format(db['LegsWon'])
        txt += '[b]Average:[/b] {}\n'.format(round(db['OverallAvg'],2))
        txt += '[b]First 9 Average:[/b] {}\n'.format(round(db['First9Avg'],2))
        txt += '[b]Best leg average:[/b] {}\n'.format(round(db['BestLegAvg'],2))
        txt += '[b]60+:[/b] {}\n'.format(db['60+'])
        txt += '[b]100+:[/b] {}\n'.format(db['100+'])
        txt += '[b]140+:[/b] {}\n'.format(db['140+'])
        txt += '[b]180:[/b] {}\n'.format(db['180'])
        txt += '[b]Highest Finish:[/b] TBD\n'
    else:
        pass
    
    return txt



