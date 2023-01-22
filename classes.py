# -*- coding: utf-8 -*-
import numpy as np
import random
       
class Player:

    def __init__(cls, id, color, name=None, strategy=None):
        cls.id = id
        if name is None:
            cls.name = f"Player {id}"
        else:
            cls.name = name
        cls.color = color
        cls.strategy = strategy
        
    def take_turn(cls):
        pass
        
class GameButton:
    def __init__(cls, name, value, status, button, i, j):
        cls.name = name
        cls.value = value
        cls.status = status
        cls.button = button
        cls.i = i
        cls.j = j
        
class GameMode:
        def __init__(cls, name, verb, n, m):
            cls.name = name
            cls.verb = verb
            cls.n = n
            cls.m = m
            
        def generate_value(cls):
            value = 0
            for i in range(cls.n):
                value += random.randint(1, cls.m)
            return(value)
            
        def generate_button_value(cls, p):
            if random.random() < p:
                return("Free Space")
            else:
                return(cls.generate_value())