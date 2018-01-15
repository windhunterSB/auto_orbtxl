# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    kongzhao
    kongzhao135@163.com
Date:
    2018-01-14
Description:

----------------------------------------------------------------------------"""

import os
import random
import Const
from Recognize import ReadImageFromFile

# =======  制作训练数据  =====================

def RGBInt(rbg_tuple):
	return (rbg_tuple[0] << 16) | (rbg_tuple[1] << 8) | rbg_tuple[2]

def RGBTuple(rgb_int):
	return (rgb_int >> 16, (rgb_int >> 8) & 255, rgb_int & 255)

def CatchSmallImageForObjects(img, pic_name):
	# 从大图中把样本抠出来
	x_size, y_size = img.size
	data = img.load()
	vst = set()
	for x in xrange(x_size):
		for y in xrange(y_size):
			if (x<<16) | y in vst:
				continue
			rgb = RGBInt(data[x, y])
			if rgb in Const.MARK_COLORS:
				name = Const.MARK_NAME[Const.MARK_COLORS[rgb]]
				ex, ey = x_size, y_size
				for xx in xrange(x, x_size):
					if RGBInt(data[xx, y]) != rgb:
						ex = xx
						break
				for yy in xrange(y, y_size):
					if RGBInt(data[x, yy]) != rgb:
						ey = yy
						break
				img.crop((x+1, y+1, ex-1, ey-1)).save("%s/%s/%s_%s_%s.bmp" % (Const.MARK_IMAGE_PATH, name,pic_name, x, y))
				for xx in xrange(x, ex):
					for yy in xrange(y, ey):
						vst.add((xx<<16)|yy)

	# 随机生成20个other系列12x12大小,用于训练
	num = 20
	while num > 0:
		x, y = random.randint(0, x_size - 13), random.randint(0, x_size - 13)
		ex, ey = x + 12, y + 12
		bad = False
		for xx in xrange(x, ex):
			for yy in xrange(y, ey):
				if (xx << 16) | yy in vst:
					bad = True
		if not bad:
			img.crop((x, y, ex, ey)).save("%s/%s/%s_%s_%s.bmp" % (Const.MARK_IMAGE_PATH, "Other", pic_name, x, y))
			num -= 1


def CatchAllObjects():
	# 批处理抠图(抠出来存盘)
	for root, dirs, files in os.walk(Const.MARK_IMAGE_ORIGIN_PATH):
		for file in files:
			if file.find(".bmp") == -1:
				continue
			img = ReadImageFromFile(os.path.join(Const.MARK_IMAGE_ORIGIN_PATH, file))
			CatchSmallImageForObjects(img, file[0:-4])


def CreateFeatureList(objID, color_cnt):
	pass
	# for color in color_cnt.iteritems():



def CalcSimilarScore(objID, color_cnt):
	# 特征计算, color_cnt = { rgb_int: num }
	pass

# ============  特征测试 =========

def CalcFeatureForObject(objID):
	name = Const.MARK_NAME[objID]
	imgs = []
	for root, dirs, files in os.walk(os.path.join(Const.MARK_IMAGE_PATH, name)):
		for file in files:
			if file.find(".bmp") == -1:
				continue
			img = ReadImageFromFile(os.path.join(Const.MARK_IMAGE_PATH, name, file))
			imgs.append(img)
	d_set = {}
	color_set = {}
	for img in imgs:
		d_set[img.size[0]] = d_set.get(img.size[0], 0) + 1
		d_set[img.size[1]] = d_set.get(img.size[1], 0) + 1

		data = img.load()
		for x in xrange(img.size[0]):
			for y in xrange(img.size[1]):
				r, g, b = data[x, y]
				rgb = r / Const.COLOR_NEIGHBOR_DIST * Const.COLOR_NEIGHBOR_DIST, \
				      g / Const.COLOR_NEIGHBOR_DIST * Const.COLOR_NEIGHBOR_DIST, \
				      b / Const.COLOR_NEIGHBOR_DIST * Const.COLOR_NEIGHBOR_DIST
				color_set[RGBInt(rgb)] = color_set.get(RGBInt(rgb), 0) + 1

	new_color_set = {}
	for k, v in color_set.iteritems():
		if v >= len(imgs) * 2:  # 平均每个pic里出现不了2个pixel的可能不能算特征色了
			new_color_set[k] = v
	color_set = new_color_set

	try:
		print "d:", Const.MARK_DIAMETER[objID], "size:", Const.MARK_DIAMETER[objID] ** 2
	except:
		pass
	print d_set
	for v, k in sorted(map(lambda kv: (kv[1], kv[0]), color_set.iteritems()), reverse=True):
		print k, RGBTuple(k), ":", v, "   ave:", 1.0 * v / len(imgs), "   (%s, %.2lf, %s)" % (k, 1.0 * v / len(imgs), RGBTuple(k))

	print "=" * 40

	# ======= test  =====
	try:
		# fea: (f1, f2, f3, f1+f2, f2+f3, f1+f3, f1+f2+f3)
		f = map(lambda e: e[1], Const.MARK_FEATURE_COLOR[objID])
		ave = (f[0], f[1], f[2], f[0] + f[1], f[1] + f[2], f[0] + f[2], f[0] + f[1] + f[2])
		print ave, " <-- ave"
		for img in imgs:
			data = img.load()
			cnt = [0, 0, 0, 0, 0, 0, 0]
			for x in xrange(img.size[0]):
				for y in xrange(img.size[1]):
					r, g, b = data[x, y]
					rgb = r / Const.COLOR_NEIGHBOR_DIST * Const.COLOR_NEIGHBOR_DIST, \
					      g / Const.COLOR_NEIGHBOR_DIST * Const.COLOR_NEIGHBOR_DIST, \
					      b / Const.COLOR_NEIGHBOR_DIST * Const.COLOR_NEIGHBOR_DIST
					rgb = RGBInt(rgb)
					for i, elem in enumerate(Const.MARK_FEATURE_COLOR[objID]):
						if rgb == elem[0]:
							cnt[i] += 1
			cnt[3] = cnt[0] + cnt[1]
			cnt[4] = cnt[1] + cnt[2]
			cnt[5] = cnt[0] + cnt[2]
			cnt[6] = cnt[0] + cnt[1] + cnt[2]
			err = map(lambda v: abs(v[0] - v[1]), zip(ave, cnt))
			print cnt, "err_sum: %.3lf" % (sum(err) / (Const.MARK_DIAMETER[objID] ** 2)), "\t", ", ".join(map(lambda e: "%.2lf" % (e / Const.MARK_DIAMETER[objID] ** 2), err))
	except:
		pass



def Test():
	# CatchAllObjects()
	for ID in xrange(5):
		CalcFeatureForObject(ID)
