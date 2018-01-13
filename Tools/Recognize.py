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
import Const

POS_BIT_MOVE = 16
BLACK_HOLE_RANGE_IN_80_60 = (36, 26, 45, 35)  # 在80*60的压缩图里，黑洞的大致范围
CENTER_IN_80_60 = (40, 30)  # 宇宙的中心
CENTER_IN_160_120 = (80.5, 60.5)

SET_IN_HOLE_RANGE = set()
for x in xrange(BLACK_HOLE_RANGE_IN_80_60[0], BLACK_HOLE_RANGE_IN_80_60[2]):
	for y in xrange(BLACK_HOLE_RANGE_IN_80_60[1], BLACK_HOLE_RANGE_IN_80_60[3]):
		SET_IN_HOLE_RANGE.add((x << POS_BIT_MOVE) | y)

AVATAR_ID = 0
FeatureColor = [
	[0x1EA9DC, 0x7AB264, 0x8FD077], # 地球，avatar
	[0xFF4644, 0xA22829, 0x933144, 0xD93C3A, 0xFFB1B2],  # 红色的那个星星
	[0xC3640D, 0x723C07, 0x864608, 0x512F33],  # 土黄的那个
	[0xFF8210, 0x8101A5, 0xBD04EF],  # 紫色那个
	[0x898989, 0xB5B6B5, 0x585858, 0x686478],  # 灰色那个
]
FeatireSize = [
	(4, 4),
	(3, 3),
	(4, 4),
	(5, 5),
	(2, 2),
]

_FeatureColorCache = {k: {} for k in xrange(len(FeatureColor))}

_Average_Image = None


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
	fea_max_dist = 40
	rare_prob = 0.002
	ro = 0.2  # objects 的密度

	def __init__(self, image_data, image_small_data=None):
		if image_small_data:
			self.small_image = ColorCnt(image_small_data)
		else:
			self.small_image =None

		self.size = image_data.size
		x_size, y_size = self.size
		move = self.pos_bit_move

		self.color_cnt = {}
		self.pos_rgb = {}
		# self.pos_pixel = {}
		for x in xrange(x_size):
			for y in xrange(y_size):
				pixel = image_data.getpixel((x, y))
				rgb = (((pixel[0] << 8) | pixel[1]) << 8) | pixel[2]
				if rgb in self.color_cnt:
					self.color_cnt[rgb] += 1
				else:
					self.color_cnt[rgb] = 1
				self.pos_rgb[(x << move) | y] = rgb
				# self.pos_pixel[(x << move) | y] = pixel
		self.sortedCnt = sorted([(v, k) for k, v in self.color_cnt.iteritems()])
		# top6 大概率是背景
		self.top6 = set()
		for i in xrange(6):
			self.top6.add(self.sortedCnt[-i - 1][1])

	def _IsFeature(self, rgb, f_id):
		return self._FeatureDist(rgb, f_id) < self.fea_max_dist

	def _FeatureDist(self, rgb, f_id):
		global _FeatureColorCache
		if rgb in _FeatureColorCache[f_id]:
			return _FeatureColorCache[f_id][rgb]
		dist = 100000000
		for f in FeatureColor[f_id]:
			dist = min(self._Dist(rgb, f), dist)
		_FeatureColorCache[f_id][rgb] = dist
		return dist

	def _Dist(self, rgb_a, rgb_b):
		return abs((rgb_a >> 16) - (rgb_b >> 16)) + abs(((rgb_a >> 8) & 255) - ((rgb_b >> 8) & 255)) + abs((rgb_a & 255) - (rgb_b & 255))

	# def _CatchBox(self, box, pos_set):
	# 	# print box, pos_set
	# 	x_min, y_min, x_max, y_max = box
	# 	move = self.pos_bit_move
	# 	ok = True
	# 	while ok:
	# 		ok = False
	# 		if y_min < y_max:
	# 			min_num = 0
	# 			max_num = 0
	# 			for x in xrange(x_min, x_max + 1):
	# 				min_num += ((x << move) | y_min) in pos_set
	# 				max_num += ((x << move) | y_max) in pos_set
	# 			if min_num < max(3, (x_max - x_min + 1) / 2):
	# 				y_min += 1
	# 				ok = True
	# 			if max_num < max(3, (x_max - x_min + 1) / 2):
	# 				y_max -= 1
	# 				ok = True
	# 		if x_min < x_max:
	# 			min_num = 0
	# 			max_num = 0
	# 			for y in xrange(y_min, y_max + 1):
	# 				min_num += ((x_min << move) | y) in pos_set
	# 				max_num += ((x_max << move) | y) in pos_set
	# 			if min_num < max(3, (y_max - y_min + 1) / 2):
	# 				x_min += 1
	# 				ok = True
	# 			if max_num < max(3, (y_max - y_min + 1) / 2):
	# 				x_max -= 1
	# 				ok = True
	#
	# 	return x_min, y_min, x_max, y_max

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
		return points


	def FastFindObjects(self):
		# 使用一些简单策略，快速过滤出潜在的被背景点，然后将它们合并成obj
		# 在小图中快速查找
		if not self.small_image:
			raise Exception("only use for origin image!")

		s_points = self.small_image.FastFindObjPoints()
		# print s_points

		# 简单过滤
		x_size, y_size =  self.size
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
			f_size = FeatireSize[s_fid]
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
							diff += self._FeatureDist(self.pos_rgb[(xxx << bit_move) | yyy], s_fid)
					if diff < best_dist:
						best_dist = diff
						best_xy = xx, yy
			max_err = f_size[0] * f_size[1] * self.fea_max_dist * 0.8
			if 1.0 * best_dist < max_err:
				self.objects.append((best_xy[0], best_xy[1], best_xy[0] + f_size[0], best_xy[1] + f_size[1], s_fid))
				for xxx in xrange(best_xy[0], best_xy[0] + f_size[0]):
						for yyy in xrange(best_xy[1], best_xy[1] + f_size[1]):
							vst.add((xxx << bit_move) | yyy)

		return self.objects


def SaveCrop(img, left, right, top, bottom, file):
	part = img.crop((left, top, right, bottom))
	part.save(file)


# ===========  fast function  ============

def FastFindAvatarInImage(image, lastPosition, lastTime):
	# 利用上一次的计算结果快速查找（因为位移不会特别大）
	pass


def FastFindBulletsInImage(image, lastPositions, lastTime):
	# 利用上一次的计算结果快速查找（因为位移不会特别大）
	pass

# ============ other function ===========

def ReadImageFromFile(file):
	return Image.open(file)

def CreateAverageImage(path):
	# 制作一张平均图(用来作为背景色，这样可以过滤出一些非法数据)
	size = None
	ave_image = None
	num = 0
	for root, dirs, files in os.walk(path):
		for file in files:
			if file.find(".bmp") == -1:
				continue
			img = ReadImageFromFile(path + "/" + file)
			if not size:
				size = img.size
				ave_image = [[[0, 0, 0] for i in xrange(size[1])] for j in xrange(size[0])]
			num += 1
			img_data = img.getdata()
			for x in xrange(size[0]):
				for y in xrange(size[1]):
					pix = img_data.getpixel((x, y))
					e = ave_image[x][y]
					e[0] += pix[0]
					e[1] += pix[1]
					e[2] += pix[2]
	new_image = Image.new("RGB", size)
	for x in xrange(size[0]):
		for y in xrange(size[1]):
			e = ave_image[x][y]
			new_image.putpixel((x, y), (e[0]/num, e[1]/num, e[2]/num))
	new_image.save(Const.AVE_IMAGE)


def _LoadAverageImage():
	global _Average_Image
	img = ReadImageFromFile(Const.AVE_IMAGE)
	img_small = img.resize((img.size[0] / 2, img.size[1] / 2))
	img_data = img.getdata()
	img_small_data = img_small.getdata()
	_Average_Image = ColorCnt(img_data, img_small_data)


def Init():
	_LoadAverageImage()


def Load1(img):
	# 0.0023
	pix = img.load()
	width = img.size[0]
	height = img.size[1]
	for x in range(width):
		for y in range(height):
			r, g, b = pix[x, y]

def Load2(img):
	# 0.0034
	pix = img.getdata()
	width = img.size[0]
	height = img.size[1]
	for x in range(width):
		for y in range(height):
			r, g, b = pix.getpixel((x, y))


def TestOneImage(path, file, debug=False):
	img = ReadImageFromFile(path + "/" + file)
	img_small = img.resize((img.size[0] / 2, img.size[1] / 2))
	# img_small = img_small.crop()
	# new_img = Image.new('RGB', (img.size[0] * 4, img.size[1] * 4 * 2), 255)
	# new_img.paste(img_small.resize((img.size[0] * 4, img.size[1] * 4)), (0, 0))
	# new_img.paste(img.resize((img.size[0] * 4, img.size[1] * 4)), (0, img.size[1] * 4))
	# new_img.save("./Objects/Test/Small/" + file)


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
		DebugDraw(new_img, (elem[0], elem[1], elem[2] - 1, elem[3] - 1), (255, 0, 0) if elem[4] != AVATAR_ID else (255, 242, 0))

	new_img.save("./Objects/Test/OutPut/" + file)


def Test():
	path = "./ImageData/"
	# CreateAverageImage(path)
	# return

	st = time.time()
	num = 0
	# TestOneImage(path, "img_151573343900.bmp")

	for root, dirs, files in os.walk(path):
		for file in files:
			if file.find(".bmp") == -1:
				continue
			num += 1
			TestOneImage(path, file)
			# img = ReadImageFromFile(path + "/" + file)
			# for i in xrange(1000):
			# 	Load1(img)
			# 	# Load2(img)
			break
	ed = time.time()
	print "use time:", ed - st, "s", "each use:", (ed - st) / num, "s"

	# img = ReadImageFromFile(path + "/" + "img_151573227110.bmp")
	# print img.size
	# img = img.resize((img.size[0] / 4, img.size[1] / 4))
	# img.save("./Objects/Test/a.bmp")


# ======= 一些加载项
Init()
