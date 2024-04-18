import xml.etree.ElementTree as ET
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(filename='myapp.log',level=logging.INFO)

import itertools


class Buff():
    buffTypes = ["ROUND","AURA","ONCE"]
    _ROUND_END = "ROUND"
    _AURA = "AURA"
    _ONCE = "ONCE"
    # round = until round ends
    # aura, until the owner is in the battlefield
    # once, only happens once (cleanse, 
    def __init__(self,source,buffType,adjAttack=0,adjDefense=0,adjCost=0,addKeywords=[],removeKeywords=[]):
        self.adjAttack = adjAttack
        self.adjDefense = adjDefense
        self.adjCost = adjCost
        self.addKeywords = addKeywords
        self.removeKeywords = removeKeywords
        self.source = source
        self.buffType = buffType
        
        pass
class Actionable():
    # Parent to Card  and Skill
    # Performs an action in the game
    id_iter = itertools.count()
    def __init__(self,owner,*args,**kwargs):
        self.id = next(Actionable.id_iter)
        self.owner = owner
    def onPlayed(self):
        pass
    
class Card(Actionable):
    # Is playable by the player
    # Parent to Unit, Landmark and Spell
    def __init__(self,owner,cardElement=None,*args,**kwargs):
        self.BaseCost = int(cardElement.find('Cost').text)
        self.BaseKeywords = (cardElement.find('Keywords').text).strip('][').split(',')
        self.BaseRegions = (cardElement.find('Region').text).strip('][').split(',')
        self.Rarity = cardElement.find('Rarity').text
        self.ID = cardElement.find('ID').text
        self.Expansion = cardElement.find('Expansion').text
        self.Name = cardElement.find('Name').text
        self.Cost = self.BaseCost # The current cost of the card
        self.RawCost = self.BaseCost
        
        self.Keywords = self.BaseKeywords
        self.Regions = self.BaseRegions
        self.Buffs = []
        
        super().__init__(owner,*args,**kwargs)
    def addBuff(self,buff):
        self.adjCost(self.Cost + buff.adjCost)
        self.addKeyWords(buff.addKeyWords)
        self.removeKeywords(buff.removeKeywords)
        self.Buffs.append(buff)
    def __str__(self):
        return self.Name
    def adjValueMinMax(self,value,adj,minVal,maxVal=30000):
        # if value +adj < min return (min,min-value)
        # if value+adj > max return (max,max-value)
        # if value+adj within min and max (value+adj,adj
        
        newValue = value + adj
        if newValue < minVal:
            changed = minVal-value
            excessValue = adj-changed
            newValue = minVal

        elif newValue > maxVal:
            changed = maxVal-value
            excessValue = adj-changed
            newValue = maxVal
        else:
            excessValue = 0
            changed = newValue - value
        return newValue,changed,excessValue
    def adjCost(self,costChange):
        self.Cost,x,y = self.adjValueMinMax(self.Cost, costChange, 0)
        
    def onDiscard(self): # called when card is discarded from hand
        pass
    def isKeyword(self,kw):
        return (kw in self.Keywords)
    def addKeywords(self,addKeywords):
        for kw in addKeywords:
            if kw not in self.Keywords:
                self.Keywords.append(kw)
                
    def removeKeywords(self,removeKeywords):
        for kw in removeKeywords:
            if kw in self.Keywords:
                self.Keywords.remove(kw)
        
class Unit(Card):
    # Has attributes: attack, defense,
    # onDeath, onSummoned
    def __init__(self,owner,cardID,*args,**kwargs):
        tree = ET.parse('Cards.xml')
        root = tree.getroot()
        cardElement = None
        for ele in root[0].findall('Card'):
            if ele.find('CardID').text == cardID:
                cardElement = ele
                pass

        self.Subtype = cardElement.find('UnitType').text
        self.Type = 'Unit'

        
        # Defense Points
        self.BaseDefense = int(cardElement.find('Defense').text) # The base defense of the card itself
        self.Defense = self.BaseDefense # the current defense (cannot be less than 0)
        self.RawDefense = self.BaseDefense # the defense if defense could go below 0
        self.MaxDefense = self.BaseDefense
        
        self.BaseAttack = int(cardElement.find('Attack').text)
        self.Attack = self.BaseAttack
        self.RawAttack = self.BaseAttack
        self.MaxAttack = self.BaseAttack
        
        
        self.BaseFamilies = (cardElement.find('Families').text).strip('][').split(',')
        self.Families = self.BaseFamilies
        
        self.TotalDamageTaken = 0
        self.TotalHealedDamage = 0
        
        super().__init__(owner,cardElement,*args,**kwargs)
        
        logger.info("New Card Created")
    def __str__(self):
        return self.Name
    def addBuff(self,buff):
        self.adjStats(buff.adjAttack, buff.adjDefense)
        super.addBuff(self,buff)
    def onDeath(self): #called when unit dies
        pass
    def onDamaged(self):
        pass
    def onAttack(self):
        pass
    def onStrike(self):
        pass
    def onSummoned(self,player):
        logger.info(str(self) + ' has been summoned by ' + str(player))
        pass
    def onBlock(self):
        pass
    def getValueString(self,currentVal,maxVal,rawVal,baseVal):
        outStr = str(currentVal) + '/' + str(maxVal) + ' raw:' + str(rawVal) + ', ' + 'base:' + str(baseVal)
        
        return outStr
    def getStatsStr(self,breakChar='\n'):
        costStr = 'Cost: ' + self.getValueString(self.Cost, 'None', self.RawCost, self.BaseCost)
        atkStr = 'Attack: ' + self.getValueString(self.Attack, self.MaxAttack, self.RawAttack, self.BaseAttack)
        defStr = 'Defense: ' + self.getValueString(self.Defense, self.MaxDefense, self.RawDefense, self.BaseDefense)
        
        kwStr = 'Keywords: ' + str(self.Keywords)
        nameStr = self.Name
        return nameStr + breakChar + costStr+ breakChar +atkStr+ breakChar +defStr+ breakChar +kwStr
    
# tak
    def takeDamage(self,dmg):
        # Adjusts Defense and RawDefense but not MaxDefense
        # dmg > 0
        if 'Tough' in self.Keywords:
            if dmg > 1:
                dmg = dmg-1
            if dmg <= 0:
                dmg = 0
        self.Defense,dmgTaken,excessDmg = self.adjValueMinMax(self.Defense, -dmg, 0)
        self.TotalDamageTaken = self.TotalDamageTaken + dmgTaken
        return self.Defense,dmgTaken,excessDmg
        
    def heal(self,healAmt):
        # Adjusts Defense and RawDefense but not MaxDefense
        self.RawDefense,x,y =self.adjValueMinMax(self.RawDefense, healAmt, 0,self.MaxDefense)
        self.Defense,healAmt,excessHealing = self.adjValueMinMax(self.Defense, healAmt, 0,self.MaxDefense)
        logging.info("Healed for" + str(healAmt) + ' with excess: ' + str(excessHealing))
        return self.Defense,healAmt,excessHealing
            
    def adjStats(self,atkChange,defChange):
        # used when buffing the unit
        # get +-x|+-y
        # changes both defense/maxdefense and atk/maxatk
        self.MaxDefense,x,y = self.adjValueMinMax(self.MaxDefense, defChange, 0)
        self.Defense,x,y = self.adjValueMinMax(self.Defense, defChange, 0, self.MaxDefense)
        
        self.MaxAttack,x,y = self.adjValueMinMax(self.MaxAttack, atkChange, 0)
        self.Attack,x,y = self.adjValueMinMax(self.Attack, atkChange, 0, self.MaxAttack)
        

    def isDamaged(self):
        return (self.MaxDefense > self.Defense )

    def addKeyWord(self,keyword):
        if keyword not in self.Keywords:
            self.Keywords.append(keyword)
            return True
        else:
            return False
class Spell(Card):
    def __init__(self,CardID,Owner):
        tree = ET.parse('Cards.xml')
        root = tree.getroot()
        
        for ele in root[1].findall('Card'):
            if ele.find('Name').text == CardID:
                cardElement = ele
                pass
        Card.__init__(self, cardElement,Owner)
        
        pass