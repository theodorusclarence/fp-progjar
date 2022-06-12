import os
import json
import base64
from glob import glob
import shelve
import random
import datetime

#asumsi, hanya ada player 1, 2 , 3
class PlayerServerInterface:
    def __init__(self):
        self.players = shelve.open('g.db',writeback=True)
        self.players['1']= "400,0"
        self.players['2']= "100,0"
        self.prev_time = datetime.datetime.now()
        self.random_x = random.randint(0, 800)
        self.random_speed = random.randint(100, 300)


    def set_location(self,params=[]):
        pnum = params[0]
        lokasi = self.players[pnum].split(',')
        x = int(lokasi[0]) + int(params[1])
        y = params[2]
        try:
            self.players[pnum] = f'{x},{y}'
            self.players.sync()
            return dict(status='OK', player=pnum)
        except Exception as e:
            return dict(status='ERROR')

    def get_location(self,params=[]):
        pnum = params[0]
        try:
            return dict(status='OK',location=self.players[pnum])
        except Exception as ee:
            return dict(status='ERROR')

    def get_enemy_location(self,params=[]):
        if(self.prev_time.second < datetime.datetime.now().second):
            self.random_x = random.randint(0, 800)
            self.random_speed = random.randint(100, 300)
        self.prev_time = datetime.datetime.now()
        try:
            return dict(status='OK',random_x=self.random_x,random_speed=self.random_speed)
        except Exception as ee:
            return dict(status='ERROR')


if __name__=='__main__':
    p = PlayerServerInterface()
    p.set_location(['1',100,100])
    print(p.get_location('1'))
    p.set_location(['2',120,100])
    print(p.get_location('2'))
    print(p.get_enemy_location())
