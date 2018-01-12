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

AvatarSize = (5, 5)
BulletSizeSet = [(4, 4), (5, 5), (7, 7)]

AvatarFeatureColor = [(143, 210, 118), (30, 169, 220)]
BulletFeatureColor = [
	[],
	[],
	[],
]


_FeatureColorCache = {}


def DebugDraw(img, rect, color=(255, 0, 0)):
	for i in xrange(rect[0], rect[2]):
		img.putpixel((i, rect[1]), color)
		img.putpixel((i, rect[3] - 1), color)
	for i in xrange(rect[1], rect[3]):
		img.putpixel((rect[0], i), color)
		img.putpixel((rect[2] - 1, i), color)


class ColorCnt(object):
	window_size = (2, 2)
	step = (1, 1)
	link = [(-step[0], 0), (step[0], 0), (0, step[0]), (0, -step[0])]
	max_dist2 = 50
	rare_prob = 0.002
	ro = 0.2  # objects 的密度

	def __init__(self, image_data, image_size):
		self.size = image_size
		x_size, y_size = image_size
		self.cnt = {}
		self.pos_rgb = {}
		self.pos_pixel = {}
		for x in xrange(x_size):
			for y in xrange(y_size):
				pixel = image_data.getpixel((x, y))
				rgb = (((pixel[0] << 8) | pixel[1]) << 8) | pixel[2]
				if rgb in self.cnt:
					self.cnt[rgb] += 1
				else:
					self.cnt[rgb] = 1
				self.pos_rgb[x * y_size + y] = rgb
				self.pos_pixel[x * y_size + y] = pixel
		self.sortedCnt = sorted([(v, k) for k, v in self.cnt.iteritems()])
		# top6 大概率是背景
		self.top6 = set()
		for i in xrange(6):
			self.top6.add(self.sortedCnt[-i - 1][1])

	def _Dist(self, pa, pb):
		return abs(pa[0] - pb[0]) + abs(pa[1] - pb[1]) + abs(pa[2] - pb[2])

	def _IsFeaColor(self, pixel):
		if

	def _MergeObjects(self, objs):
		x_r = [100000, -100000]
		y_r = [100000, -100000]
		x_size, y_size =  self.size
		for obj in objs:
			x = obj // y_size
			y = obj % y_size
			x_r[0] = min(x_r[0], x)
			x_r[1] = max(x_r[1], x)
			y_r[0] = min(y_r[0], y)
			y_r[1] = max(y_r[1], y)

		return (x_r[0], y_r[0],
		        x_r[1] + self.window_size[0],
		        y_r[1] + self.window_size[1])

	def FastFindObjects(self, box=None):
		# 使用一些简单策略，快速过滤出潜在的被背景点，然后将它们合并成obj
		# 简单过滤
		x_size, y_size =  self.size

		window_size = self.window_size
		step = self.step
		if box == None:
			box = (0, 0, x_size, y_size)
		check_num = window_size[0] * window_size[1]
		full_num = x_size * y_size

		yu = check_num / 2
		objs = {}

		for x in xrange(box[0], box[2] - window_size[0] + 1, step[0]):
			for y in xrange(box[1], box[3] - window_size[1] + 1, step[1]):
				sp_cnt = 0
				bg_cnt = 0
				for xx in xrange(x, x + window_size[0]):
					for yy in xrange(y, y + window_size[1]):
						rgb = self.pos_rgb[xx * y_size + yy]
						if self.cnt[rgb] < full_num * self.rare_prob:  # 不超过0.002概率出现的点
							sp_cnt += 1
						if rgb in self.top6:
							bg_cnt += 1
				# fast check
				if bg_cnt >= yu or sp_cnt <= yu:
					continue
				fea_cnt = 0
				box_type = 0
				for xx in xrange(x, x + window_size[0]):
					for yy in xrange(y, y + window_size[1]):
						pos = xx * y_size + yy
						if self.pos_rgb[pos] in _FeatureColorCache:
							fea_cnt += _FeatureColorCache[self.pos_rgb[pos]][0]
						else:
							fea_cnt += self._IsFeaColor(self.pos_pixel[pos])
				if fea_cnt >= yu:
					objs[x * y_size + y] = box_type

		self.objects = []
		# 窗口合并
		vst = set()
		link = self.link
		for elem in objs:
			if elem in vst:
				continue
			que = [elem]
			head = 0
			while head < len(que):
				e, head = que[head], head + 1
				x = e // y_size
				y = e % y_size
				pixel = objs[e]
				for d in link:
					p = (x + d[0]) * y_size + y + d[1]

					if p in objs and p not in que:#  and self._Dist(objs[p], pixel) < self.max_dist2 :
						que.append(p)
					# elif p in objs:
					# 	print "dis", self._Dist(objs[p], pixel)
			if len(que) >= 1:
				self.objects.append(self._MergeObjects(que))
				vst.update(que)
				print que

		return self.objects

	def FindAvatarInImage(image):

		pass


	def FindBulletsInImage(image):
		pass


def SaveCrop(img, left, right, top, bottom, file):
	part = img.crop((left, top,right, bottom))
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


def TestOneImage(path, file, debug=False):
	img = ReadImageFromFile(path + "/" + file)

	img_data = img.getdata()
	img_size = img.size

	colorObj = ColorCnt(img_data, img_size)

	# print len(colorObj.sortedCnt)
	# for v, k in colorObj.sortedCnt:
	# 	if v <= 40:
	# 		continue
	# 	print k >> 16, k>>8 & 255, k & 255, ":", v

	objs = colorObj.FastFindObjects()

	new_img = Image.new('RGB', (img_size[0], img_size[1] * 2), 255)
	new_img.paste(img, (0, 0))
	new_img.paste(img, (0, img_size[1]))

	# print len(objs)
	for elem in objs:
		DebugDraw(new_img, (elem[0], elem[1], elem[2] - 1, elem[3] - 1))

	new_img.save("./Objects/Test/" + file)


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
