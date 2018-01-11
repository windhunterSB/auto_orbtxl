# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
	kongzhao
	kongzhao135@163.com
Date:
	2018/1/11
Description:

----------------------------------------------------------------------------"""

from CatchScreen import CatchScreen
import time
import threading

COLLECT_INTERVAL = 0.1  # 0.5s采集一次
IS_OPEN = False
IS_RUNNING = False


def Collecting():
	global IS_OPEN
	global COLLECT_INTERVAL
	global IS_RUNNING
	IS_RUNNING = True
	while IS_OPEN:
		name = "./ImageData/img_" + str(int(time.time() * 100)) + ".jpg"
		try:
			CatchScreen(name)
		except Exception, ex:
			print ex
			IS_OPEN = False
			break
		time.sleep(COLLECT_INTERVAL)
	IS_RUNNING = False


def Start():
	global IS_OPEN
	if IS_OPEN:
		return
	if IS_RUNNING:
		print "Not stop success, can't start now!"
		return
	IS_OPEN = True
	threading.Thread(target=Collecting, args=()).start()


def Close():
	global IS_OPEN
	IS_OPEN = False
