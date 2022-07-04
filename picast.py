#!/usr/bin/python3
import urllib.parse as urlparse
import http.server
import socketserver
import os
import subprocess
import configparser
import json
import psutil
import datetime
import threading
import time
import shutil
import libvlc as vlc
from threading import Timer
from urllib.parse import parse_qs
from os import path
from gpiozero import CPUTemperature
from gpiozero import Button
from datetime import datetime as dt
from os import listdir
from os.path import isfile, join, isdir

config = configparser.ConfigParser()
config.read('/home/pi/piaudiocast/config.ini')
WEBPATH=config['system']['path']+"web"
os.chdir(WEBPATH)
button = Button(config['system']['button'])
buttonPressed = False

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        pathSplit = self.path.split("?")
        pathSection = pathSplit[0].split("/")
        if self.path == '/':
            self.path = '/index.html'
            print(self.path);
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        elif path.exists(WEBPATH+pathSplit[0]) is True:
            self.path = pathSplit[0]
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        elif pathSection[1] == "api":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            if pathSection[2] == "play":
                file=self.getData("file",self.path)
                if(file[0:4] != "http"):
                    file=config['system']['music']+file
                piCastPlayer.play(file)
                outputJson={"result":"play","url":file}
            elif pathSection[2] == "stop":
                piCastPlayer.stop()
                outputJson={"result":"stop"}
            elif pathSection[2] == "pause":
                piCastPlayer.pause()
                outputJson={"result":"pause"}
            elif pathSection[2] == "back":
                piCastPlayer.playlistMove="back"
                outputJson={"result":"back"}
            elif pathSection[2] == "next":
                piCastPlayer.playlistMove="next"
                outputJson={"result":"next"}
            elif pathSection[2] == "info":
                outputJson=piCastPlayer.updatePlayer(True)
            elif pathSection[2] == "volume":
                nv=self.getData("v",self.path)
                outputJson={"result":piCastPlayer.volume(nv)}
            elif pathSection[2] == "files":
                directory=self.getData("path",self.path)
                outputJson=self.dirListFormatted(config['system']['music']+directory)
            elif pathSection[2] == "playall":
                directory=self.getData("path",self.path)
                if directory == "stop":
                    outputJson={"result":piCastPlayer.playAllStop()}
                else:
                    outputJson={"result":"playall"}
                    s=Timer(1,piCastPlayer.playAll,[config['system']['music']+directory])
                    s.start()
            else:
                outputJson={"error":"novalid"}
            return self.wfile.write(bytes(json.dumps(outputJson), "utf-8"))
        
        elif pathSection[1] == "stats.json":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            outputJson={"ramfree":str(self.get_ramFree())+"MB","ramtotal":str(self.get_ramTotal())+"MB","cpuspeed":str(self.get_cpu_speed())+"MHz","cputemp":str(self.get_temperature())+"°C","cpuuse":str(self.get_cpu_use())+"%","load":str(self.get_load()),"ip":str(self.get_ipaddress()),"uptime":str(self.get_uptime())}
            return self.wfile.write(bytes(json.dumps(outputJson), "utf-8"))
        
        elif pathSection[1] == "run":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            if self.getData("pass",self.path) == config['ctrl']['pass']:
                if pathSection[2] == "reboot":
                    self.wfile.write(bytes('{"html":"Rebooting the Raspberry Pi","cmd":null}', "utf-8"))
                    piCastPlayer.play(config['system']['path']+"wifi.mp3")
                    time.sleep(2)
                    os.system(config['cli']['reboot'])
                elif pathSection[2] == "poweroff":
                    self.wfile.write(bytes('{"html":"Powering off the Raspberry Pi","cmd":null}', "utf-8"))
                    piCastPlayer.play(config['system']['path']+"wifi.mp3")
                    time.sleep(2)
                    os.system(config['cli']['poweroff'])
                elif pathSection[2] == "service":
                    if pathSection[3] == "start" and pathSection[4] is not None:
                        self.wfile.write(bytes('{"html":"Starting the ' + pathSection[4] + ' service.","cmd":null}', "utf-8"))
                        os.system("sudo systemctl start " + pathSection[4])   
                    elif pathSection[3] == "stop" and pathSection[4] is not None:
                        self.wfile.write(bytes('{"html":"Stoping the ' + pathSection[4] + ' service.","cmd":null}', "utf-8"))
                        os.system("sudo systemctl stop " + pathSection[4])
                    elif pathSection[3] == "restart" and pathSection[4] is not None:
                        self.wfile.write(bytes('{"html":"Re-starting the ' + pathSection[4] + ' service.","cmd":null}', "utf-8"))
                        os.system("sudo systemctl restart " + pathSection[4])
                    else:
                        self.wfile.write(bytes('{"html":"Unknown service command","cmd":null}', "utf-8"))
                else:
                    self.wfile.write(bytes('{"html":"Wrong command","cmd":null}', "utf-8"))
            else:
                self.wfile.write(bytes('{"html":"Wrong password","cmd":null}', "utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes('Document requested is not found.', "utf-8"))
        return
        
    def getData(self,data,url):
        parsed = urlparse.urlparse("http://localhost"+url)
        try:
            return str(parse_qs(parsed.query)[data]).replace("['","").replace("']","")
        except:
            return ""
            pass

    def get_ramTotal(self):
        memory = psutil.virtual_memory()
        return round(memory.total/1024.0/1024.0,1)
        
    def get_ramFree(self):
        memory = psutil.virtual_memory()
        return round(memory.available/1024.0/1024.0,1)       
    
    def get_cpu_use(self):
        return psutil.cpu_percent()

    def get_temperature(self):
        try:
            cpu = CPUTemperature()
            return cpu.temperature
        except:
            return "n/a"

    def get_uptime(self):
        try:
            s = subprocess.check_output(["uptime","-p"])
            return s.decode().replace("\n","")
        except:
            return "n/a"

    def get_load(self):
        try:
            s = subprocess.check_output(["uptime"])
            load_split = s.decode().split("load average:")
            return load_split[1].replace("\n","")
        except:
            return "n/a"
    
    def get_ipaddress(self):
        try:
            s = subprocess.check_output(["hostname","-I"])
            return s.decode().replace("\n","")
        except:
            return "0.0.0.0"
    
    def get_cpu_speed(self):
        try:
            f = os.popen('vcgencmd get_config arm_freq')
            cpu = f.read()
            if cpu != "":
                return cpu.split("=")[1].replace("\n","")
            else:
                return "n/a"
        except:
            return "n/a"
        
    def dirList(self,path):
        self.dataListFiles=[]
        self.dataListDirs=[]
        for x in os.listdir(path):
            if isfile(path+"/"+x) and piCastPlayer.isAudio(x) is True:
                self.dataListFiles.append(x)
            elif isdir(path+"/"+x):
                self.dataListDirs.append(x)
            elif os.path.islink(path+"/"+x):
                continue
            else:
                continue
        
    def dirListFormatted(self,mypath):
        self.dirList(mypath)
        result = {"path":mypath.replace(config['system']['music'],""),"directories":self.dataListDirs,"files":self.dataListFiles}
        return result          

    
# Music Player
# With VLC libs
class castPlayer():
    def __init__(self):
        print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Init Media Player")
        self.threadPlayer = threading.Thread(target=self.threadPlayer)
        self.threadPlayer.daemon=True 
        self.threadPlayer.start()
        
    def threadPlayer(self):
        self.statePlayer = False
        self.vlcInstance = vlc.Instance("--no-xlib --quiet")
        #self.vlcInstance = vlc.Instance() #for debug
        self.player = self.vlcInstance.media_player_new()   
        self.player.set_mrl(config['system']['path']+"picast.mp3")
        self.player.audio_set_volume(100)
        self.player.play()
        self.dataVolume="100"
        self.playlistMode=False
        self.playlistMove="none"
        
    def updatePlayer(self,api=False):
        posTimeNano = self.player.get_time()
        self.dataTime=round(float(posTimeNano / 1000))
        self.dataTimeText=str(datetime.timedelta(seconds=self.dataTime))
        posTimeNanoTotal = self.player.get_length()
        self.dataTimeTotal=round(float(posTimeNanoTotal / 1000))
        self.dataTimeTotalText=str(datetime.timedelta(seconds=self.dataTimeTotal))
        self.dataVolume=self.player.audio_get_volume()
        self.dataMute=self.player.audio_get_mute()
        self.dataTitle=str(self.player.get_media().get_meta(0))
        self.dataPosition=round(self.player.get_position() * 100)
        self.dataPlaying=self.player.is_playing()
        if(piCastPlayer.playlistMode is True):
            self.dataPlaylist=1
        else:
            self.dataPlaylist=0
        if(api is True):
            return {"playlist":str(self.dataPlaylist),"mute":str(self.dataMute),"volume":str(self.dataVolume),"playing":str(self.dataPlaying),"time":str(self.dataTimeText),"timeraw":str(self.dataTime),"title":str(self.dataTitle),"position":str(self.dataPosition),"totaltime":str(self.dataTimeTotalText),"totaltimeraw":str(self.dataTimeTotal)}
        else:
            return True
    
    def play(self,url):
        print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Play Media Player : "+url)
        if self.player.is_playing() is True:
            self.player.stop()
            self.player.audio_set_volume(self.dataVolume) 
        self.player.set_mrl(url)
        self.player.audio_set_volume(int(self.dataVolume))
        self.player.play()
    
    def stop(self):
        print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Stop Media Player")
        if(self.playlistMove=="none"):
            self.playlistMode=False
        self.playlistMove="none"
        self.player.stop()
        self.player.audio_set_volume(self.dataVolume)      
    
    def pause(self):
        print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Pause Media Player")
        self.player.pause()
        
    def volume(self,vol):
        self.dataVolume=self.player.audio_get_volume()
        v=self.dataVolume
        if(vol=="plus"):
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Increase volume")
            v=self.dataVolume+5
        elif(vol=="minus"):
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Decrease volume")
            v=self.dataVolume-5
        elif(vol=="mute"):
            if(self.player.audio_get_mute() == 0):
                print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Mute volume")
                self.player.audio_set_mute(True)
            else:
                print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Remove Mute volume")
                self.player.audio_set_mute(False)

        if(v >=0 and v <= 100 and v!=self.dataVolume):
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Volume set to "+str(v)+"%")
            self.player.audio_set_volume(v)        
        self.dataVolume=self.player.audio_get_volume()
        return self.dataVolume
    
    def volumeLoop(self,inc):
        self.dataVolume=self.player.audio_get_volume()
        v=self.dataVolume
        nv=v+inc
        if(nv>100):
            nv=0
        print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Volume set to "+str(v)+"%")
        self.player.audio_set_volume(nv)        
        self.dataVolume=self.player.audio_get_volume()
        return self.dataVolume
    
    def playAllStop(self):
        self.playlistMode=False
        self.playlistMove="none"
        return self.playlistMode
    
    def playAll(self,path):
        if(self.playlistMode is True):
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Disabling playlist mode")
            self.playlistMode=False
            return "normal"
        else:
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Enabling playlist mode")
            self.path=path
            self.playlistMode=True
            self.playlistFiles=[]
            for x in os.listdir(self.path):
                if isfile(self.path+"/"+x) and self.isAudio(x) is True:
                    self.playlistFiles.append(x)
                elif isdir(self.path+"/"+x):
                    #self.playlistDirs.append(x)
                    continue
                elif os.path.islink(self.path+"/"+x):
                    continue
                else:
                    continue
            playNow=0
            while self.playlistMode is True:
                if(self.player.is_playing() == 1):
                    if(self.playlistMove=="next"):
                        print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Playlist move forward")
                        if(playNow<len(self.playlistFiles)):
                            self.stop()
                    elif(self.playlistMove=="back"):
                        print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Playlist move backward")
                        if(playNow>=1):
                            playNow=playNow - 2
                            self.stop()
                    else:
                        continue
                else:
                    if(playNow < len(self.playlistFiles)):
                        print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Playlist mode play : "+self.playlistFiles[playNow])
                        self.play(self.path+"/"+self.playlistFiles[playNow])
                        playNow=playNow + 1
                        time.sleep(2)
                    else:
                        break;
    
    def isAudio(self,f):
        l = len(f)
        if(str(f[(l-4):]).lower() == ".mp3"):
            return True
        elif(str(f[(l-4):]).lower() == ".wav"):
            return True
        elif(str(f[(l-4):]).lower() == ".wma"):
            return True
        elif(str(f[(l-4):]).lower() == ".ogg"):
            return True
        elif(str(f[(l-4):]).lower() == ".m4a"):
            return True
        elif(str(f[(l-4):]).lower() == ".aud"):
            return True
        elif(str(f[(l-4):]).lower() == ".mid"):
            return True
        elif(str(f[(l-5):]).lower() == ".flac"):
            return True
        else:
            return False  

        
def checkWLAN():
    try:
        if(piCastPlayer.threadPlayer.daemon is True):
            if(os.path.exists(config['system']['music']+"/USB/usb1/wpa_supplicant.conf") is True):
                installWLAN(1)
            elif(os.path.exists(config['system']['music']+"/USB/usb2/wpa_supplicant.conf") is True):
                installWLAN(2)
            elif(os.path.exists(config['system']['music']+"/USB/usb3/wpa_supplicant.conf") is True):
                installWLAN(3)
            elif(os.path.exists(config['system']['music']+"/USB/usb4/wpa_supplicant.conf") is True):
                installWLAN(4)
            else:
                s=Timer(1.0,checkWLAN)
                s.start()
        else:
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Device not ready, skip New Wifi conf check.")
            s=Timer(1.0,checkWLAN)
            s.start()
    except:
        print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Device not ready, skip New Wifi conf check.")
        w=Timer(1.0,checkWLAN)
        w.start()

def installWLAN(usb):
    print(dt.now().strftime("%m-%d-%y %H:%M > ") + "New Wifi conf detected, install it")
    piCastPlayer.stop()
    time.sleep(1)
    piCastPlayer.play(config['system']['path']+"wifi.mp3")
    file=config['system']['music']+"/USB/usb"+str(usb)+"/wpa_supplicant.conf"
    bootfile="/boot/wpa_supplicant.conf"
    savefile=config['system']['music']+"/USB/usb"+str(usb)+"/wpa_supplicant.conf.installed"
    shutil.copyfile(file, bootfile)
    shutil.move(file, savefile)
    print(dt.now().strftime("%m-%d-%y %H:%M > ") + "New Wifi conf installed, reboot")
    time.sleep(2)
    os.system(config['cli']['reboot'])

def checkButton():
    global buttonPressed, button
    if button.is_pressed and buttonPressed is False:
        buttonPressed = True
        piCastPlayer.volumeLoop(5)
        time.sleep(2)
    elif button.is_pressed:
        piCastPlayer.volumeLoop(5)
        pass
    elif buttonPressed:
        buttonPressed = False
    else:
        buttonPressed = False
    b=Timer(0.5,checkButton)
    b.start()
        
print(dt.now().strftime("%m-%d-%y %H:%M > ") + "piCast started")
piCast = MyHttpRequestHandler
piCastServer = socketserver.TCPServer(("0.0.0.0", int(config['ctrl']['port'])), piCast)
print(dt.now().strftime("%m-%d-%y %H:%M > ") + "piCast started Web Server")
print(dt.now().strftime("%m-%d-%y %H:%M > ") + "piCast started Media Player")
piCastPlayer = castPlayer()
print(dt.now().strftime("%m-%d-%y %H:%M > ") + "piCast started Media Player")
print(dt.now().strftime("%m-%d-%y %H:%M > ") + "piCast starting extended scripts")
checkWLAN()
checkButton()
print(dt.now().strftime("%m-%d-%y %H:%M > ") + "piCast started extended scripts")
piCastServer.serve_forever()
