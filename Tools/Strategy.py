# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
	kongzhao
	kongzhao135@163.com
Date:
	2018/1/18
Description:
	策略提供
----------------------------------------------------------------------------"""

import math
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


class Strategy(object):

	def __init__(self):
		self.record = RecordData()
		self.lazy_clear = False

	def _Dist2(self, p1, p2):
		return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

	def Update(self, avatarPos, others, catchScreenTime):
		# 注意这里用的时间是截图的时间，而不是识别后的时间。识别由额外的时间开销
		if not avatarPos:
			self.lazy_clear = True
			return 0
		if self.lazy_clear:
			self.record.clean()
			self.lazy_clear = False

		pwm = 0

		mapCenter = (160, 120)
		R = math.sqrt(self._Dist2(avatarPos, mapCenter))
		for objPos, objID in others:
			pass
		print R, avatarPos, time.time()

		self.record.InsertData(avatarPos, others, catchScreenTime, pwm, time.time())
		return pwm

	def Save(self):
		self.record.Save()