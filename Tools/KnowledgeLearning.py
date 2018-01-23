# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
	kongzhao
	kongzhao135@163.com
Date:
	2018/1/20
Description:

----------------------------------------------------------------------------"""

import math
import time
import pickle

RECORD_PATH = "./GameData/Record/"

class RecordData(object):
	def __init__(self):
		self.Clean()

	def Clean(self):
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

	def Save(self, file="test.dat"):
		if not self.frames:
			return
		with open(RECORD_PATH + file, "wb") as fl:
			pickle.dump(self.frames, fl, True)

	def Load(self, file="test.dat"):
		with open(RECORD_PATH + file, "rb") as fl:
			self.frames = pickle.load(fl)


def Dist(p1, p2):
	return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def Yaw(p, center):
	return math.atan2(p[1] - center[1], p[0] - center[0])


def Analysis(record):
	frames = record.frames

	lastP, lastT, lastA = (0, 0), 0, 0
	for elem in frames:
		avtpos = elem["avtpos"]
		tim = elem["catchT"]
		yaw = Yaw(avtpos, (160, 120))
		speed = 0
		yaw_speed = 0
		if lastT:
			speed = Dist(avtpos, lastP) / (tim - lastT)
			yaw_speed = (yaw - lastA) / (tim - lastT)
		lastP = avtpos
		lastT = tim
		lastA = yaw
		print avtpos, yaw, "\t speed:", speed, yaw_speed


def Test():
	record = RecordData()
	record.Load("g_1516670554.dat")
	Analysis(record)
