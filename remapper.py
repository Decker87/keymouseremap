from collections import defaultdict
from hook import getEventQueueWithHookedEvents, debugPrintEvent
from send_input import pressKey, releaseKey, pressMouseButton, releaseMouseButton
import codes

# Used like enums
class triggerTypes:
    KEYDOWN = 0
    KEYUP = 1
    MOUSEDOWN = 2
    MOUSEUP = 3
class actionTypes:
    KEYDOWN = 0
    KEYUP = 1
    MOUSEDOWN = 2
    MOUSEUP = 3

class Remapper:
    '''A useful thing that can remap some keys.'''
    # Design idea: everything boils down to registering some granular actions to take upon certain triggers.
    #   For example, when the middle mouse button goes down, take N actions. Everything else to make it easy
    #   for the user can be syntactic sugar around that.

    def __init__(self):
        # Registry looks like: registry[(triggertype, triggerspec)] = [(actionType, actionSpec)]
        self.actionRegistry = defaultdict(list)

    def registerAction(self, triggerType, triggerSpec, actionType, actionSpec):
        self.actionRegistry[(triggerType, triggerSpec)].append((actionType, actionSpec))
        pass

    def _performAction(self, actionType, actionSpec):
        if actionType == actionTypes.KEYDOWN:
            pressKey(actionSpec)
        elif actionType == actionTypes.KEYUP:
            releaseKey(actionSpec)
        elif actionType == actionTypes.MOUSEDOWN:
            pressMouseButton(actionSpec)
        elif actionType == actionTypes.MOUSEUP:
            releaseMouseButton(actionSpec)

    def _getKeyCodesAndMouseButtons(self):
        '''Uses the current action registry to determine which mouse buttons and key codes need to be hooked.'''
        keyCodes = [triggerSpec for (triggerType, triggerSpec) in self.actionRegistry.keys() if triggerType == triggerTypes.KEYDOWN or triggerType == triggerTypes.KEYUP]
        keyCodes = list(set(keyCodes))

        mouseButtons = [triggerSpec for (triggerType, triggerSpec) in self.actionRegistry.keys() if triggerType == triggerTypes.MOUSEDOWN or triggerType == triggerTypes.MOUSEUP]
        mouseButtons = list(set(mouseButtons))

        return keyCodes, mouseButtons
    
    def _getTriggerTypeAndSpec(self, e):
        if e.MessageName == 'key down':
            return triggerTypes.KEYDOWN, e.KeyID
        if e.MessageName == 'key up':
            return triggerTypes.KEYUP, e.KeyID
        if e.MessageName == 'mouse left down':
            return triggerTypes.MOUSEDOWN, "left"
        if e.MessageName == 'mouse left up':
            return triggerTypes.MOUSEUP, "left"
        if e.MessageName == 'mouse middle down':
            return triggerTypes.MOUSEDOWN, "middle"
        if e.MessageName == 'mouse middle up':
            return triggerTypes.MOUSEUP, "middle"
        if e.MessageName == 'mouse right down':
            return triggerTypes.MOUSEDOWN, "right"
        if e.MessageName == 'mouse right up':
            return triggerTypes.MOUSEUP, "right"

    def start(self, windowRegexStr):
        keyCodes, mouseButtons = self._getKeyCodesAndMouseButtons()

        # Do the remapping!
        eventQueue = getEventQueueWithHookedEvents(windowRegexStr, keyCodes=keyCodes, mouseButtons=mouseButtons)
        while True:
            e = eventQueue.get(block=True)

            # Process all actions associated with this trigger
            triggerType, triggerSpec = self._getTriggerTypeAndSpec(e)
            for (actionType, actionSpec) in self.actionRegistry[(triggerType, triggerSpec)]:
                self._performAction(actionType, actionSpec)

if __name__ == "__main__":
    # Test: Map the W key to Y, and middle button to right button
    r = Remapper()
    r.registerAction(triggerTypes.KEYDOWN, codes.VK_W, actionTypes.KEYDOWN, codes.VK_Y)
    r.registerAction(triggerTypes.KEYUP, codes.VK_W, actionTypes.KEYUP, codes.VK_Y)
    r.registerAction(triggerTypes.MOUSEDOWN, "middle", actionTypes.MOUSEDOWN, "right")
    r.registerAction(triggerTypes.MOUSEUP, "middle", actionTypes.MOUSEUP, "right")
    r.start(".*")