# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
	kongzhao
	kongzhao135@163.com
Date:
	2018/1/11
Description:

----------------------------------------------------------------------------"""

from Tools import CatchScreen, Event, CollectImages, Recognize, MarkData, Player, KnowledgeLearning
import time


def CollectLoop():
	CollectImages.Start()
	raw_input()
	print "stop loop"
	CollectImages.Close()


def LearnAndPlay():
	pass


if __name__ == "__main__":
	print "start"
	# CollectLoop()  # do collect images
	# MarkData.Test()
	# Recognize.Test()
	# Recognize.TestGameStartImage()
	# Player.Test()
	KnowledgeLearning.Test()
