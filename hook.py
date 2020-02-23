import pythoncom, pyWinhook
import queue, threading, re, time
from . import codes

# KEYBOARD EVENT LIKE
# e.Alt: 0
# e.Ascii: 3
# e.Extended: 1
# e.Injected: 0
# e.Key: 'Cancel'
# e.KeyID: 3
# e.Message: 256
# e.MessageName: 'key down'
# e.ScanCode: 70
# e.Time: -1222330843
# e.Transition: 0
# e.Window: 3932860
# e.WindowName: 'MINGW64:/d/Users/Adam/programming/keymouseremap'
# e.flags: 1

# MOUSE EVENT LIKE
# e.Injected: 0
# e.Message: 516
# e.MessageName: 'mouse right down'
# e.Position: (768, 694)
# e.Time: -1219646062
# e.Wheel: 0
# e.Window: 3932860
# e.WindowName: 'MINGW64:/d/Users/Adam/programming/keymouseremap'

def debugPrintEvent(e):
    print("=" * 40)
    for attr in dir(e):
        # Ignore internals and properties of events
        if attr.startswith("__") or attr.startswith("Is"):
            continue
        else:
            print("e.%s: %s" % (attr, e.__getattribute__(attr).__repr__()))
    print("=" * 40)

def getClosedEventHandler(windowRegexCompiled, keyCodes, mouseButtons, eventQueue):
    '''Returns an event handler with key information closed (as in closure).'''
    # Note: Anything that is material in deciding whether an event should be passed through or blocked MUST
    #   be dealt with in the event handler, since the handler needs to return a bool that tells pyHook
    #   whether to pass the event through to the active window or block it.

    # Holding a key will send multiple keydown events. We use a set to track when they go up or down.
    # Ostensibly, the pyHook library gives us events with a property called "Transition" which sounds like
    # it should do this, but I could not get it to do so.
    keysDown = set()

    mouseMessageNameToButton = {
        'mouse left down': codes.MOUSE_LEFT,
        'mouse left up': codes.MOUSE_LEFT,
        'mouse right down': codes.MOUSE_RIGHT,
        'mouse right up': codes.MOUSE_RIGHT,
        'mouse middle down': codes.MOUSE_MID,
        'mouse middle up': codes.MOUSE_MID,
    }

    def closedEventHandler(e):
        # If it's the wrong window, do nothing
        if not windowRegexCompiled.match(e.WindowName):
            return True

        if 'key' in e.MessageName:
            if e.KeyID not in keyCodes:
                return True

            # If it's a key down event but it's already down, ignore it.
            if e.MessageName == 'key down' and e.KeyID in keysDown:
                return True
            
            # Manage keysDown state
            if e.MessageName == 'key down':
                keysDown.add(e.KeyID)
            elif e.MessageName == 'key up':
                keysDown.discard(e.KeyID)

        elif 'mouse' in e.MessageName:
            mouseButton = mouseMessageNameToButton[e.MessageName]
            if mouseButton not in mouseButtons:
                return True

        # Take action!
        eventQueue.put(e, block=False)
        return False

    return closedEventHandler

def hookInBackground(eventHandler):
    '''Run the message pump in the background while hooking events with the given event handler.'''
    def hookAndPumpInSingleThread():
        # These things all must happen on the same thread, so must be part of the same function
        hm = pyWinhook.HookManager()
        hm.KeyAll = eventHandler
        hm.HookKeyboard()
        hm.MouseAllButtons = eventHandler
        hm.HookMouse()
        pythoncom.PumpMessages()

    pumpingThread = threading.Thread(target=hookAndPumpInSingleThread)
    pumpingThread.daemon = True
    pumpingThread.start()

# API functions
def getEventQueueWithHookedEvents(windowRegexStr, keyCodes = [], mouseButtons = []):
    '''Returns a queue object that will get raw key events.'''
    eventQueue = queue.Queue()
    windowRegexCompiled = re.compile(windowRegexStr)
    closedEventHandler = getClosedEventHandler(windowRegexCompiled, keyCodes, mouseButtons, eventQueue)
    hookInBackground(closedEventHandler)
    return eventQueue

def test():
    '''Does a quick test of this file, debug prints events for G and H keys.'''
    import codes
    eventQueue = getEventQueueWithHookedEvents(".*", keyCodes=[codes.VK_G, codes.VK_H], mouseButtons=['right'])

    while True:
        e = eventQueue.get(block=True)
        debugPrintEvent(e)

if __name__ == "__main__":
    test()
