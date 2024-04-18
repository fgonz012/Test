'''
Created on Apr 17, 2024

@author: FG
'''

from Base.Game import *
from Base.Set1 import *


d1 = cardContainer()

d2 = cardContainer()

p1 = Player('Player1', 25)
p2 = Player('Player2', 25)
newUnit = VanguardDefender(p1)
newGaren = Garen1(p1)
d1.addCard(newUnit, -1)
d1.addCard(newUnit, -1)
d2.addCard(newGaren, -1)
d2.addCard(newGaren, -1)
newGaren.onSummoned(p1)


gm = Game([p1,p2],[d1,d2])





print(p1.Deck)
print(p2.Deck)

gm.RoundStart()
print(p1.Deck)
print(p2.Deck)