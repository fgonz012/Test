'''
Created on Apr 17, 2024

@author: FG
'''


from Base.Card import Unit,Buff

class Garen1(Unit):
    def __init__(self,owner,*args,**kwargs):
        super().__init__(owner,'Garen1',*args,**kwargs)
    def __str__(self):
        return 'Garen1'
    def onSummoned(self,player):
        GarenBuff = Buff(source=self,buffType=Buff._ROUND_END, adjAttack=1,adjDefense=1)
        for unit in player.getUnitsInPlay():
            unit.addBuff(GarenBuff)
        super().onSummoned(player)
        
class VanguardDefender(Unit):
    def __init__(self,owner,*args,**kwargs):
        super().__init__(owner,'VanguardDefender',*args,**kwargs)