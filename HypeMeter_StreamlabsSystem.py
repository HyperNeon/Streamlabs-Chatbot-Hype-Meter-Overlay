#---------------------------------------
#   Import Libraries
#---------------------------------------
import sys
import clr
import json
import codecs
import os
import time
import threading

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#---------------------------------------
#   [Required] Script Information
#---------------------------------------
ScriptName = "Hype Meter"
Website = "github.com/hyperneon"
Description = "Hype Meter Overlay That Fills Based on Chat Phrase/Emote Matches"
Creator = "GameTangent" 
Version = "1.1.3"

# ---------------------------------------
#	Set Variables
# ---------------------------------------


SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
ReadMeFile = os.path.join(os.path.dirname(__file__), "ReadMe.txt")
ScriptSettings = None


# ---------------------------------------
#	Script Classes
# ---------------------------------------
class Settings(object):
    """ Class to hold the script settings, matching UI_Config.json. """

    def __init__(self, settingsfile=None):
        """ Load in saved settings file if available else set default values. """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        except:
            #TODO Allow this to take an optional list of phrases to look for intead of single phrase
            self.HypePhrases = "gameta5OnFire,casper5CaSpicy"
            self.SwitchSceneOnMaxHype = "TestScene"
            self.SwitchSceneDelaySeconds = 1
            self.EnableSourceOnMaxHype = "TestSource"
            self.EnableSourceDelaySeconds = 1
            self.EnabledSourceSeconds = 10
            self.CommandPermission = "moderator"
            self.ResetOnMaxHype = True
            self.ResetDelaySeconds = 1
            self.CooldownSeconds = 30
            self.APIKey = ""
            self.LookbackMinutes = 5
            self.BlockLengthSeconds = 5
            self.HypeLevelCount = 100
            self.CountIndividualMatch = False
            self.TickTimeSeconds = 5
            self.ClipAtMaxHype = True


    def Reload(self, jsondata):
        """ Reload settings from Chatbot user interface by given json data. """
        self.__dict__ = json.loads(jsondata, encoding="utf-8")
        return

# ---------------------------------------
#	Functions
# ---------------------------------------
def CallbackLogger(response):
	""" Logs callback error response in scripts logger. """
	parsedresponse = json.loads(response)
	if parsedresponse["status"] == "error":
		Parent.Log("Hype Meter", parsedresponse["error"])
	return
    
def SwitchSceneDelayTimer(scene, seconds):
	""" Switches to a given scene after set seconds. """
	counter = 0
	while counter < seconds:
		time.sleep(1)
		counter += 1
	Parent.SetOBSCurrentScene(scene, CallbackLogger)
	return
    
def EnableSourceDelayTimer(source, seconds, enabled_seconds):
    """ Enables a given source after set seconds. """
    counter = 0
    while counter < seconds:
        time.sleep(1)
        counter += 1
    Parent.SetOBSSourceRender(source, True, None, CallbackLogger)
    if enabled_seconds > 0:
        # Start a new thread for the disable timer
        threading.Thread(target=DisableSourceTimer, args=(source, enabled_seconds)).start()
    return

def DisableSourceTimer(source, seconds):
	""" Disables a given source in optional scene after set seconds. """
	counter = 0
	while counter < seconds:
		time.sleep(1)
		counter += 1
	Parent.SetOBSSourceRender(source, False, None, CallbackLogger)
	return

def SendHypeLevelWebsocket(hype_level):
    # Broadcast WebSocket Event
    payload = {
        "hype_level": hype_level
    }
    Parent.BroadcastWsEvent("EVENT_HYPE_LEVEL", json.dumps(payload))
    return
    
def UpdateEmoteLog(emote_count):
    current_time = time.time()
    
    global EmoteLog
    global LastLogBlockTime
    
    # Check if we're still within the log block time
    if current_time < (LastLogBlockTime + ScriptSettings.BlockLengthSeconds):
        # Add emote count to the current block
        EmoteLog[-1] += emote_count
    else:
        # Block time has passed. Create a new block with the current emote count
        EmoteLog.append(emote_count)
        lookback_length = (ScriptSettings.LookbackMinutes*60) / ScriptSettings.BlockLengthSeconds
        EmoteLog = EmoteLog[-lookback_length:]
        LastLogBlockTime = current_time
    return
    
def CalculateHypeLevel():
    # Simple rolling percent over the period
    # Python makes you coerce integers into floats so multiplying by 1.0
    hype_level = sum(EmoteLog)/(ScriptSettings.HypeLevelCount*1.0)*100
    return hype_level
    
def ActivateReset():
    global AwaitingReset
    global OnCooldown
    global CooldownStartTime
    global EmoteLog
    
    # Parent.Log("Hype Meter", "WE IN HERE")
    # Wipe out the EmoteLog
    EmoteLog = []
    if ScriptSettings.CooldownSeconds:
        OnCooldown = True
        CooldownStartTime = time.time()
    AwaitingReset = False
    
def ActivateMaximumHype():

    global AwaitingReset
    global AwaitingResetStartTime

    # Do various things depending on what the user has configured
    if ScriptSettings.SwitchSceneOnMaxHype:
        # Only if the user has input a scene name do we attempt to switch the scene after configured delay
        threading.Thread(target=SwitchSceneDelayTimer, args=(ScriptSettings.SwitchSceneOnMaxHype, ScriptSettings.SwitchSceneDelaySeconds)).start()
        
    if ScriptSettings.EnableSourceOnMaxHype:
        # Set scene target and call OBS Source Renderer after configured delay
        threading.Thread(target=EnableSourceDelayTimer, args=(ScriptSettings.EnableSourceOnMaxHype, ScriptSettings.EnableSourceDelaySeconds, ScriptSettings.EnabledSourceSeconds)).start()
    
    if ScriptSettings.ResetOnMaxHype:
        AwaitingReset = True
        AwaitingResetStartTime = time.time()
    return
    

#---------------------------------------
#   [Required] Initialize Data / Load Only
#---------------------------------------
def Init():
    """ Initialize script or startup or reload. """

    # Globals
    global ScriptSettings
    global EmoteLog
    global LastLogBlockTime
    global LastTickTime
    global HypeReached
    global AwaitingReset
    global AwaitingResetStartTime
    global OnCooldown
    global CooldownStartTime
    global MeterFreeze

    # Load saved settings and validate values
    ScriptSettings = Settings(SettingsFile)
    EmoteLog = []
    LastLogBlockTime = 0
    LastTickTime = 0
    HypeReached = False
    AwaitingReset = False
    AwaitingResetStartTime = 0
    OnCooldown = False
    CooldownStartTime = 0
    MeterFreeze = False

    return

# ---------------------------------------
# Chatbot Save Settings Function
# ---------------------------------------
def ReloadSettings(jsondata):
    """ Set newly saved data from UI after user saved settings. """

    # Globals
    global ScriptSettings
    
    # Reload saved settings and validate values
    ScriptSettings.Reload(jsondata)

    return
	

def Execute(data):
    global MeterFreeze

    # Check if we have a chat message
    if data.IsChatMessage():
    
        param_zero = data.GetParam(0).lower()
        command_check = param_zero == "!freezehypemeter" or param_zero == "!unfreezehypemeter"
        if command_check and Parent.HasPermission(data.User, ScriptSettings.CommandPermission, ""):
            MeterFreeze = param_zero == "!freezehypemeter"
        elif param_zero == "!maxhypemeter" and Parent.HasPermission(data.User, ScriptSettings.CommandPermission, ""):
            # If a mod wants to max out the meter then lets update it with however many are left to pass 100
            UpdateEmoteLog(ScriptSettings.HypeLevelCount - sum(EmoteLog) + 1)
        elif MeterFreeze == False:
            if AwaitingReset or OnCooldown:
                # Don't resume calculating things until we're off cooldown
                return
            # Count how many times the HypePhrases are found in the message
            match_count = 0
            for phrase in ScriptSettings.HypePhrases.split(','):
                match_count += data.Message.count(phrase)
            if match_count > 0:
                if ScriptSettings.CountIndividualMatch == False:
                    # If we're counting multiple emotes in the same message as 1 then set to 1
                    match_count = 1
            UpdateEmoteLog(match_count)  
    return

def Tick():
    if AwaitingReset and time.time() - AwaitingResetStartTime >= ScriptSettings.ResetDelaySeconds:
        ActivateReset()

    if OnCooldown and time.time() - CooldownStartTime >= ScriptSettings.CooldownSeconds:
        global OnCooldown
        OnCooldown = False
        
    # Every few seconds we'll broadcast the new HypeLevel
    if time.time() - LastTickTime >= ScriptSettings.TickTimeSeconds:
        
        global LastTickTime
        global HypeReached
        
        # Just in case no one is talking, let's send a zero to allow for decay
        UpdateEmoteLog(0)
        hype_level = CalculateHypeLevel()
        if hype_level > 100 and ScriptSettings.ClipAtMaxHype:
            hype_level = 100
        SendHypeLevelWebsocket(hype_level)
        if MeterFreeze == False:
            if hype_level >= 100 and HypeReached == False:
                HypeReached = True
                ActivateMaximumHype()
            if HypeReached == True and hype_level < 100:
                HypeReached = False
        LastTickTime = time.time()
    return

# ---------------------------------------
# Script UI Button Functions
# ---------------------------------------
def OpenReadMe():
    """ Open the script readme file in users default .txt application. """
    os.startfile(ReadMeFile)
    return
