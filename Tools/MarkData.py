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
from Const import *
from sklearn import linear_model
from sklearn.externals import joblib
import Image
import numpy as np


def ReadImageFromFile(file):
	return Image.open(file)


models = {}
models_mid = {}


def SaveModels():
	for idx, model in models.iteritems():
		joblib.dump(model, "./Models/m_%d.model" % idx)
	joblib.dump(models_mid, "./Models/models_mid.mid")


def LoadModels(num=None):
	global models_mid
	global models
	if not num:
		num = len(MARK_NAME)
	for idx in xrange(num):
		models[idx] = joblib.load("./Models/m_%d.model" % idx)
	models_mid = joblib.load("./Models/models_mid.mid")


# =======  制作训练数据  =====================

def RGBWithIgnore(rgb_int):
	return rgb_int & RGB_NEIGHBOR_CREATOR

def RGBIntWithIgnore(rbg_tuple):
	return ((rbg_tuple[0] << 16) | (rbg_tuple[1] << 8) | rbg_tuple[2]) & RGB_NEIGHBOR_CREATOR

def RGBInt(rbg_tuple):
	return (rbg_tuple[0] << 16) | (rbg_tuple[1] << 8) | rbg_tuple[2]

def RGBTuple(rgb_int):
	return (rgb_int >> 16, (rgb_int >> 8) & 255, rgb_int & 255)

def GrayInt(rgb_tuple):
	return (rgb_tuple[0] * 30 + rgb_tuple[1] * 59 + rgb_tuple[2] * 11) / 100

def CreateGrayImage(img):
	for x in xrange(img.size[0]):
		for y in xrange(img.size[1]):
			g = GrayInt(img.getpixel((x, y)))
			img.putpixel((x, y), (g, g, g))
	return img

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
			if rgb in MARK_COLORS:
				name = MARK_NAME[MARK_COLORS[rgb]]
				ex, ey = x_size, y_size
				for xx in xrange(x, x_size):
					if RGBInt(data[xx, y]) != rgb:
						ex = xx
						break
				for yy in xrange(y, y_size):
					if RGBInt(data[x, yy]) != rgb:
						ey = yy
						break
				if ex - x > 3 and ey - y > 3:
					img.crop((x+1, y+1, ex-1, ey-1)).save("%s/%s/%s_%s_%s.bmp" % (MARK_IMAGE_PATH, name,pic_name, x, y))
					# # 灰度图
					# CreateGrayImage(img.crop((x+1, y+1, ex-1, ey-1))).save("%s/%s/%s_%s_%s.bmp" % (MARK_IMAGE_PATH, "Test", pic_name, x, y))

					for xx in xrange(x, ex):
						for yy in xrange(y, ey):
							vst.add((xx<<16)|yy)

	# 随机生成10个other系列12x12大小,用于训练
	num = 10
	while num > 0:
		x, y = random.randint(0, x_size - 13), random.randint(0, x_size - 13)
		ex, ey = x + 12, y + 12
		bad = False
		for xx in xrange(x, ex):
			for yy in xrange(y, ey):
				if (xx << 16) | yy in vst:
					bad = True
		if not bad:
			img.crop((x, y, ex, ey)).save("%s/%s/%s_%s_%s.bmp" % (MARK_IMAGE_PATH, "Other", pic_name, x, y))
			num -= 1


def CatchAllObjects():
	# 批处理抠图(抠出来存盘)
	for root, dirs, files in os.walk(MARK_IMAGE_ORIGIN_PATH):
		for file in files:
			if file.find(".bmp") == -1:
				continue
			img = ReadImageFromFile(os.path.join(MARK_IMAGE_ORIGIN_PATH, file))
			CatchSmallImageForObjects(img, file[0:-4])


def GetColorCntIgnore(img):
	color_cnt = {}
	data = img.load()
	for x in xrange(img.size[0]):
		for y in xrange(img.size[1]):
			rgb = RGBIntWithIgnore(data[x, y])
			color_cnt[rgb] = color_cnt.get(rgb, 0) + 1
	return color_cnt


def CreateFeatureList(objID, color_ig_cnt):
	div = MARK_DIAMETER[objID] ** 2
	f = [0, 0, 0, 0]
	# ave = [0, 0, 0]
	s = 0
	main_color = MARK_FEATURE_COLOR[objID]
	for i in xrange(len(main_color)):
		color, num, rgb = main_color[i]
		cnt = color_ig_cnt.get(color, 0)
		f[i] = 1.0 * abs(cnt - num) / div
		s += num
	f[3] = 1.0 * (div - s) / div
	# 	ave[i] = num
	# f[3] = 1.0 * abs(f[0] + f[1] - ave[0] - ave[1]) / div
	# f[4] = 1.0 * abs(f[1] + f[2] - ave[1] - ave[2]) / div
	# f[5] = 1.0 * abs(f[0] + f[2] - ave[0] - ave[2]) / div
	# f[6] = 1.0 * abs(f[0] + f[1] + f[2] - ave[0] - ave[1] - ave[2]) / div
	# f[7] = 1.0 * abs(div - (f[0] + f[1] + f[2])) / div
	return f


fea = np.array(((0.0, 0.0, 0.0, 0.0),))
def CalcSimilarScore(objID, color_ig_cnt):
	# 特征计算, color_cnt = { rgb_int: num }
	global fea, main_ave
	global models
	f = CreateFeatureList(objID, color_ig_cnt)
	for i in xrange(len(f)):
		fea[0][i] = f[i]
	return models[objID].predict_proba(fea)[0][0]


def GetMidOfModel(objID):
	return models_mid[objID]


# ============  特征测试 =========

def CalcFeatureForObject(objID):
	print "objID:", objID
	name = MARK_NAME[objID]
	imgs = []
	for root, dirs, files in os.walk(os.path.join(MARK_IMAGE_PATH, name)):
		for file in files:
			if file.find(".bmp") == -1:
				continue
			img = ReadImageFromFile(os.path.join(MARK_IMAGE_PATH, name, file))
			imgs.append(img)
	d_set = {}
	color_set = {}
	for img in imgs:
		d_set[img.size[0]] = d_set.get(img.size[0], 0) + 1
		d_set[img.size[1]] = d_set.get(img.size[1], 0) + 1

		data = img.load()
		for x in xrange(img.size[0]):
			for y in xrange(img.size[1]):
				color_set[RGBIntWithIgnore(data[x, y])] = color_set.get(RGBIntWithIgnore(data[x, y]), 0) + 1

	new_color_set = {}
	for k, v in color_set.iteritems():
		if v >= len(imgs) * 2:  # 平均每个pic里出现不了2个pixel的可能不能算特征色了
			new_color_set[k] = v
	color_set = new_color_set

	try:
		print "d:", MARK_DIAMETER[objID], "size:", MARK_DIAMETER[objID] ** 2
	except:
		pass
	print "d_set:", d_set
	for v, k in sorted(map(lambda kv: (kv[1], kv[0]), color_set.iteritems()), reverse=True):
		print k, RGBTuple(k), ":", v, "   ave:", 1.0 * v / len(imgs), "   (%s, %.2lf, %s)" % (k, 1.0 * v / len(imgs), RGBTuple(k))

	print "=" * 40

	# ======= test  =====
	try:
		# fea: (f1, f2, f3, f1+f2, f2+f3, f1+f3, f1+f2+f3)
		f = map(lambda e: e[1], MARK_FEATURE_COLOR[objID])
		ave = (f[0], f[1], f[2])
		print ave, " <-- ave"
		for img in imgs:
			data = img.load()
			c_cnt = {}

			for x in xrange(img.size[0]):
				for y in xrange(img.size[1]):
					rgb = RGBIntWithIgnore(data[x, y])
					c_cnt[rgb] = c_cnt.get(rgb, 0) + 1

			err = CreateFeatureList(objID, c_cnt)
			print "err_sum: %.3lf" % sum(err), "\t", ", ".join(map(lambda e: "%.2lf" % e, err))
	except:
		pass

	print "=" * 20


def TrainForObject(objID):
	print "objID:", objID
	name = MARK_NAME[objID]
	positive_features = []
	negative_features = []
	man_made_negative_features = []
	trainX, trainY = [], []
	testX, testY = [], []
	for root, dirs, files in os.walk(os.path.join(MARK_IMAGE_PATH, name)):
		for file in files:
			if file.find(".bmp") == -1:
				continue
			img = ReadImageFromFile(os.path.join(MARK_IMAGE_PATH, name, file))
			color_cnt = GetColorCntIgnore(img)
			positive_features.append(CreateFeatureList(objID, color_cnt))
			# for k, v in color_cnt.items():
			# 	color_cnt[k] = v  * 0.25
			# man_made_negative_features.append(CreateFeatureList(objID, color_cnt))

	for root, dirs, files in os.walk(os.path.join(MARK_IMAGE_PATH, "Other")):
		for file in files:
			if file.find(".bmp") == -1:
				continue
			img = ReadImageFromFile(os.path.join(MARK_IMAGE_PATH, "Other", file))
			negative_features.append(CreateFeatureList(objID, GetColorCntIgnore(img)))

	pro = 0.8
	for f in positive_features:
		if random.random() < pro:
			trainX.append(f)
			trainY.append(1)
		else:
			testX.append(f)
			testY.append(1)

	for f in man_made_negative_features:
		trainX.append(f)
		trainY.append(0)

	pro_n = min(pro, 1.0 * len(trainX) * 2 / len(negative_features))
	for f in negative_features:
		if random.random() < pro_n:
			trainX.append(f)
			trainY.append(0)
		else:
			testX.append(f)
			testY.append(0)

	model = linear_model.LogisticRegression(penalty="l2")
	model.fit(trainX, trainY)

	tt = model.predict_proba(trainX)
	l = 0
	r = 1.0
	for i in xrange(len(trainY)):
		if trainY[i]:
			l = max(l, tt[i][0])
		else:
			r = min(r, tt[i][0])
	mid = 0.75 * l + r * 0.25  # 不取中值了
	print "train l & r:", l, r, "mid:", mid


	tt = model.predict_proba(testX)
	ll = 0
	rr = 1.0
	bad_num = 0
	for i in xrange(len(testY)):
		if testY[i]:
			ll = max(ll, tt[i][0])
			if tt[i][0] > mid:
				bad_num += 1000
		else:
			rr = min(rr, tt[i][0])
			if tt[i][0] < mid:
				bad_num += 1
	print "test  l & r:", ll, rr
	print "bad:", bad_num
	print model.coef_, model.intercept_
	print "=" * 20
	global models
	models[objID] = model
	models_mid[objID] = mid


def Test():
	# CatchAllObjects()
	for ID in xrange(7):
		CalcFeatureForObject(ID)

	# for ID in xrange(7):
	# 	TrainForObject(ID)
	# SaveModels()