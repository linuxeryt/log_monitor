#!/usr/bin/env python
#coding: utf-8

import re

li = []
value = {}

def readconf():
    f = open('/home/swallow/log_monitor/conf/zoomeye.conf','r')
    for line in f:
       m = re.search('[a-zA-Z]*_[a-zA-Z]*=[0-9]*',line)
       if m is not None:
          li.append(m.group())

    key = []
    val = []
    for i in li:
        key = i.split('=')[0]
        val = i.split('=')[1]
        value[key] = val
    return value

if __name__ == "__main__":
    print readconf()
