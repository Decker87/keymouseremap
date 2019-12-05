import pythoncom, pyHook
import Queue, threading, re

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

def debugPrintEvent(e):
    print("=" * 40)
    for attr in dir(e):
        # Ignore internals and properties of events
        if attr.startswith("__") or attr.startswith("Is"):
            continue
        else:
            print("e.%s: %s" % (attr, e.__getattribute__(attr).__repr__()))
    print("=" * 40)

def getClosedEventHandler(windowRegexCompiled, keyCodes, eventQueue):
    '''Returns an event handler with key information closed (as in closure).'''
    # Note: Anything that is material in deciding whether an event should be passed through or blocked MUST
    #   be dealt with in the event handler, since the handler needs to return a bool that tells pyHook
    #   whether to pass the event through to the active window or block it.

    # Holding a key will send multiple keydown events. We use a set to track when they go up or down.
    # Ostensibly, the pyHook library gives us events with a property called "Transition" which sounds like
    # it should do this, but I could not get it to do so.
    keysDown = set()

    def closedEventHandler(e):
        # If it's the wrong window, do nothing
        if not windowRegexCompiled.match(e.WindowName):
            return True

        # If it's not in our key codes, do nothing
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

        # Take action!
        eventQueue.put(e, block=False)
        return False

    return closedEventHandler

def hookInBackground(eventHandler):
    '''Run the message pump in the background while hooking events with the given event handler.'''
    def hookAndPumpInSingleThread():
        # These things all must happen on the same thread, so must be part of the same function
        hm = pyHook.HookManager()
        hm.KeyAll = eventHandler
        hm.HookKeyboard()
        pythoncom.PumpMessages()

    pumpingThread = threading.Thread(target=hookAndPumpInSingleThread)
    pumpingThread.daemon = True
    pumpingThread.start()

# API functions
def getEventQueueWithHookedEvents(windowRegexStr, keyCodes = []):
    '''Returns a queue object that will get raw key events.'''
    eventQueue = Queue.Queue()
    windowRegexCompiled = re.compile(windowRegexStr)
    closedEventHandler = getClosedEventHandler(windowRegexCompiled, keyCodes, eventQueue)
    hookInBackground(closedEventHandler)
    return eventQueue

def test():
    '''Does a quick test of this file, debug prints events for G and H keys.'''
    import codes
    eventQueue = getEventQueueWithHookedEvents(".*", [codes.VK_G, codes.VK_H])

    while True:
        e = eventQueue.get(block=True)
        debugPrintEvent(e)

if __name__ == "__main__":
    test()
