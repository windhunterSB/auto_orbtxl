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

	lastP, lastT, lastA, lastR = [], [], [], []
	for elem in frames:
		avtpos = elem["avtpos"]
		tim = elem["catchT"]
		yaw = Yaw(avtpos, (160, 121))
		speed = 0
		yaw_speed = 0
		r_speed = 0
		a_speed = 0
		dt = 0
		r = Dist(avtpos, (160, 121))
		step = 1
		if len(lastT) >= step:
			dt = (tim - lastT[-step])
			speed = Dist(avtpos, lastP[-step]) / (tim - lastT[-step])
			yaw_speed = (yaw - lastA[-step]) / (tim - lastT[-step])
			r_speed = (r - lastR[-step]) / (tim - lastT[-step])
			a_speed = math.sqrt(speed ** 2 - r_speed ** 2)
		lastP.append(avtpos)
		lastT.append(tim)
		lastA.append(yaw)
		lastR.append(r)
		print avtpos, "\t%6.3f" % yaw, " %6.2f" % r, "\t speed: %8.4f" % speed, "  %6.3f %7.3f   %7.3f\t " % (yaw_speed, r_speed, a_speed), dt, elem["action"]


def Test():
	record = RecordData()
	record.Load("g_1516704746.dat")
	Analysis(record)
