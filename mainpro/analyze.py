#!/usr/bin/env python
#coding:utf-8

#analyze.py
#从/var/log/auth.log中过滤出主机本地登录错误日志，匹配关键字'LOGIN','FAILED','tty*'
import time
import datetime
from readconf import readconf
from isfileempty import isFileEmpty

t = time.ctime()
today = (t.split()[1],t.split()[2])
#print today

class colors:
    BLACK         = '\033[0;30m'
    DARK_GRAY     = '\033[1;30m'
    LIGHT_GRAY    = '\033[0;37m'
    BLUE          = '\033[0;34m'
    LIGHT_BLUE    = '\033[1;34m'
    GREEN         = '\033[0;32m'
    LIGHT_GREEN   = '\033[1;32m'
    CYAN          = '\033[0;36m'
    LIGHT_CYAN    = '\033[1;36m'
    RED           = '\033[0;31m'
    LIGHT_RED     = '\033[1;31m'
    PURPLE        = '\033[0;35m'
    LIGHT_PURPLE  = '\033[1;35m'
    BROWN         = '\033[0;33m'
    YELLOW        = '\033[1;33m'
    WHITE         = '\033[1;37m'
    DEFAULT_COLOR = '\033[00m'
    RED_BOLD      = '\033[01;31m'
    ENDC          = '\033[0m'


class Analyze:
    def __init__(self):
        value = readconf()
        self.TTY_Threshold = int(value['TTY_Threshold'])
        self.Telnet_Threshold = int(value['Telnet_Threshold'])
        self.Su_Time = int(value['Su_Time'])
        self.Su_Threshold = int(value['Su_Threshold'])
        self.TTY_Time = int(value['TTY_Time'])

        
        #print self.TTY_Threshold,self.Telnet_Threshold,self.Su_Time,self.Su_Threshold,self.TTY_Time
        #if isFileEmpty('/var/log/auth.log'):
        #    print
        #    print 'This is a empty file.'
        #    print
        #    exit()
        #else:
        self.login_failed()

    def login_failed(self):
        filename = '/var/log/auth.log'
        f = open(filename,'r')
        tty_count = 0
        telnet_count = 0
        self.su_count = 0

        while True:
            content = f.readline()
            error_log = []
            tty = ("'/dev/tty1'","'/dev/tty2'","'/dev/tty3'","'/dev/tty4'","'/dev/tty5'","'/dev/tty6'","'/dev/tty7'")        

            if(content != ''):				#判断是否达到文件末尾(监听文件更新)           
                self.split_list = content.split()
                if self.split_list[0] == today[0] and self.split_list[1] == today[1]:		#只检测当天的日志文件
                    if len(self.split_list) > 9:
                        console_value = self.split_list[9].split('/')
                    
                        #过滤出主机本地登录错误日志，匹配关键字'LOGIN','FAILED','tty*'
                        if 'LOGIN' == self.split_list[6] and 'FAILED' == self.split_list[5] and self.split_list[9] in tty:
                            self.ttyloginAnalyze()

                        #过滤出telnet连接失败记录
                        elif ('login' in self.split_list[4].split('[')) and ('FAILED' in self.split_list[5]) and ('dev' in console_value and 'pts' in console_value):
                            self.telnetAnalyze()

                        #过滤出su切换失败的记录      
                        elif self.split_list[4].split("[")[0] == 'su' and self.split_list[6] == 'authentication' and self.split_list[7] == 'failure;':
                            self.suAnalyze()

    #tty login错误处理
    def ttyloginAnalyze(self):
        tty_fobj = open('log/tty.log','a')
        Time = self.split_list[2].split(":")[0]+":"+self.split_list[2].split(":")[1]            #tty类型登录时间
        Console = self.split_list[9]                                                        #tty类型登录的虚拟控制台
        User = self.split_list[11].split(',')[0]                                                        #tty类型登录的用户
        tty_fobj.write("%s\t%s\t%s\n" % (Time,Console,User))                                #将时间,控制台,用户三个信息写入tty.log日志文件
        tty_fobj.close()
    
        tty_count += 1
        #60s内错误4次则为异常
        if tty_count == 1:
            start = datetime.datetime.now()
            print start

            if tty_count == TTY_Threshold:
                end = datetime.datetime.now()
                sec = (end-start).seconds
                print end 
                if sec <= TTY_Time: 
                    print colors.YELLOW + 'TTY Exception: ' + colors.ENDC
                    tty_count = 0 

    #telnet异常
    def telnetAnalyze(self):        
        telnet_fobj = open('log/TelnetError.log','a')
        Time = self.split_list[2].split(":")[0]+":"+self.split_list[2].split(":")[1]
        User = self.split_list[13].split(",")[0]
        IP = self.split_list[11]
        telnet_fobj.write("%s\t%s\t%s\n" % (Time,User,IP))
        telnet_fobj.close()
        print colors.BLUE + 'Telnet Exception: %s\t%s\t%s' % (Time,IP,User) + colors.ENDC

    #su命令使用异常,10s有3次错误记录即为异常
    def suAnalyze(self):
        global start
        global end
        su_fobj = open('log/su.log','a')
        Time = self.split_list[2]
        CurrentUser = 'CurrentUser='+self.split_list[12].split("=")[1]
        LoginUser = 'LoginUser='+self.split_list[14].split("=")[1]
        su_fobj.write("%s\t%s\t%s\n" % (Time,CurrentUser,LoginUser))
                    
        self.su_count += 1
        if self.su_count == 1:
            start = datetime.datetime.now()
        if self.su_count == self.Su_Threshold:
            print 'This is a test'
            end = datetime.datetime.now()
            sec = (end-start).seconds
            if sec <= self.Su_Time:
                print colors.RED + 'Su Login Exception: %s\t%s\t%s' % (start,CurrentUser,LoginUser)+ colors.ENDC
                self.su_count = 0

if __name__ == '__main__':
    ex = Analyze()
    #ex.login_failed()
    #pass
