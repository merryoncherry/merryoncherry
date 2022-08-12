import argparse
import json
import os
import requests
import subprocess
import urllib
import winreg

# python Desktop\xlDo.py
# python Desktop\xlDo.py -b "M:\Users\Chuck\Source\Repos\xLights\xLights\x64\Debug"
# python Desktop\xlDo.py -b "M:\Users\Chuck\Source\Repos\xLights\xLights\x64\Release"

# TODOs:
# Put in version control once reasonably neat and tidy
# Use xlDo to start xSchedule also

def getXLightsBinDir():
    xlightsDir = "c:\\Program Files\\xLights"
    xlEnv = os.getenv("XLIGHTS_BIN")

    if xlEnv:
        xlightsDir = xlEnv
    return xlightsDir

def getShowFolder():
    sf = ""
    fhandle1 = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE")
    fhandle2 = winreg.OpenKey(fhandle1, "Xlights")
    if (fhandle2):
        sf = winreg.QueryValueEx(fhandle2, "LastDir")[0] # This appears to be the permanent show directory
#       sf = winreg.QueryValueEx(fhandle2, "FSEQDir")[0]
        winreg.CloseKey(fhandle2)
    winreg.CloseKey(fhandle1)
    return sf

def addXLEnvArgs(parser):
    parser.add_argument('-b', '--bindir',  help="Path to xLights binaries")
    parser.add_argument('-d', '--datadir', help="Path to xlights data dir")
    parser.add_argument('-i', '--host',    help="Host name / IP Address for xLights")
    parser.add_argument('-j', '--xshost',  help="Host name / IP Address for xSchedule")
    parser.add_argument('-p', '--port',    help="Port number for xLights")
    parser.add_argument('-q', '--xsport',  help="Port number for xSchedule")

class XLEnv:
    def __init__(self):
        self.bin = getXLightsBinDir()
        self.data = getShowFolder()
        self.xlightsRunning = 2
        self.xscheduleRunning = 2
        self.xlhost = "127.0.0.1"
        self.xlport = 49913
        self.xshost = "127.0.0.1"
        self.xsport = 80

    def getCommandLine(self, opts):
        if opts.bindir:
            self.bin = opts.bindir
        if opts.datadir:
            self.data = opts.datadir
        if opts.host:
            self.xlhost = opts.host
        if opts.port:
            self.port = int(opts.port)
        if opts.xshost:
            self.xshost = opts.xshost
        if opts.xsport:
            self.xsport = int(opts.xsport)

    def xlDoCmd(self, cmd):
        cp = subprocess.run([self.bin+"\\"+"xlDo.exe", "-c", cmd], capture_output=False); # Output capture doesn't work... bummer
        #print (cp)
        return str(cp.stdout)

    def xlDoHttp(self, cmd):
        x = requests.post('http://'+self.xlhost+':'+str(self.xlport)+'/xlDoAutomation', data=cmd)
        return x.text

    def xlDoHttpJ(self, cmdjson):
        x = requests.post('http://'+self.xlhost+':'+str(self.xlport)+'/xlDoAutomation', json=cmdjson)
        return json.loads(x.text)

    def xLightsHttp(self, cmd, params):
        x = requests.get('http://'+self.xlhost+':'+str(self.xlport)+cmd, params=params)
        return x.text

    def xScheduleHttpGet(self, cmd, params):
        # Sadly, requests uses '+' to escape spaces, xLights can only handle '%20'... so do this
        new_send_params = []
        for (k, v) in params.items():
            if not v:
                continue
            new_send_params.append(k + "=" + urllib.parse.quote(v))
        url = 'http://'+self.xshost+':'+str(self.xsport)+'/'+cmd+'?'+('&'.join(new_send_params))
        x = requests.get(url)
        return x.text

    def xScheduleHttpCloseDirect(self):
        x = requests.get('http://'+self.xshost+':'+str(self.xsport)+'/xScheduleCommand?Command=Close%20xSchedule')
        return x.text

    def xScheduleHttpCommand(self, command, params):
        return self.xScheduleHttpGet('xScheduleCommand', {'Command':command, 'Parameters':params})

    def xlDoVersion(self):
        return self.xlDoCmd('{"cmd":"getVersion"}')

    def xlDoHttpVersion(self):
        return json.loads(self.xlDoHttp('{"cmd":"getVersion"}'))["version"]

    def xlDoHttpVersionJ(self):
        j = {'cmd':'getVersion'}
        return self.xlDoHttpJ(j)["version"]

    def xlHttpVersion(self):
        return self.xLightsHttp('/getVersion', {})

    def startXLightsInternal(self, knownNotRunning):
        if knownNotRunning:
            cmd = '{"cmd":"startxLights", "ifNotRunning":"false"}'
        else:
            cmd = '{"cmd":"startxLights", "ifNotRunning":"true"}'
        self.xlDoCmd(cmd)

    def startXScheduleInternal(self, knownNotRunning):
        if knownNotRunning:
            cmd = '{"cmd":"startxSchedule", "ifNotRunning":"false"}'
        else:
            cmd = '{"cmd":"startxSchedule", "ifNotRunning":"true"}'
        self.xlDoCmd(cmd)

    def stopXLightsInternalCmd(self, knownRunning):
        cmd = '{"cmd":"closexLights", "force":"true"}'
        self.xlDoCmd(cmd)
        return 0

    def stopXLightsInternalHttp(self, knownRunning):
        try:
            x = self.xlDoHttpJ({'cmd':'closexLights','force':'true'})
            return 1
        except:
            return 0

    def isXLightsRunning(self, forceCheck):
        if (self.xlightsRunning == 2 or forceCheck):
            try:
                x = self.xlHttpVersion()
                self.xlightsRunning = 1
            except:
                self.xlightsRunning = 0
        return self.xlightsRunning

    def startXLights(self):
        if self.xlightsRunning == 0:
            self.startXLightsInternal(True)
        if self.xlightsRunning == 2:
            self.startXLightsInternal(False)
        self.xlightsRunning = 1;

    def stopXLights(self):
        rv = 0
        if self.xlightsRunning == 1:
            rv = self.stopXLightsInternalHttp(True)
        if self.xlightsRunning == 2:
            rv = self.stopXLightsInternalHttp(False)
        self.xlightsRunning = 0;
        while self.isXLightsRunning(True):
            pass
        return rv

    def startXSchedule(self):
        if self.xscheduleRunning == 0:
            self.startXScheduleInternal(True)
        if self.xscheduleRunning == 2:
            self.startXScheduleInternal(False)
        self.xscheduleRunning = 1;

    def batchRenderSeqList(self, seqs):
        self.startXLights();
        cmd = '{"cmd":"batchRender", "seqs":['
        i = 0
        for s in seqs:
            if i > 0:
                cmd = cmd + ", "
            i = i + 1
            cmd = cmd + '"' + s + '"'
        cmd = cmd + '], "promptIssues":"false"}'
        self.xlDoCmd(cmd)

#    def renderSeqList(self, seqs):
#        self.startXLights();
#        cmd = '{"cmd":"batchRender", "seqs":['
#        i = 0
#        for s in seqs:
#            if i > 0:
#                cmd = cmd + ", "
#            i = i + 1
#            cmd = cmd + '"' + s + '"'
#        cmd = cmd + '], "promptIssues":"false"}'
#        self.xlDoCmd(cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    addXLEnvArgs(parser)
    args = parser.parse_args()

    xlenv = XLEnv()
    xlenv.getCommandLine(args)

    print (xlenv.bin)
    print (xlenv.data)

    #xlenv.startXLights()
    #xlenv.stopXLights()
    #xlenv.batchRenderSeqList(['TimingTrackLabels.xsq'])
    #print("xlDo Version: "+xlenv.xlDoVersion()) # Busted
    #print("xlDo HTTP Version: "+xlenv.xlDoHttpVersion())
    #print("xlDo HTTP/JSON Version: "+xlenv.xlDoHttpVersionJ())
    #print("xLights HTTP Version: "+xlenv.xlHttpVersion())
    #print("xSchedule shutdown: "+xlenv.xScheduleHttpCommand('Close xSchedule', None))
    #print("xSchedule shutdown silly: "+xlenv.xScheduleHttpCloseDirect())

    #print("xLights running: "+str(xlenv.isXLightsRunning(False)))
    #if not xlenv.isXLightsRunning(False):
    #    xlenv.startXLights()
    #print("xLights running: "+str(xlenv.isXLightsRunning(False)))
    #print("xLights running: "+str(xlenv.isXLightsRunning(True)))
    #print("stop xLights: "+str(xlenv.stopXLights()))
    #print("xLights running: "+str(xlenv.isXLightsRunning(False)))
    #print("xLights running: "+str(xlenv.isXLightsRunning(True))) # This gets wrong answer

    print ("start xSchedule: "+str(xlenv.startXSchedule()))
