#!/usr/bin/env python
#coding:utf-8

import sys
from PyQt4 import QtGui
#from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import psutil
import time


#how long for update
MAXITERS = 300

class CPUMonitor(FigureCanvas):
    def __init__(self):
        self.before = self.prepare_cpu_usage()
        self.fig = plt.figure()
        
        self.ax = self.fig.add_subplot(2,1,1)
        self.ax2 = self.fig.add_subplot(2,1,2)
           

        FigureCanvas.__init__(self,self.fig)
        
        self.ax.set_title('CPUMonitor')
        self.ax.axis([1,5*60,0,100])
        self.ax2.axis([1,5*60,0,4000])
        #alist = [str(i) for i in range(0,100)]
        #alist = ['6:00','12:00','18:00','00:00']
        #plt.xticks(range(5),alist)
        #self.ax.set_xlim(1,24)
        #self.ax.set_ylim(0,100)

        self.ax.set_autoscale_on(False)
       
        #初始化各类cpu信息的存放列表
        self.user,self.nice,self.sys,self.idle = [],[],[],[]
        #建立axis    
        self.l_user, = self.ax.plot([],self.user,label = "User %")
        self.l_nice, = self.ax.plot([],self.nice,label = "Nice %")
        self.l_sys, = self.ax.plot([],self.sys,label = "Sys %")
        self.l_idle, = self.ax.plot([],self.idle,label = "Idle %")


        #memory info list
        self.used = []
        self.available = []
        self.l_used, = self.ax2.plot([],self.used,'r',label="MemUsage")
        self.l_available, = self.ax2.plot([],self.available,label='MemAvailable')

        plt.grid(True)
        self.ax.legend()
        self.ax.legend()

        # self.fig.canvas.draw and plt.show diffrrences
        self.fig.canvas.draw()
        #plt.show()
        
        self.setWindowTitle('SourceMonitor')        

        self.count = 0
        #调用时间事件
        self.timerEvent(None)
        #时间定时器设定为1秒更新一次
        self.timer = self.startTimer(1000)
        
    #获取最开始的cpu信息
    def prepare_cpu_usage(self):
        cpuinfo = psutil.cpu_times()
        if hasattr(cpuinfo,'nice'):
            return [cpuinfo.user,cpuinfo.nice,cpuinfo.system,cpuinfo.idle]
        else:
            return [cpuinfo.user,0,cpuinfo.system,cpuinfo.idle]

    def get_cpu_usage(self):
        now = self.prepare_cpu_usage()
        delta = [now[i]-self.before[i] for i in range(len(now))]
	
		#total is cpu sum
        total = sum(delta)

        self.before = now

        return [(100.0*dt) / total for dt in delta]


    def prepare_mem_usage(self):
        used_mem = float(psutil.virtual_memory().used/(1024.0**2))
        available_mem = float(psutil.virtual_memory().available/(1024.0**2))
        return [used_mem,available_mem]

    def get_mem_usage(self):
        now = self.prepare_mem_usage()
        return now



    #时间事件函数
    def timerEvent(self,event):
        result = self.get_cpu_usage()
        result_mem = self.get_mem_usage()

        self.user.append(result[0])
        self.nice.append(result[1])
        self.sys.append(result[2])
        self.idle.append(result[3])

        self.used.append(result_mem[0])
        self.available.append(result_mem[1])

        #通过更新各个列表中的数据，以打印到图上
        self.l_user.set_data(range(len(self.user)), self.user)
        self.l_nice.set_data(range(len(self.nice)), self.nice)
        self.l_sys.set_data(range(len(self.sys)), self.sys)
        self.l_idle.set_data(range(len(self.idle)), self.idle)

        self.l_used.set_data(range(len(self.used)),self.used)
        self.l_available.set_data(range(len(self.available)),self.available)
        
        self.fig.canvas.draw()
        #plt.show()

   
        if self.count == MAXITERS:
            now = time.localtime(time.time())
            pngname = time.strftime("%y-%m-%d-%H:%M",now)+".png"
            plt.savefig(pngname)
            self.killTimer(self.timer)
        else:
            self.count += 1

app = QtGui.QApplication(sys.argv)

widget = CPUMonitor()
widget.show()
sys.exit(app.exec_())
