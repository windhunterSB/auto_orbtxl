# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
	kongzhao
	kongzhao135@163.com
Date:
	2018/1/20
Description:

----------------------------------------------------------------------------"""

import time
import pickle

RECORD_PATH = "./GameData/Record/"

class RecordData(object):
	def __init__(self):
		self.clean()

	def clean(self):
		self.frames = []  # 记录过程的每一帧的实际数据

	def InsertData(self, avatarPos, others, catchScreenTime, action, actionTime):
		# 注意这里用的时间是截图的时间，而不是识别后的时间。识别由额外的时间开销
		frame = {
			"avtpos": avatarPos,
			"others": others,
			"catchT": catchScreenTime,
			"action": action,
			"actionT": actionTime,
		}
		self.frames.append(frame)

	def Save(self):
		with open(RECORD_PATH + "test.dat", "wb") as fl:
			pickle.dump(self.frames, fl, True)

	def Load(self):
		with open(RECORD_PATH + "test.dat", "rb") as fl:
			self.frames = pickle.load(fl)


def Analysis():
	pass
