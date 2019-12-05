from collections import defaultdict
from hook import getEventQueueWithHookedEvents, debugPrintEvent
from send_input import pressKey, releaseKey
import codes

# Used like enums
class triggerTypes:
    KEYDOWN = 0
    KEYUP = 1
class actionTypes:
    KEYDOWN = 0
    KEYUP = 1

_messageNameToTriggerType = {
    "key down": triggerTypes.KEYDOWN,
    "key up":   triggerTypes.KEYUP,
}

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
        if actionType == actionTypes.KEYUP:
            releaseKey(actionSpec)

    def start(self, windowRegexStr):
        # Determine which keycodes to capture
        keyCodes = [triggerSpec for (triggerType, triggerSpec) in self.actionRegistry.keys() if triggerType == triggerTypes.KEYDOWN or triggerType == triggerTypes.KEYUP]
        keyCodes = list(set(keyCodes))

        # Do the remapping!
        eventQueue = getEventQueueWithHookedEvents(windowRegexStr, keyCodes)
        while True:
            e = eventQueue.get(block=True)

            # Determine which trigger and spec to match
            triggerType = _messageNameToTriggerType[e.MessageName]
            triggerSpec = e.KeyID

            # Process all actions associated with this trigger
            for (actionType, actionSpec) in self.actionRegistry[(triggerType, triggerSpec)]:
                self._performAction(actionType, actionSpec)

if __name__ == "__main__":
    # Test: Map the W key to Y
    r = Remapper()
    r.registerAction(triggerTypes.KEYDOWN, codes.VK_W, actionTypes.KEYDOWN, codes.VK_Y)
    r.registerAction(triggerTypes.KEYUP, codes.VK_W, actionTypes.KEYUP, codes.VK_Y)
    r.start(".*")
