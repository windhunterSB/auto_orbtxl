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
from MarkData import ReadImageFromFile, LoadModels, GetColorCntIgnore, CalcSimilarScore, RGBWithIgnore


POS_BIT_MOVE = 16
BLACK_HOLE_RANGE_IN_80_60 = (36, 26, 45, 35)  # 在80*60的压缩图里，黑洞的大致范围
CENTER_IN_80_60 = (40, 30)  # 宇宙的中心
CENTER_IN_160_120 = (80.5, 60.5)

SET_IN_HOLE_RANGE = set()
for x in xrange(BLACK_HOLE_RANGE_IN_80_60[0], BLACK_HOLE_RANGE_IN_80_60[2]):
	for y in xrange(BLACK_HOLE_RANGE_IN_80_60[1], BLACK_HOLE_RANGE_IN_80_60[3]):
		SET_IN_HOLE_RANGE.add((x << POS_BIT_MOVE) | y)


def DebugDraw(img, rect, color=(255, 0, 0)):
	for i in xrange(rect[0], rect[2] + 1):
		img.putpixel((i, rect[1]), color)
		img.putpixel((i, rect[3]), color)
	for i in xrange(rect[1], rect[3] + 1):
		img.putpixel((rect[0], i), color)
		img.putpixel((rect[2], i), color)


class ColorCnt(object):
	pos_bit_move = POS_BIT_MOVE  # xy = (x << pos_bit_move) | y
	pos_bit_mod = (1 << pos_bit_move) - 1
	rare_prob = 0.002
	ro = 0.2  # objects 的密度

	def __init__(self, image, image_small=None):
		if image_small:
			self.small_image = ColorCnt(image_small)
		else:
			self.small_image =None

		self.size = image.size
		x_size, y_size = self.size
		move = self.pos_bit_move

		image_data = image.load()

		self.color_cnt = {}
		self.pos_rgb = {}
		for x in xrange(x_size):
			for y in xrange(y_size):
				rgb = RGBWithIgnore(image_data[x, y])
				if rgb in self.color_cnt:
					self.color_cnt[rgb] += 1
				else:
					self.color_cnt[rgb] = 1
				self.pos_rgb[(x << move) | y] = rgb
		self.sortedCnt = sorted([(v, k) for k, v in self.color_cnt.iteritems()])
		# top6 大概率是背景
		self.top6 = set()
		for i in xrange(6):
			self.top6.add(self.sortedCnt[-i - 1][1])

	def FastFindObjPoints(self):
		# 快速找到可疑点（只在小图中使用）
		global _Average_Image
		if self.small_image:
			raise Exception("only use for small image!")
		points = []
		for pos, rgb in self.pos_rgb.iteritems():
			if pos in SET_IN_HOLE_RANGE or rgb in self.top6 or (pos & 255) == 0:  # 直接过滤掉中间的 和 背景的 以及边缘的
				continue
			for fi in xrange(len(FeatureColor)):
				if self._IsFeature(rgb, fi):
					points.append((pos, fi))
					break
		print "fast points:"
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

		bit_move = self.pos_bit_move
		bit_mod = self.pos_bit_mod

		vst = set()
		self.objects = []
		for s_point, s_fid in s_points:
			x = (s_point >> bit_move) * x_scale
			y = (s_point & bit_mod) * y_scale
			pos = (x << bit_move) | y
			if pos in vst:
				continue
			f_size = MARK_DIAMETER[s_fid]
			x_min = max(0, x - f_size[0] + 1)
			x_max = min(x + f_size[0], x_size - 1)
			y_min = max(0, y - f_size[1] + 1)
			y_max = min(y + f_size[1], y_size - 1)

			best_dist = 100000000
			best_xy = None
			for xx in xrange(x_min, x_max + 1 - f_size[0]):
				for yy in xrange(y_min, y_max + 1 - f_size[1]):
					diff = 0
					for xxx in xrange(xx, xx + f_size[0]):
						for yyy in xrange(yy, yy + f_size[1]):
							pass

		return self.objects

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


def TestOneImage(path, file, debug=False):
	img = ReadImageFromFile(path + "/" + file)
	img_small = img.resize((img.size[0] / 2, img.size[1] / 2))

	img_data = img.getdata()
	img_small_data = img_small.getdata()

	colorObj = ColorCnt(img_data, img_small_data)

	# print len(colorObj.sortedCnt)
	# for v, k in colorObj.sortedCnt:
	# 	if v <= 40:
	# 		continue
	# 	print k >> 16, k>>8 & 255, k & 255, ":", v

	objs = colorObj.FastFindObjects()

	new_img = Image.new('RGB', (img.size[0], img.size[1] * 2), 255)
	new_img.paste(img, (0, 0))
	new_img.paste(img, (0, img.size[1]))

	# print len(objs)
	for elem in objs:
		# print elem
		DebugDraw(new_img, (elem[0], elem[1], elem[2] - 1, elem[3] - 1), (255, 0, 0))

	new_img.save("./Objects/Test/OutPut/" + file)


def Test():
	path = "./ImageData/"

	st = time.time()
	num = 0

	for root, dirs, files in os.walk(path):
		for file in files:
			if file.find(".bmp") == -1:
				continue
			num += 1
			TestOneImage(path, file)
			break
	ed = time.time()
	print "use time:", ed - st, "s", "each use:", (ed - st) / num, "s"

