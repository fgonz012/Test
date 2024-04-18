'''
Created on Apr 17, 2024

@author: FG
'''

from collections.abc import Iterable
from random import randrange
from itertools import chain
from keyword import kwlist

import logging


logger = logging.getLogger(__name__)
logging.basicConfig(filename='myapp.log',level=logging.INFO)

class cardContainer(Iterable):
    def __init__(self,maxCards=9999):
        self.cardDict = {} # {card, (prev,next)} # top is last card, bottom is first card
        self.cnt = 0
        self.maxCards = maxCards
    def __iter__(self):
        self.n = 0
        return self
    def __next__(self):
        if self.n < self.cnt:
            self.n += 1
            return self.cardDict[self.n]
        else:
            raise StopIteration
    def __str__(self):
        return str([card.Name for card in self.cardDict.values()])


    
    def addCard(self,card,location=-1):# loc 0 = random, -1=top, 1 = bottom
        if self.cnt >= self.maxCards:
            return False
        if self.cnt == 0: # container is empty
            self.cardDict = {1:card}
        else:
            if location == 0: #random location
                location = randrange(1,self.cnt+1)
            elif location == -1: # top
                location = self.cnt+1
                
            
            if location == self.cnt+1: # location is at the top
                self.cardDict.update({self.cnt+1:card})
            else: # location is somewhere in the middle ( or 1 )
                self.cardDict.update({self.cnt+1:self.cardDict[self.cnt]}) # add another 1 at the end with the card from self.cnt
                for i in range(self.cnt,location,-1):
                    cardTemp = self.cardDict[i]
                    self.cardDict[i] = cardTemp
                self.cardDict[location] = card
                
        self.cnt = self.cnt +1
        return True
    def isFull(self):
        return self.cnt >= self.maxCards

    
    def getCard(self):
        if self.cnt==0:
            return None
        
        card = self.cardDict[self.cnt]
        del self.cardDict[self.cnt]
        self.cnt = self.cnt-1
        return card
    def findCard(self,CardID):
        for card in list(self.cardDict.values()):
            if card.CardID == CardID:
                return True
        return False
    def shuffle(self):
        pass
        
        
class Player:
    
    def __init__(self,Name,Health):
        self.Name = Name
        self.Health = Health
        self.MaxHealth = Health
        self.Deck = cardContainer()
        self.Graveyard = cardContainer()
        self.Hand = cardContainer(7)
        self.UnitMana = 0
        self.SpellMana = 0
        self.Backcourt = cardContainer(6)
        self.Attackcourt = cardContainer(7)
        logger.info(self.getReportStr())
    def __str__(self):
        return self.Name
        
    def addCardToDeck(self,card):
        card.Owner = self
        self.Deck.addCard(card, 0)
    def addCardToBackcourt(self,card):
        self.Backcourt.addCard(card, -1)
        return True
    def addUnitMana(self,amt):
        if self.UnitMana + amt > 10:
            self.UnitMana = 10
        else:
            self.UnitMana += amt
            
    def getUnitsInPlay(self):
        return chain(self.Backcourt,self.Attackcourt)
        
    def reshuffleCardBackToDeck(self,card):
        self.Deck.addCard(card, 0)
        
    def draw(self):
        card = self.Deck.getCard()
        if self.Hand.isFull():
            pass
            #ACTION TO ELIMINATE CARD
        else:
            self.Hand.addCard(card,-1)
            
    def getReportStr(self):
        outStr = 'Player: ' + str(self) + ' hp=' + str(self.Health) + '/' + str(self.MaxHealth)
        return outStr

class Game():
    def __init__(self,players,decks):
        self.players = players
        self.turn = 0
        
        for player,deck in zip(players,decks):
            player.Health = 25
            for card in deck:
                card.Owner = player
                player.addCardToDeck(card)
            
    def RoundStart(self):
        self.turn += 1
        for player in self.players:
            player.addUnitMana(1)
            player.draw()