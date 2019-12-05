# keymouseremap
Library for quickly and easily remapping keys and mouse events. Windows only.

Usage is something like

```
from keymouseremap import codes, remapper

if __name__ == "__main__":
    # Check that we're running as admin
    import ctypes
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("ERROR: Must be running as admin!")
        exit(1)

    # Map middle click to right AND left click at same time
    r = remapper.Remapper()
    r.registerAction(remapper.triggerTypes.MOUSEDOWN, codes.MOUSE_MID, remapper.actionTypes.MOUSEDOWN, codes.MOUSE_LEFT)
    r.registerAction(remapper.triggerTypes.MOUSEUP, codes.MOUSE_MID, remapper.actionTypes.MOUSEUP, codes.MOUSE_LEFT)
    r.registerAction(remapper.triggerTypes.MOUSEDOWN, codes.MOUSE_MID, remapper.actionTypes.MOUSEDOWN, codes.MOUSE_RIGHT)
    r.registerAction(remapper.triggerTypes.MOUSEUP, codes.MOUSE_MID, remapper.actionTypes.MOUSEUP, codes.MOUSE_RIGHT)
    r.start(windowRegexStr='.*Skyrim.*')
```
