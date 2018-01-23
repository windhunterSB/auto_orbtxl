# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
	kongzhao
	kongzhao135@163.com
Date:
	2018/1/11
Description:
	# 批量取pixel的方法:(直接img取会调很多次load非常慢)
	imgdata = img.getdata()
	rgb = imgdata.getpixel((x, y))
	
	
----------------------------------------------------------------------------"""
import Image
import time
import os
from Const import *
from MarkData import ReadImageFromFile, LoadModels, GetColorCntIgnore, CalcSimilarScore, RGBIntWithIgnore, RGBTuple, GetMidOfModel
from random import random


LoadModels()

POS_BIT_MOVE = 16
POS_BIT_MOD = (1 << POS_BIT_MOVE) - 1
BLACK_HOLE_RANGE_IN_160_120 = (72, 52, 90, 70)  # 在80*60的压缩图里，黑洞的大致范围
CENTER_IN_160_120 = (80.5, 60.5)

START_GAME_FEATURE_RECTS = ((140, 122, 179, 130), (140, 109, 179, 117), (133, 166, 187, 178))

SET_IN_HOLE_RANGE = set()
for x in xrange(BLACK_HOLE_RANGE_IN_160_120[0], BLACK_HOLE_RANGE_IN_160_120[2]):
	for y in xrange(BLACK_HOLE_RANGE_IN_160_120[1], BLACK_HOLE_RANGE_IN_160_120[3]):
		if (x - CENTER_IN_160_120[0]) ** 2 + (y - CENTER_IN_160_120[1]) ** 2 <= 81:  # 100 = 10 * 10
			SET_IN_HOLE_RANGE.add((x << POS_BIT_MOVE) | y)

FeatureColor = {}
for idx, fs in enumerate(MARK_FEATURE_COLOR):
	FeatureColor[idx] = set()
	for elem in fs:
		FeatureColor[idx].add(elem[0])


def DebugDraw(img, rect, color=(255, 0, 0)):
	for i in xrange(rect[0], rect[2] + 1):
		img.putpixel((i, rect[1]), color)
		img.putpixel((i, rect[3]), color)
	for i in xrange(rect[1], rect[3] + 1):
		img.putpixel((rect[0], i), color)
		img.putpixel((rect[2], i), color)


class ColorCnt(object):
	rare_prob = 0.002

	def __init__(self, image, image_small=None):
		if image.size == (320, 240):
			image_small = image.resize((image.size[0] / 2, image.size[1] / 2))
			self.small_image = ColorCnt(image_small)
		else:
			self.small_image =None

		self.size = image.size
		self.image_data = image.load()

		x_size, y_size = self.size
		image_data = self.image_data

		self.color_cnt = {}  # 随机采样来提取
		random_num = 1000
		while random_num > 0:
			random_num -= 1
			rgb = RGBIntWithIgnore(image_data[int(random() * x_size), int(random() * y_size)])
			if rgb in self.color_cnt:
				self.color_cnt[rgb] += 1
			else:
				self.color_cnt[rgb] = 1

		self.sortedCnt = sorted([(v, k) for k, v in self.color_cnt.iteritems()])
		# top5大概率是背景
		self.top5 = set()
		for i in xrange(5):
			self.top5.add(self.sortedCnt[-i - 1][1])

	def FastFindObjPoints(self):
		# 快速找到可疑点（只在小图中使用）
		global _Average_Image
		if self.small_image:
			raise Exception("only use for small image!")
		points = []
		x_size, y_size = self.size
		image_data = self.image_data
		for x in xrange(x_size):
			for y in xrange(y_size):
				rgb = RGBIntWithIgnore(image_data[x, y])
				pos = (x << POS_BIT_MOVE) | y
				if pos in SET_IN_HOLE_RANGE or rgb in self.top5:  # 直接过滤掉中间的 和 背景的 以及边缘的
					continue
				for fi, fs in FeatureColor.iteritems():
					if rgb in fs:
						points.append((x, y, fi))
		# print "fast point num:", len(points)
		return points

	def FastFindObjects(self):
		# 使用一些简单策略，快速过滤出潜在的被背景点，然后将它们合并成obj
		# 在小图中快速查找
		if not self.small_image:
			raise Exception("only use for origin image!")

		s_points = self.small_image.FastFindObjPoints()
		# print s_points

		# 简单过滤
		x_size, y_size = self.size
		x_scale = self.size[0] / self.small_image.size[0]
		y_scale = self.size[1] / self.small_image.size[1]

		image_data = self.image_data

		vst = set()
		self.objects = []
		check_num = 0
		for s_x, s_y, s_fid in s_points:
			x = s_x * x_scale
			y = s_y * y_scale
			pos = (x << POS_BIT_MOVE) | y
			if pos in vst:
				continue
			check_num += 1
			f_d = MARK_DIAMETER[s_fid]
			x_min = max(0, x - f_d + 1)
			x_max = min(x + f_d, x_size - 1)
			y_min = max(0, y - f_d + 1)
			y_max = min(y + f_d, y_size - 1)

			# 预处理,加速一下
			color_sum = {}

			for xx in xrange(x_min, x_max + 1):
				for yy in xrange(y_min, y_max + 1):
					color = RGBIntWithIgnore(image_data[xx, yy])
					pp = (xx << POS_BIT_MOVE) | yy
					color_sum[pp] = {}
					for c in FeatureColor[s_fid]:
						color_sum[pp][c] = 0 if color != c else 1
						if xx > x_min:
							color_sum[pp][c] += color_sum[((xx - 1) << POS_BIT_MOVE) | yy][c]
						if yy > y_min:
							color_sum[pp][c] += color_sum[(xx << POS_BIT_MOVE) | yy - 1][c]
						if xx > x_min and yy > y_min:
							color_sum[pp][c] -= color_sum[((xx - 1) << POS_BIT_MOVE) | yy - 1][c]

			best_score = 1.1  # 1.0 mean must impossible
			best_xy = None
			tmp_color = {}
			for xx in xrange(x_min, x_max + 1 - f_d):
				for yy in xrange(y_min, y_max + 1 - f_d):
					for c in FeatureColor[s_fid]:
						tmp_color[c] = color_sum[((xx + f_d - 1) << POS_BIT_MOVE) | yy + f_d - 1][c]
						if xx > x_min:
							tmp_color[c] -= color_sum[((xx - 1) << POS_BIT_MOVE) | yy][c]
						if yy > y_min:
							tmp_color[c] -= color_sum[(xx << POS_BIT_MOVE) | yy - 1][c]
						if xx > x_min and yy > y_min:
							tmp_color[c] += color_sum[((xx - 1) << POS_BIT_MOVE) | yy - 1][c]
					score = CalcSimilarScore(s_fid, tmp_color)
					if score < best_score:
						best_score = score
						best_xy = (xx, yy)
					# print score, (xx, yy), tmp_color, MARK_FEATURE_COLOR[s_fid]
			if best_score < GetMidOfModel(s_fid):
				# print best_score, best_xy, (x_min, y_min), (x_max, y_max)
				xx, yy = best_xy
				self.objects.append((xx, yy, xx + f_d, yy + f_d, s_fid))
				for _x in xrange(x_min, x_max + 1):
					for _y in xrange(y_min, y_max + 1):
						vst.add((_x << POS_BIT_MOVE) | _y)
			else:
				x_min = max(0, x - f_d / 2 + 1)
				x_max = min(x + f_d / 2, x_size)
				y_min = max(0, y - f_d / 2 + 1)
				y_max = min(y + f_d / 2, y_size)
				for _x in xrange(x_min, x_max):
					for _y in xrange(y_min, y_max):
						vst.add((_x << POS_BIT_MOVE) | _y)
				# print "fid:", s_fid

		# print check_num, len(self.objects)
		return self.objects


def FindObjs(image):
	# 提取图片中的
	colorObj = ColorCnt(image)
	objs = colorObj.FastFindObjects()
	avatar = None
	others = []
	for obj in objs:
		center = 0.5 * (obj[2] - 1 + obj[0]), 0.5 * (obj[3] - 1 + obj[1])
		if obj[4] == AVATAR_ID:
			avatar = center
		else:
			others.append((center, obj[4]))
	return avatar, others


def IsInGame(image):
	# 通过像素分布验证是不是在游戏的准备画面上（即游戏有没开始）
	pix = image.load()
	for elem in START_GAME_FEATURE_RECTS:
		s = 0
		cnt = 0
		for x in xrange(elem[0] + 1, elem[2]):
			for y in xrange(elem[1] + 1, elem[3]):
				r, g, b = pix[x, y]
				if r == 255 and g == 255 and b == 255:
					cnt += 1
				s += 1
		# print cnt, s, 1.0 * cnt / s
		if cnt < s * 3 / 5:
			return True
	return False


# ============ other function ===========

# def Load1(img):
# 	# 0.0023
# 	pix = img.load()
# 	width = img.size[0]
# 	height = img.size[1]
# 	for x in range(width):
# 		for y in range(height):
# 			r, g, b = pix[x, y]
#
# def Load2(img):
# 	# 0.0034
# 	pix = img.getdata()
# 	width = img.size[0]
# 	height = img.size[1]
# 	for x in range(width):
# 		for y in range(height):
# 			r, g, b = pix.getpixel((x, y))


def TestOneImage(img, file, debug=False):
	colorObj = ColorCnt(img)

	objs = colorObj.FastFindObjects()
	# print "objs num:", len(objs)

	new_img = Image.new('RGB', (img.size[0], img.size[1] * 2), 255)
	new_img.paste(img, (0, 0))
	new_img.paste(img, (0, img.size[1]))

	# print len(objs)
	for elem in objs:
		# print elem
		DebugDraw(new_img, (elem[0], elem[1], elem[2] - 1, elem[3] - 1), RGBTuple(MARK_ID_COLORS[elem[4]]))

	new_img.save("./Test/OutPut/" + file)
	new_img.crop((0, 0, img.size[0], img.size[1])).save("./Test/Draw/" + file)


def Test():
	path = "./ImageData/"
	read_use = 0
	st = time.time()
	num = 0

	for root, dirs, files in os.walk(path):
		for file in files:
			if file.find(".bmp") == -1:
				continue
			num += 1
			read_use -= time.time()
			img = ReadImageFromFile(path + "/" + file)
			read_use += time.time()
			TestOneImage(img, file)
			if num > 100:
				break
			# break
	ed = time.time()
	print "use time:", ed - st - read_use, "s", "each use:", (ed - st - read_use) / num, "s", "read total use:", read_use, "s"


def TestGameStartImage():
	path = "./ImageData/end_image.bmp"
	img = ReadImageFromFile(path)
	st = time.time()

	IsInGame(img)

	ed = time.time()
	print "use time:", ed - st, "s"

	new_img = Image.new('RGB', (img.size[0], img.size[1] * 2), 255)
	new_img.paste(img, (0, 0))
	new_img.paste(img, (0, img.size[1]))

	DebugDraw(new_img, (133, 166, 187, 178), (255, 0, 0))
	DebugDraw(new_img, (140, 122, 179, 130), (255, 0, 0))
	DebugDraw(new_img, (140, 109, 179, 117), (255, 0, 0))

	new_img.save("./Test/OutPut/end_image.bmp")
