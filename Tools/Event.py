# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
	kongzhao
	kongzhao135@163.com
Date:
	2018/1/11
Description:

----------------------------------------------------------------------------"""
import time
from pymouse import *
from pykeyboard import *


_mouse = PyMouse()
_keyboard = PyKeyboard()

LEFT_MOUSE = 1
RIGHT_MOUSE = 2

KEY_F = _keyboard.function_keys  # F1: KEY_F[1]
KEY_SPACE = _keyboard.space_key
KEY_ENTER = _keyboard.enter_key
KEY_ESC = _keyboard.escape_key


# ---- listen mouse & keyboard event
class GKeyBoardEvent(PyKeyboardEvent):
    def __init__(self, tapHandler=None):
        PyKeyboardEvent.__init__(self)
        self.tapHandler = tapHandler

    def handler(self, event):
        self._tap(event)
        return True

    def _tap(self, event):
        # 源码中的在windows下有些错误，有时Ascii获得不了。
        keycode = event.KeyID
        press_bool = (event.Message in [self.hc.WM_KEYDOWN, self.hc.WM_SYSKEYDOWN])
        if keycode not in self.hc.id_to_vk:
            character = chr(keycode)
        else:
            character = self.hc.id_to_vk[keycode][3:]
        self.tap(keycode, character, press_bool)

    def tap(self, keycode, character, press):
        # print(time.time(), keycode, character, press)
        if self.tapHandler:
            self.tapHandler(keycode, character, press)


class GMouseEvent(PyMouseEvent):
    def __init__(self, clickHandler=None):
        PyMouseEvent.__init__(self)

    def click(self, x, y, button, press):
        print(time.time(), x, y, button, press)


# _keyboard_event_instance = GKeyBoardEvent()
# _mouse_event_instance = GMouseEvent()
#
#
# # ========= function
#
# def StartListen():
#     global _mouse_event_instance
#     global _keyboard_event_instance
#     _mouse_event_instance.start()
#     _keyboard_event_instance.start()
#
#
# def StopListen():
#     global _mouse_event_instance
#     global _keyboard_event_instance
#     _mouse_event_instance.stop()
#     _keyboard_event_instance.stop()


def Click(x, y, button=LEFT_MOUSE, n=1):
    # 在(x, y)用button点击n次
    _mouse.click(x, y, button, n)


def TapKey(key, n=1, interval=0.1):
    # 点击n下key,间隔interval秒
    _keyboard.tap_key(key, n=n, interval=interval)


def PressKey(key):
    # 按住key
    _keyboard.press_key(key)


def ReleaseKey(key):
    # 松开key
    _keyboard.release_key(key)
