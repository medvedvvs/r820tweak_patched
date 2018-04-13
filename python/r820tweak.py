#!/usr/bin/env python

import wx
import socket
import sys
import os

from pprint import pprint
from struct import *
import time

# define range of registers
RO_REGS = range(0,5)
RW_REGS = range(5,32)
ALL_REGS = range(0,32)
#print RO_REGS
#print RW_REGS

def get_lna_gain(sock):
    message = "g 5\n"
    sock.sendall(message)
    data = sock.recv(32)
    message = "s 6 "+str(1<<6)+" "+str(1<<6)+"\n"
    sock.sendall(message)
    data2 = sock.recv(32)
    return int(data[2:])&15

def get_mix_gain(sock):
    message = "g 7\n"
    sock.sendall(message)
    data = sock.recv(32)
    return int(data[2:])&15

def get_vga_gain(sock):
    message = "g 12\n"
    sock.sendall(message)
    data = sock.recv(32)
    return int(data[2:])&15

def get_hpf(sock):
    message = "g 27\n"
    sock.sendall(message)
    data = sock.recv(32)
    return 15-(int(data[2:])&15)

def set_hpf(sock,width):
    message = "s 27 "+str(15-width)+" 15\n"
    sock.sendall(message)
    data = sock.recv(32)

def get_lpnf(sock):
    message = "g 27\n"
    sock.sendall(message)
    data = sock.recv(32)
    return 15-(int(data[2:])&(15>>4))

def set_lpnf(sock,width):
    message = "s 27 "+str((15-width)<<4)+" "+str(15<<4)+"\n"
    sock.sendall(message)
    data = sock.recv(32)


def get_lpf(sock):
    message = "g 11\n"
    sock.sendall(message)
    data = sock.recv(32)
    return (int(data[2:])&15)

def set_lpf(sock,width):
    message = "s 11 "+str(width)+" 15\n"
    sock.sendall(message)
    data = sock.recv(32)

def get_filt(sock):
    message = "g 10\n"
    sock.sendall(message)
    data = sock.recv(32)
    return 15-(int(data[2:])&15)

def set_filt(sock,width):
    message = "s 10 "+str(15-width)+" 15\n"
    sock.sendall(message)
    data = sock.recv(32)

def set_lna_gain(sock,gain):

    message = "s 5 "+str(gain)+" 15\n"
    sock.sendall(message)
    data = sock.recv(32)
    


def set_mix_gain(sock, gain):
    message = "s 7 "+str(gain)+" 15\n"
    sock.sendall(message)
    data = sock.recv(32)


def set_vga_gain(sock, gain):
    message = "s 12 "+str(gain)+" 15\n"
    sock.sendall(message)
    data = sock.recv(32)





class MyPanel(wx.Panel):

    def scan_device(self):
        self.lna_gain = get_lna_gain(self.sock)
        self.mix_gain = get_mix_gain(self.sock)
        self.vga_gain = get_vga_gain(self.sock)
        self.lpf = get_lpf(self.sock)
        self.lpnf = get_lpnf(self.sock)
        self.hpf = get_hpf(self.sock)
        self.filt = get_filt(self.sock)


        self.slider_gain_lna.SetValue(self.lna_gain)
        self.slider_gain_mix.SetValue(self.mix_gain) 
        self.slider_gain_vga.SetValue(self.vga_gain)
        self.slider_lpf.SetValue(self.lpf)
        self.slider_lpnf.SetValue(self.lpnf)
        self.slider_hpf.SetValue(self.hpf)
        self.slider_filt.SetValue(self.filt)


    def connect(self, dev):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_address = '/var/tmp/rtlsdr' + str(dev)
        try:
            self.sock.connect(server_address)
        except socket.error:
            print >>sys.stderr
            #sys.exit(1)
            # TODO: proper warning


    def scan_devices(self):
        self.device_list = []
        self.device_nodes = []
        for a in range(16):
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server_address = '/var/tmp/rtlsdr' + str(a)
            try:
                sock.connect(server_address)
            except socket.error:
                pass
            else:
                self.device_list.append("R820T2 device: #" + str(a))
                self.device_nodes.append(a)



    def __init__(self, parent, id):
        self.scan_devices()

        wx.Panel.__init__(self, parent, id)
        self.SetBackgroundColour("white")
        
        fnt = wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, True)
        T = wx.StaticText(self, -1, 'LNA Gain', (10,45))
        T.SetFont(fnt)
        self.slider_gain_lna = wx.Slider(self, -1, 0, 0, 15, (10, 50), (180, 48), wx.SL_HORIZONTAL | wx.SL_AUTOTICKS, name="LNA Gain")

        T = wx.StaticText(self, -1, 'Mixer Gain', (10,85))
        T.SetFont(fnt)
        self.slider_gain_mix = wx.Slider(self, -1, 0, 0, 15, (10, 90), (180, 48), wx.SL_HORIZONTAL | wx.SL_AUTOTICKS, name="Mixer Gain")

        T = wx.StaticText(self, -1, 'VGA Gain', (10,125))
        T.SetFont(fnt)
        self.slider_gain_vga = wx.Slider(self, -1, 0, 0, 15, (10, 130), (180, 48), wx.SL_HORIZONTAL | wx.SL_AUTOTICKS, name="VGA Gain")

        T = wx.StaticText(self, -1, 'LPF Cutoff', (10,175))
        T.SetFont(fnt)
        self.slider_lpf = wx.Slider(self, -1, 0, 0, 15, (10, 180), (180, 48), wx.SL_HORIZONTAL | wx.SL_AUTOTICKS, name="LPF Cutoff")
        
        T = wx.StaticText(self, -1, 'LPNF Cutoff', (6, 215))
        T.SetFont(fnt)
        self.slider_lpnf = wx.Slider(self, -1, 0, 0, 15, (10, 220), (180, 49), wx.SL_HORIZONTAL | wx.SL_AUTOTICKS, name="LNPF Cutoff")

        T = wx.StaticText(self, -1, 'HPF Cutoff', (10,255))
        T.SetFont(fnt)
        self.slider_hpf = wx.Slider(self, -1, 0, 0, 15, (10, 260), (180, 40), wx.SL_HORIZONTAL | wx.SL_AUTOTICKS, name="HPF Cutoff")

        T = wx.StaticText(self, -1, 'Filter BW', (10, 295))
        T.SetFont(fnt)
        self.slider_filt = wx.Slider(self, -1, 0, 0, 15, (10, 300), (180, 40), wx.SL_HORIZONTAL | wx.SL_AUTOTICKS, name="Filter BW")

        fnt = wx.Font(5, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, True)
        self.cb = wx.ComboBox(self,
                              id=0,
                              value=self.device_list[0],
                              pos=(10,10),
                              size=(160,25),
                              choices=self.device_list,
                              style=wx.CB_READONLY|wx.CB_DROPDOWN)
        self.cb.SetFont(fnt)

        
        self.button = wx.Button(self, id=wx.ID_ANY, pos=(190,10), size=(50,25), label="Rescan")
        self.button.SetFont(fnt)
        self.button.Bind(wx.EVT_BUTTON, self.onButton)
        self.cb.Bind(wx.EVT_COMBOBOX, self.onCBChange)

        font = wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, True)
        font1 = wx.Font(5, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, True)
#        self.regtxt = wx.TextCtrl(self, -1, pos=(10,270), size=(60, 10))
#        self.regtxt.SetValue('0x0a')
#        self.regtxt.SetFont(font)
#        self.buttontxt = wx.Button(self, id=wx.ID_ANY, pos=(80,260), size=(50,24), label="Get")
#        self.buttontxt.SetFont(font)
#        self.buttontxt.Bind(wx.EVT_BUTTON, self.onButtontxt)


        self.re = []
        self.bur = []
        self.buw = []
        step = 28
        ypos = 45
        x00 = 210
        x0 = x00 + 20
        x1 = x0 + 55
        x2 = x1 + 55
        x3 = x2 + 22
        self.BID  = 13350
        self.BIDR = 14350
        self.BIDW = 15350
        bid  = self.BID	# base id for checkbox
        bidr = self.BIDR	# base id for readreg button
        bidw = self.BIDW	# base id for writereg button
        j = 0
        for i in range(0, 16):
            y = ypos + j * step
            j = j+1
            cheb = wx.CheckBox(self, bid, pos=(x00, y-6)); bid += 1;
            cheb.SetValue(True)
            self.re.insert(i, [wx.TextCtrl(self, -1, pos=(x0, y), size=(50, 10)), wx.TextCtrl(self, -1, pos=(x1, y), size=(50, 10)), cheb])
            self.re[i][0].SetValue('0x0a')
            self.re[i][1].SetValue('0x0')
            self.re[i][0].SetFont(font)
            self.re[i][1].SetFont(font)
            self.bur.insert(i, wx.Button(self, id=bidr, pos=(x2, y-5), size=(20,20), label="r")); bidr += 1;
            self.bur[i].SetFont(font1)
            self.bur[i].SetBackgroundColour("green")
            self.bur[i].SetForegroundColour("white")
            self.bur[i].Bind(wx.EVT_BUTTON, self.onButtonbitsr)
            self.buw.insert(i, wx.Button(self, id=bidw, pos=(x3, y-5), size=(20,20), label="w")); bidw += 1;
            self.buw[i].SetFont(font1)
            self.buw[i].SetBackgroundColour("red")
            self.buw[i].SetForegroundColour("white")
            self.buw[i].Bind(wx.EVT_BUTTON, self.onButtonbitsw)

        x00 = 410
        x0 = x00 + 20
        x1 = x0 + 55
        x2 = x1 + 55
        x3 = x2 + 22
        j = 0
        for i in range(16, 32):
            y = ypos + j * step
            j = j+1
            cheb = wx.CheckBox(self, bid, pos=(x00, y-6)); bid += 1;
            cheb.SetValue(True)
            self.re.insert(i, [wx.TextCtrl(self, -1, pos=(x0, y), size=(50, 10)), wx.TextCtrl(self, -1, pos=(x1, y), size=(50, 10)), cheb])
            self.re[i][0].SetValue('0x0a')
            self.re[i][1].SetValue('0x0')
            self.re[i][0].SetFont(font)
            self.re[i][1].SetFont(font)
            self.bur.insert(i, wx.Button(self, id=bidr, pos=(x2, y-5), size=(20,20), label="r")); bidr += 1;
            self.bur[i].SetFont(font1)
            self.bur[i].SetBackgroundColour("green")
            self.bur[i].SetForegroundColour("white")
            self.bur[i].Bind(wx.EVT_BUTTON, self.onButtonbitsr)
            self.buw.insert(i, wx.Button(self, id=bidw, pos=(x3, y-5), size=(20,20), label="w")); bidw += 1;
            self.buw[i].SetFont(font1)
            self.buw[i].SetBackgroundColour("red")
            self.buw[i].SetForegroundColour("white")
            self.buw[i].Bind(wx.EVT_BUTTON, self.onButtonbitsw)
            

        self.butsave = wx.Button(self, id=wx.ID_ANY, pos=(200, y + 30), size=(66,25), label="File Save")
        self.butsave.Bind(wx.EVT_BUTTON, self.saveregs)
        self.butsave.SetFont(font)
        self.butread = wx.Button(self, id=wx.ID_ANY, pos=(300, y + 30), size=(66,25), label="File Read")
        self.butread.Bind(wx.EVT_BUTTON, self.readregs)
        self.butread.SetFont(font)
        self.butreset = wx.Button(self, id=wx.ID_ANY, pos=(440, y + 30), size=(55,25), label="Get")
        self.butreset.Bind(wx.EVT_BUTTON, self.getregs)
        self.butreset.SetFont(font)
        self.butreset = wx.Button(self, id=wx.ID_ANY, pos=(510, y + 30), size=(55,25), label="Clear")
        self.butreset.Bind(wx.EVT_BUTTON, self.resetregs)
        self.butreset.SetFont(font)

        if len(self.device_list):
            self.connect(self.device_nodes[0])
            self.scan_device()

        self.Bind(wx.EVT_SLIDER, self.sliderUpdate)
        # initial set of registers
        self.getregs(0)


    def onCBChange(self, event):
        item = self.cb.GetValue()
        num = self.device_list.index(item)
        self.connect(num)
        self.scan_device()


    def onButton(self, event):
        self.scan_devices()
        if len(self.device_list):
            self.connect(self.device_nodes[0])
            self.scan_device()
            self.cb = wx.ComboBox(self,
                              id=0,
                              value=self.device_list[0],
                              pos=(10,10),
                              size=(160,25),
                              choices=self.device_list,
                              style=wx.CB_READONLY|wx.CB_DROPDOWN)
            fnt = wx.Font(5, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, True)
            self.cb.SetFont(fnt)

    def getRegEntry(self, rr):
#        print "Call getRegEntry ", rr
        ra = int(str(rr), 0)
        for i in range(0,32):
            r = int(str(self.re[i][0].GetValue()), 0)
#            print "Compare ", ra, " with ", r
            if r == ra:
               return i
        return -1
            

    def onButtontxt(self, event):
        rr = self.regtxt.GetValue()
        message = "g " + str(rr) +"\n"
        print "Call getreg " + message
        self.sock.sendall(message)
        data = self.sock.recv(32)
        data = int(data[2:])&15
        da = "{0:0>8b}".format(data)
        dah = "{0:0>2x}".format(data)
        print data, dah, da
#        print "{0:b}".format(data)
#        print "{0:0>8b}".format(data)

    def saveregs(self, event):
        f = open('regs.txt', 'w')
        for i in range(32):
            ch = self.re[i][2].GetValue()
            if ch is True:
               rr = self.re[i][0].GetValue()
               v = self.getReg(rr)
#               print "Got checked reg ", rr, "  val = ", v
               da = "{0:0>8b}".format(v)
               dah = "{0:0>2x}".format(v)
##             print data, dah, da
               r = int(rr, 0)
               r = "{0:0>2x}".format(r)
               s = "0x" + r + " 0x" + str(dah) +" " + "  " + da + "\n"
               f.write(s)
        f.close()
        print "Writing to regs.txt done\n"
#        print "{0:b}".format(data)
#        print "{0:0>8b}".format(data)

    def readregs(self, event):
        print "Start reading registers file"
        f = open('regs.txt', 'r')
        for rr in range(32):
            s = f.readline()
            if s:
                ss = s.split(" ")
                ss = filter(None, ss)
#                print "SS:", ss[0], "   ", ss[1]
                r_ = int(str(ss[0]), 0)
                r = self.getRegEntry(r_)
                if r > -1:
                    v = int(str(ss[1]), 0)
                    dah = "0x" + "{0:0>2x}".format(v)
#                    print "Dah: ", dah
                    self.re[r][1].SetValue(dah)
                    self.setReg(str(ss[0]), dah)
        f.close()
        print "Read from regs.txt done\n"
#        print "{0:b}".format(data)
#        print "{0:0>8b}".format(data)

    def resetregs(self, event):
        print "Reset all registers..."
        for rr in RW_REGS:
            self.setReg(str(rr), 0)
        self.getregs(event)
        print "Reset done.\n"

    def getregs(self, event):
        print "Read all registers from board..."
        for rr in ALL_REGS:
            v = self.getReg(str(rr))
            rz = "0x" + "{0:0>2x}".format(rr)
            self.re[int(rr)][0].SetValue(rz)
            rz = "0x" + "{0:0>2x}".format(v)
#            print "++++++++++++++", v, "     ", rz
            self.re[int(rr)][1].SetValue(rz)
        print "Reading done."


    def getReg(self, rr):
       message = "g " + str(rr) +"\n"
       self.sock.sendall(message)
       data = self.sock.recv(32)
#       print "Got from socket: ", data
       ret = -1
       if len(data) > 0:
           data = int(data[2:]) #& 15
#           da = "{0:0>8b}".format(data)
#           dah = "{0:0>2x}".format(data)
#           print "Got from reg ", rr, " ", data, dah, da, "\n"
           ret = data
       return ret
    
           
    def setReg(self, rr, bb):
       r_i = int(rr, 0)
       if r_i in RO_REGS:
          print "RO register given! No write performed."
          return
       message = "s " + str(rr) + " " + str(bb) + " 255\n"
#       print "Call setreg ", str(rr) + " " + str(bb)
       self.sock.sendall(message)
       data = self.sock.recv(32)
        
    def onButtonbitsr(self, event):
        button = event.GetEventObject()
        id = button.GetId()
#        print "Button ", id, " position ", (id - self.BIDR)
        id = id - self.BIDR
        rr = self.re[id][0].GetValue()
        bb = self.re[id][1].GetValue()
#        print "Get reg ", rr, " to ", bb
        data = self.getReg(rr)
        da = "{0:0>8b}".format(data)
        dah = "0x" + "{0:0>2x}".format(data)
        print "Got from reg ", rr, " ", data, dah, da, "\n"
        self.re[id][1].SetValue(dah)
        

    def onButtonbitsw(self, event):
        button = event.GetEventObject()
        id = button.GetId()
#        print "Button ", id, " position ", (id - self.BIDW)
        id = id - self.BIDW
        rr = self.re[id][0].GetValue()
        bb = self.re[id][1].GetValue()
#        print "Set reg ", rr, " to ", bb
        self.setReg(rr, bb)
#        time.sleep(2.5)
        data = self.getReg(rr)
        da = "{0:0>8b}".format(data)
        dah = "0x" + "{0:0>2x}".format(data)
        print "Got from reg ", rr, " ", data, dah, da, "\n"
        self.re[id][1].SetValue(dah)

    def setEntry(self, rr):
        r = self.getRegEntry(rr)
        if r > -1:
            v = self.getReg(rr)
            dah = "0x" + "{0:0>2x}".format(v)
            self.re[r][1].SetValue(dah)

    def sliderUpdate(self, event):
        try:
            if self.lna_gain != self.slider_gain_lna.GetValue():
                self.lna_gain = self.slider_gain_lna.GetValue()
                set_lna_gain(self.sock,self.lna_gain)
                self.setEntry(5)

            if self.mix_gain != self.slider_gain_mix.GetValue():
                self.mix_gain = self.slider_gain_mix.GetValue()
                set_mix_gain(self.sock,self.mix_gain)
                self.setEntry(7)

            if self.vga_gain != self.slider_gain_vga.GetValue():
                self.vga_gain = self.slider_gain_vga.GetValue()
                set_vga_gain(self.sock,self.vga_gain)
                self.setEntry(12)

            if self.lpf != self.slider_lpf.GetValue():
                self.lpf = self.slider_lpf.GetValue()
                set_lpf(self.sock,self.lpf)
                self.setEntry(11)

            if self.lpnf != self.slider_lpnf.GetValue():
                self.lpnf = self.slider_lpnf.GetValue()
                set_lpnf(self.sock,self.lpnf)
                self.setEntry(27)

            if self.hpf != self.slider_hpf.GetValue():
                self.hpf = self.slider_hpf.GetValue()
                set_hpf(self.sock,self.hpf)
                self.setEntry(27)

            if self.filt != self.slider_filt.GetValue():
                self.filt = self.slider_filt.GetValue()
                set_filt(self.sock,self.filt)
                self.setEntry(10)
        except Exception:
            self.connect(0)


def usage():
    print sys.argv[1],"[program_to_run]"
    print "\n\n"
    print "When used without argument, the r820tweak control panel will launch"
    print "When [program_to_run] is provided, it starts the SDR program with the modified RTLSDR driver"


def main():
    if len(sys.argv)>1:
        if sys.argv[1]!="-h" or sys.argv[1]!="-?":
            os.system("LD_PRELOAD=/usr/local/share/r820tweak/librtlsdr.so " + sys.argv[1])
            return
        else:
            usage()
            return

    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, "r820tweak", size = (620, 550))
    MyPanel(frame,-1)
    frame.Show(True)
    app.MainLoop()


if __name__ == '__main__':
    main()