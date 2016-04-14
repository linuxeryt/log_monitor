#!/usr/bin/env python
#coding: utf-8

import os

def isFileEmpty(filepath):  
        '''判断文件的内容是否为空'''  
        #fileSize = os.stat(filepath).st_size  
        #print fileSize
        f = open(filepath,'r').read()
        
        if len(f) == 0:  
            return False
        else:  
            return True

if __name__ == '__main__':       
    print isFileEmpty('/var/log/auth.log')
