import hexchat
import re

__module_name__ = 'Triggers'
__module_version__ = '1'
__module_description__ = 'Auto-respond to specific key words'


#---------------------------------------------------------------------------------
#
# Description:   Based on possible trigger events call corresponding functions
#
#---------------------------------------------------------------------------------
def msg_triggers_cb(word, word_eol, userdata):

    channel = hexchat.get_info("channel")
    allowedChannels = ["#pcasb", "#prettyanon"]
    if channel not in allowedChannels:
        return hexchat.EAT_NONE

    triggerList = ["\\bmangas\\b", "\\banimes\\b", "\\bgrammer\\b", "\\bvlc\\b", "\\bprozess\\b", "\\bwoah\\b"]
    responseList = ["mangas", "animes", "grammer", "vlc", "prozess", "woah"]

    count = 0
    for trigger in triggerList:
        compiled = re.compile(trigger, re.IGNORECASE)
        result = compiled.search(word[1])  
        if result is not None:
            hexchat.command("MSG %s \00303>%s" %(hexchat.get_info("channel"), responseList[count]))
        count += 1

    return hexchat.EAT_NONE

hexchat.hook_print("Channel Message", msg_triggers_cb)
hexchat.hook_print("Channel Msg Hilight", msg_triggers_cb)

#---------------------------------------------------------------------------------
#
# Description:   Based on possible trigger events call corresponding functions
#
#---------------------------------------------------------------------------------
def cmd_sp_cb(word, word_eol, userdata):    
    hexchat.command("nick SP")
    hexchat.command("nickserv ghost SP <pw>")
    hexchat.command("nickserv recover SP <pw>")
    hexchat.command("nick SP")
    hexchat.command("nickserv identify <pw>")
    return hexchat.EAT_ALL

hexchat.hook_command("sp", cmd_sp_cb)
