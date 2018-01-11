# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
	kongzhao
	kongzhao135@163.com
Date:
	2018/1/11
Description:

----------------------------------------------------------------------------"""
import ctypes
from PIL import ImageGrab
from win32gui import EnumWindows, IsWindow, GetWindowText


HWND_NAME_KEY_WORD = "G68Robot"
HWND_TOP = 0
SWP_NOMOVE= 2
SWP_NOSIZE= 1
SWP_SHOWWINDOW= 64
_HWND = None


class RECT(ctypes.Structure):
	_fields_ = [('left', ctypes.c_long),
	            ('top', ctypes.c_long),
	            ('right', ctypes.c_long),
	            ('bottom', ctypes.c_long)]
	def __str__(self):
		return str((self.left, self.top, self.right, self.bottom))


def _Checker(hwnd, mouse):
	global _HWND
	if IsWindow(hwnd) and GetWindowText(hwnd).find(HWND_NAME_KEY_WORD) > -1:
		_HWND = hwnd


def GetHwnd():
	global _HWND
	if not _HWND:
		EnumWindows(_Checker, 0)
	return _HWND


def CatchScreen(save_file=""):
	hwnd = GetHwnd()
	if not hwnd:
		print "Can't find Game Screen!"
		return None
	# 置顶好像没用的样子
	# ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
	rect = RECT()
	ctypes.windll.user32.GetWindowRect(hwnd,ctypes.byref(rect))
	rangle = (rect.left, rect.top, rect.right, rect.bottom)
	image = ImageGrab.grab(rangle)
	if save_file:
		image.save(save_file)
	return image
