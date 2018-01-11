# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
	kongzhao
	kongzhao135@163.com
Date:
	2018/1/11
Description:

----------------------------------------------------------------------------"""

from Tools import CatchScreen, Event, CollectImages
import time


if __name__ == "__main__":
	print "start"
	#	CatchScreen.CatchScreen("./a.jpg")
	# Event.StartListen()
	#
	# time.sleep(30)
	# print "stop"
	# Event.StopListen()
	# time.sleep(10)
	# print "end"
	CollectImages.Start()
	while True:
		time.time()
