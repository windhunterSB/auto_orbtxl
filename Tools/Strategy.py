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


class HistoryData(object):
	def __init__(self):
		self.clean()

	def clean(self):
		self.idx = []
		self._monster_idx = 0
		self.time = []
		self.avatar = []
		self.others = {}  # id: history_list

	def GetNewMonsterID(self):
		self._monster_idx += 1
		return self._monster_idx

	def Update(self, avatarPos, others, catchScreenTime):
		# 注意这里用的时间是截图的时间，而不是识别后的时间。识别由额外的时间开销
		pass


class Strategy(object):

	def __init__(self):
		self.history = HistoryData()
		self.lazy_clear = False

	def _Dist2(self, p1, p2):
		return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

	def Update(self, avatarPos, others, catchScreenTime):
		# 注意这里用的时间是截图的时间，而不是识别后的时间。识别由额外的时间开销
		if not avatarPos:
			self.lazy_clear = True
			return
		if self.lazy_clear:
			self.history.clean()
			self.lazy_clear = False
		# self.history.Update(avatarPos, others, catchScreenTime)
		mapCenter = (160, 120)
		R = math.sqrt(self._Dist2(avatarPos, mapCenter))
		for objPos, objID in others:
			if self._Dist2(objPos, avatarPos) < 1600:
				ROBJ = math.sqrt(self._Dist2(objPos, mapCenter))
				if ROBJ > R:
					print ROBJ, R, avatarPos, objPos, time.time(), 0
					return 0
				else:
					print ROBJ, R, avatarPos, objPos, time.time(), 1
					return 2
		print R, avatarPos, time.time()
		if R > 70:
			return 0
		elif R < 50:
			return 2
		else:
			return 1

