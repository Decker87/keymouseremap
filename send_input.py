import ctypes
from ctypes import wintypes
import time
from . import codes

user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_ulong), ("y", ctypes.c_ulong)]

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize

# Functions
def pressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=hexKeyCode, dwFlags=KEYEVENTF_SCANCODE))
    # k = (1, ctypes.byref(x), ctypes.sizeof(x))
    # print("SendInput args: %s" % (x.__str__()))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def releaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=hexKeyCode, dwFlags=KEYEVENTF_KEYUP+KEYEVENTF_SCANCODE))
    # k = (1, ctypes.byref(x), ctypes.sizeof(x))
    # print("SendInput args: %s" % (x.__str__()))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

# mouse_event: https://msdn.microsoft.com/en-us/library/windows/desktop/ms646260(v=vs.85).aspx
mouseButtonCodes = {
    codes.MOUSE_LEFT:   {'down': 0x02, 'up': 0x04},
    codes.MOUSE_RIGHT:  {'down': 0x08, 'up': 0x10},
    codes.MOUSE_MID:    {'down': 0x20, 'up': 0x40},
}

def pressMouseButton(button):
    user32.mouse_event(mouseButtonCodes[button]['down'], 0, 0, 0, 0)

def releaseMouseButton(button):
    user32.mouse_event(mouseButtonCodes[button]['up'], 0, 0, 0, 0)

def getCursorPosition():
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)

def setCursorPosition(pos):
    x, y = pos
    user32.SetCursorPos(x, y)

# Experimental
def pressKeyIndirect(hexKeyCode):
    user32.keybd_event(hexKeyCode, 0, 2, 0)

def releaseKeyIndirect(hexKeyCode):
    user32.keybd_event(hexKeyCode, 0, 0, 0)
