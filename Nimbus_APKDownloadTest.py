import subprocess
import time 
import datetime
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

DebugCode = True

PackageNameList= [
    "com.instagram.android",
    "com.twitter.android",
    "com.facebook.katana"
    ]
ADBCommand= ['adb']
ADBCommand_wakeupPhone =['shell' ,'input' ,'keyevent' ,'KEYCODE_POWER']
ADBCommand_unlockPhone = ['shell' ,'input' ,'keyevent' ,'82' ]
ADBCommand_checkDevices = ['devices']
ADBCommand_go2HomeScreen = ['shell' , 'input' , 'keyevent', 'KEYCODE_HOME']
ADBCommand_installedAPKs = ['shell' ,'pm' ,'list' ,'packages']
ADBCommand_clearLogcat = ['logcat' , '-c']
ADBCommand_getUICompInfo = ['exec-out', 'uiautomator', 'dump', '/dev/tty'] 
ADBCommand_getFinskyInfo = ['logcat']
PackageName="com.intagram.android"
TargetAPK= "market://details?id="+ PackageName
ADBCommand_uninstallAPK = ['uninstall' , PackageName]
ADBCommand_go2PlayStoreAPK= ['shell' ,'am' ,'start', '-a' 'android.intent.action.VIEW', '-d' , TargetAPK]
FinskyTimeout=120 #Sec
ADBCommand_airplaneMode =['shell' ,'cmd' ,'connectivity' ,'airplane-mode'] # ["disable"] #["enable"]

FinskyFile="FinskyLog.txt"

indexAPKInstallStart="Will queue " + PackageName
indexAPKSize= "status:4, size: 0" #"sufficient disk space space available for " + PackageName
indexAPKDLStartTime=":RUNNING:0%"
indexAPKDLEndTime=  "Submit start. " + PackageName  #"VerifyApps: Verification complete"
indexAPKInstallationComplete="SCH: job service finished with" 

airplaneMode_enable ='enabled'
airplaneMode_disable = 'disabled'

def setADBCommand(pkName, tSec):
    global PackageName
    global TargetAPK
    global ADBCommand_uninstallAPK
    global ADBCommand_go2PlayStoreAPK
    global FinskyTimeout
    global indexAPKInstallStart
    global indexAPKDLEndTime

    PackageName=pkName
    TargetAPK= "market://details?id="+ PackageName
    ADBCommand_uninstallAPK = ['uninstall' , PackageName]
    ADBCommand_go2PlayStoreAPK= ['shell' ,'am' ,'start', '-a' 'android.intent.action.VIEW', '-d' , TargetAPK]
    FinskyTimeout=tSec #Sec
    indexAPKInstallStart="Will queue " + pkName
    indexAPKDLEndTime=  "Submit start. " + pkName  

def printDebug(printString):
    if DebugCode:
        print (printString)


def sendADBCommand (lCommand):
    # Execute the adb command and capture the output
    Complete_ADBCommand = ADBCommand + lCommand
    process = subprocess.Popen(Complete_ADBCommand, stdout=subprocess.PIPE)
    outputCL= ""
    while True:
        temp = process.stdout.readline().decode() 
        outputCL= outputCL+ temp 
        if temp == '' and process.poll() is not None:
            break
    return outputCL

def checkDeviceConnected():
    adbOutput= sendADBCommand(ADBCommand_checkDevices)
    if adbOutput.endswith("List of devices attached\n\n" ):
        print ("\n*** No device is connected to the Computer ****")
        print ("please connect an Android device in Developer Mode  to the computer and rerunt the test\n" )
        return False
    else:    
        print(adbOutput.strip())
        return True

def checkAPKInstalled():
    adbOutput= sendADBCommand(ADBCommand_installedAPKs)
    if PackageName in adbOutput:
        return True
    else: 
        return False

def tapUIButton(buttonName):
    pageInfo= sendADBCommand(ADBCommand_getUICompInfo)
    sXYButtonLimits = ((pageInfo.split(buttonName,1)[1]).split("bounds=")[1]).split(" />")[0]
    iXYButtonLimits = sXYButtonLimits.replace('][',',').replace ('[','').replace(']','').replace('"','').split(',')
    xButtonLimit= (int(iXYButtonLimits[0])+int(iXYButtonLimits[2]))/2
    yButtonLimit= (int(iXYButtonLimits[1])+int(iXYButtonLimits[3]))/2
    sendADBCommand (['shell', 'input','tap',str(xButtonLimit),str(yButtonLimit)])

def analyzeFidnskyFile():
    apkInstallStart=""
    apkSize=""
    apkDLStartTime=""
    apkDLEndTime=""
    apkInstallationComplete=""
    apkInstallStart_NotReceived= True
    apkSize_NotReceived= True
    apkDLStartTime_NotReceived= True
    apkDLEndTime_NotReceived= True
    apkInstallationComplete_NotReceived= True

    loopTimeout= time.time() + FinskyTimeout
    Complete_ADBCommand = ADBCommand + ADBCommand_getFinskyInfo
    process = subprocess.Popen(Complete_ADBCommand, stdout=subprocess.PIPE)
    while True:
        if time.time() > loopTimeout:
            return  -1 , -1 , -1 , -1 , -1 
        temp = process.stdout.readline().decode()
        if temp.find ("Finsky")!=-1:
            #print (temp)
            if (temp.find(indexAPKInstallStart)!= -1) & apkInstallStart_NotReceived :
                printDebug ("indexAPKInstallStart*************************************" + temp)
                apkInstallStartDate = temp.split()[0]
                apkInstallStartDate_Sec= datetime.datetime(datetime.date.today().year, int(apkInstallStartDate.split('-')[0]), int(apkInstallStartDate.split('-')[1]), 0, 0, 0).timestamp()
                apkInstallStart = temp.split()[1]
                apkInstallStart_Sec = int(apkInstallStart.split(':')[0])*3600 + int(apkInstallStart.split(':')[1])*60 + float(apkInstallStart.split(':')[2])
                apkInstallStart_TotalSec = apkInstallStartDate_Sec + apkInstallStart_Sec
                print ( "Install Start Time = " + apkInstallStartDate + " " +  apkInstallStart) 
                printDebug ( "Install Start Time Sec = " + str(apkInstallStartDate_Sec) +  " + " + str(apkInstallStart_Sec) + " = " + str(apkInstallStart_TotalSec) + " Sec")
                apkInstallStart_NotReceived = False
            if  (apkInstallStart != "") & apkDLStartTime_NotReceived:
                if temp.find(indexAPKDLStartTime) != -1:
                    printDebug ("indexAPKDLStartTime*************************************" + temp)
                    apkDLStartTimeDate = temp.split()[0]
                    apkDLStartTimeDate_Sec= datetime.datetime(datetime.date.today().year, int(apkDLStartTimeDate.split('-')[0]), int(apkDLStartTimeDate.split('-')[1]), 0, 0, 0).timestamp()
                    apkDLStartTime = temp.split()[1]
                    apkDLStartTime_Sec = int(apkDLStartTime.split(':')[0])*3600 + int(apkDLStartTime.split(':')[1])*60 + float(apkDLStartTime.split(':')[2])
                    apkDLStartTime_TotalSec = apkDLStartTimeDate_Sec + apkDLStartTime_Sec
                    print ("APK Download Start Time = " + apkDLStartTimeDate + " " + apkDLStartTime ) 
                    printDebug ( "APK Download Start Time Sec = " + str(apkDLStartTimeDate_Sec) +  " + " + str(apkDLStartTime_Sec) + " = " + str(apkDLStartTime_TotalSec) + " Sec")
                    apkDLStartTime_NotReceived =False  
            if  (apkDLStartTime != "") & apkSize_NotReceived:
                if temp.find(indexAPKSize)!= -1:
                    printDebug ("indexAPKSize*************************************" + temp)
                    apkSize= temp.split('/')[1].strip()
                    apkSize_MBit =  int(apkSize) * 0.000008
                    print ("APK File Size = " + apkSize + " Byte = " + str(apkSize_MBit) + "MBit")
                    apkSize_NotReceived =False
            if  (apkSize != "") & apkDLEndTime_NotReceived:
                if temp.find(indexAPKDLEndTime) != -1:
                    printDebug ("indexAPKDLEndTime*************************************" + temp)
                    apkDLEndTimeDate = temp.split()[0]
                    apkDLEndTimeDate_Sec= datetime.datetime(datetime.date.today().year, int(apkDLEndTimeDate.split('-')[0]), int(apkDLEndTimeDate.split('-')[1]), 0, 0, 0).timestamp()                    
                    apkDLEndTime = temp.split()[1]
                    apkDLEndTime_Sec = int(apkDLEndTime.split(':')[0])*3600 + int(apkDLEndTime.split(':')[1])*60 + float(apkDLEndTime.split(':')[2])
                    apkDLEndTime_TotalSec = apkDLEndTimeDate_Sec + apkDLEndTime_Sec
                    print ("APK Download End Time = " + apkDLEndTimeDate + " " + apkDLEndTime ) 
                    printDebug ( "APK Download End Time Sec = " + str(apkDLEndTimeDate_Sec) +  " + " + str(apkDLEndTime_Sec) + " = " + str(apkDLEndTime_TotalSec) + " Sec")                             
                    apkDLEndTime_NotReceived = False
            if (apkDLEndTime != "") & apkInstallationComplete_NotReceived :
                if temp.find(indexAPKInstallationComplete) !=-1:
                    printDebug ("indexAPKInstallationComplete*************************************" + temp)
                    apkInstallationCompleteDate = temp.split()[0]
                    apkInstallationCompleteDate_Sec= datetime.datetime(datetime.date.today().year, int(apkInstallationCompleteDate.split('-')[0]), int(apkInstallationCompleteDate.split('-')[1]), 0, 0, 0).timestamp()                       
                    apkInstallationComplete = temp.split()[1]
                    apkInstallationComplete_Sec = int(apkInstallationComplete.split(':')[0])*3600 + int(apkInstallationComplete.split(':')[1])*60 + float(apkInstallationComplete.split(':')[2])
                    apkInstallationComplete_TotalSec = apkInstallationCompleteDate_Sec + apkInstallationComplete_Sec
                    print ("Installation Complete = " + apkInstallationCompleteDate + " " + apkInstallationComplete ) 
                    printDebug ( "Installation Complete Sec = " + str(apkInstallationCompleteDate_Sec) +  " + " + str(apkInstallationComplete_Sec) + " = " + str(apkInstallationComplete_TotalSec) + " Sec")                          
                    apkInstallationComplete_NotReceived = False
                    break
    
    printDebug ( "\n*** Finsky Summary ***" +
                "\nInstall Start Time = " + apkInstallStart + " = " + str(apkInstallStart_Sec) + " Sec" + 
                "\nAPK File Size = " + apkSize + " Byte = " + str(apkSize_MBit) + " MBit" +
                "\nAPK Download Start Time = " + apkDLStartTime + " = " + str(apkDLStartTime_Sec)  + " Sec" + 
                "\nAPK Download End Time = " + apkDLEndTime + " = " + str(apkDLEndTime_Sec)  + " Sec" +
                "\nInstallation Complete = " + apkInstallationComplete + " = " + str(apkInstallationComplete_Sec)  + " Sec" )
    return  apkInstallStart_TotalSec , apkSize_MBit, apkDLStartTime_TotalSec, apkDLEndTime_TotalSec, apkInstallationComplete_TotalSec       

class ApkGuiApp:
    def __init__(self, master=None):
        # build ui
        self.UI_tlfr = tk.Tk() if master is None else tk.Toplevel(master)
        self.UI_tlfr.title("Nimbus APK Test App")
        self.UI_tlfr.configure(height=200, width=200)
        
        
        self.UI_fr_TopAirPlaneMode = tk.Frame(self.UI_tlfr)
        self.UI_fr_TopAirPlaneMode.configure(height=200, width=200)
        self.UI_fr_TopAirPlaneMode_sub_Left = tk.Frame(self.UI_fr_TopAirPlaneMode)
        self.UI_fr_TopAirPlaneMode_sub_Left.configure(height=200, width=200)
        self.UI_btn_AirplaneMode = tk.Button(self.UI_fr_TopAirPlaneMode_sub_Left, command= self.airplaneModeState)
        self.UI_btn_AirplaneMode.configure(
            font="TkDefaultFont",
            foreground="#8924ae",
            text='Airplane Mode')
        self.UI_btn_AirplaneMode.pack(expand="true", fill="x", side="top")
        self.UI_btn_AirplaneMode.pack(expand="true", fill="x", padx=10, side="top")
        self.UI_fr_TopAirPlaneMode_sub_Left.pack(side="left")
        self.UI_fr_TopAirPlaneMode_sub_Right = tk.Frame(self.UI_fr_TopAirPlaneMode)
        self.UI_fr_TopAirPlaneMode_sub_Right.configure(height=200, width=200)
        self.UI_lbl_AirplaneMode = tk.Label(self.UI_fr_TopAirPlaneMode_sub_Right)
        self.UI_lbl_AirplaneMode.configure(text=' disable ')
        self.UI_lbl_AirplaneMode.pack(padx=0, side="left")
        self.UI_fr_TopAirPlaneMode_sub_Right.pack(side="left")
        self.UI_fr_TopAirPlaneMode.pack(
            expand="true",
            fill="x",
            padx=10,
            pady=10,
            side="top")
        

        self.UI_fr_Top = tk.Frame(self.UI_tlfr)
        self.UI_fr_Top.configure(height=200, width=200)
        self.UI_fr_Top_sub_Left = tk.Frame(self.UI_fr_Top)
        self.UI_fr_Top_sub_Left.configure(height=200, width=200)
        self.om_APKList_Var = tk.StringVar(value=PackageNameList[0])
        om_APKlist_Values = PackageNameList
        self.UI_om_APKList = tk.OptionMenu(
            self.UI_fr_Top_sub_Left, self.om_APKList_Var, *om_APKlist_Values, command=None)
        self.UI_om_APKList.pack(side="top")
        self.UI_fr_Top_sub_Left.pack(side="left")
        self.UI_fr_Top_sub_Right = tk.Frame(self.UI_fr_Top)
        self.UI_fr_Top_sub_Right.configure(height=200, width=200)
        self.UI_lbl_Timeout = tk.Label(self.UI_fr_Top_sub_Right)
        self.UI_lbl_Timeout.configure(text='     Timeout (sec): ')
        self.UI_lbl_Timeout.pack(padx=0, side="left")
        self.UI_ent_Timeout = tk.Entry(self.UI_fr_Top_sub_Right)
        self.UI_ent_Timeout.configure(justify="right", width=4)
        self.entTimeout_text= '120'
        self.UI_ent_Timeout.delete("0", "end")
        self.UI_ent_Timeout.insert("0", self.entTimeout_text)
        self.UI_ent_Timeout.pack(side="right")
        self.UI_fr_Top_sub_Right.pack(side="right")
        self.UI_fr_Top.pack(
            expand="true",
            fill="x",
            padx=10,
            pady=10,
            side="top")
        self.UI_fr_StartTest = tk.Frame(self.UI_tlfr)
        self.UI_fr_StartTest.configure(height=200, width=200)
        self.UI_btn_StartTest = tk.Button(self.UI_fr_StartTest, command= self.startAPKTest)
        self.UI_btn_StartTest.configure(
            font="TkDefaultFont",
            foreground="#8924ae",
            text='Start APK Download Test')
        self.UI_btn_StartTest.pack(expand="true", fill="x", side="top")
        self.UI_fr_StartTest.pack(expand="true", fill="x", padx=10, side="top")
        self.UI_fr_Log = tk.LabelFrame(self.UI_tlfr)
        self.UI_fr_Log.configure(height=200, text='Log', width=200)
        self.UI_stxt_Log = ScrolledText(self.UI_fr_Log)
        self.UI_stxt_Log.configure(height=15, width=60)
        self.UI_stxt_Log.pack(expand="true", fill="both", side="top")
        self.UI_fr_Log.pack(expand="true", fill="both", padx=10, side="top")
        self.UI_fr_Bottom = tk.Frame(self.UI_tlfr)
        self.UI_fr_Bottom.configure(height=200, width=200)
        self.UI_btn_Quit = tk.Button(self.UI_fr_Bottom, command= self.btnQuite_Clicked)
        self.UI_btn_Quit.configure(foreground="#ff031a", text='Quit')
        self.UI_btn_Quit.pack(side="top")
        self.UI_fr_Bottom.pack(
            expand="false",
            fill="x",
            padx=10,
            pady=10,
            side="top")
     
        # Main widget
        self.mainwindow = self.UI_tlfr

    def run(self):
        self.UI_lbl_AirplaneMode.configure(text= sendADBCommand(ADBCommand_airplaneMode).strip()) 
        self.mainwindow.mainloop()

    def startAPKTest(self):
        self.UI_stxt_Log.delete("1.0",tk.END)
        if sendADBCommand(ADBCommand_airplaneMode).strip() == airplaneMode_enable:
            self.printLog ("\n**** Phone is in Airplane mode ****  \nPlease disable the Airplane mode and rerun the test.")
            return() 
        FinskyTimeout = int(self.UI_ent_Timeout.get())
        PackageName =   self.om_APKList_Var.get()  
        if self.UI_ent_Timeout.get() == "":
            FinskyTimeout =120
        if self.om_APKList_Var.get() == "":
            PackageName =   "com.facebook.katana"  
        setADBCommand (PackageName,FinskyTimeout )
        if checkDeviceConnected() == False:
            self.printLog ("No device is connected to the Nimbus APK Test App!")
            return()
        print ('Wakeup the phone')
        sendADBCommand(ADBCommand_unlockPhone)
        print ('Unlock the screen')
        sendADBCommand(ADBCommand_unlockPhone)
        print ('Switch to phone Home screen')
        sendADBCommand(ADBCommand_go2HomeScreen)
        if checkAPKInstalled() == True:
            print ("Unintalling the " + PackageName)
            sendADBCommand(ADBCommand_uninstallAPK)
        print ('Clear the ADB Log')    
        sendADBCommand(ADBCommand_clearLogcat)    
        time.sleep(1)
        print ('Go to APK page at Google PlayStore')
        sendADBCommand(ADBCommand_go2PlayStoreAPK)
        print ('Click the install button')
        tapUIButton('Install')
        printDebug ('Analyze the Finsky file information')
        rec_apkInstallStart_TotalSec , rec_apkSize_MBit, rec_apkDLStartTime_TotalSec, rec_apkDLEndTime_TotalSec, rec_apkInstallationComplete_TotalSec = analyzeFidnskyFile()

        if rec_apkInstallStart_TotalSec == -1 :
            self.printLog ( "*****Time Out*****")
        else: 
            self.printLog("\n*** RAW Data Summary: "+ PackageName +" ***" +
                    "\nInstall Start Time = " +str(rec_apkInstallStart_TotalSec) + " Sec" + 
                    "\nAPK File Size = " + str(rec_apkSize_MBit) + " MBit" +
                    "\nAPK Download Start Time = " + str(rec_apkDLStartTime_TotalSec)  + " Sec" + 
                    "\nAPK Download End Time = " + str(rec_apkDLEndTime_TotalSec)  + " Sec" +
                    "\nInstallation Complete = " + str(rec_apkInstallationComplete_TotalSec)  + " Sec" )

            self.printLog("\n\n--- Result: "+ PackageName +" ---")
            DownloadTime_Sec = rec_apkDLEndTime_TotalSec - rec_apkDLStartTime_TotalSec
            self.printLog("APK Download time: " + '%.2f' %DownloadTime_Sec+ " Sec")
            AveDownloadSpeed = rec_apkSize_MBit/DownloadTime_Sec
            self.printLog("Average APK Download Speed: " + '%.3f' %AveDownloadSpeed + " mbps")
            TotalTime = rec_apkInstallationComplete_TotalSec- rec_apkInstallStart_TotalSec
            self.printLog("Total APK Download and Install time: " + '%.2f' %TotalTime + " Sec")
            print("----------------")
        
        # action method
    
    def btnQuite_Clicked(self):
        self.printLog("Quit pressed")
        quit()

    def airplaneModeState (self):
       startAirplaneMode = sendADBCommand(ADBCommand_airplaneMode).strip()
       if startAirplaneMode == airplaneMode_enable :
           sendADBCommand(ADBCommand_airplaneMode + ['disable'])
           updatedAirplaneMode = airplaneMode_disable
       else:
            sendADBCommand(ADBCommand_airplaneMode + ['enable'])
            updatedAirplaneMode = airplaneMode_enable
       self.UI_lbl_AirplaneMode.configure(text= updatedAirplaneMode) 
       self.printLog ("\nAirplane Mode is changed from " + startAirplaneMode + " to " + updatedAirplaneMode)


    def printLog(self, sMessage):
        print (sMessage)
        self.UI_stxt_Log.insert(tk.INSERT, "\n"+sMessage)

def main():
    NimbusApp = ApkGuiApp()
    NimbusApp.run()  

if __name__ == "__main__":
    main()



