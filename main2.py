import json

import configparser


config = configparser.ConfigParser()

a = config.read('conf.ini')

b = config.get('SCOPE Settings', 'scopelist')

def Convert(string):
    li = list(string.split(","))
    return li

liii = Convert(b)
print(liii)