# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    kongzhao
    kongzhao135@163.com
Date:
    2018/1/12
Description:

----------------------------------------------------------------------------"""

ScreenSize = (646, 508)     # 整个hwnd窗口界面的大小
GameFrameSize = (640, 480)  # 有效区域的偏移
GameFrameOffset = (3, 24)  # 左上角和Screen间的偏移
SCALE_DIV = 2  # 640x480长宽个缩小2倍，这样图片只有原来的1/4处理速度快

AVE_IMAGE = "./Objects/ave_image.bmp"

# 标记数据
MARK_IMAGE_ORIGIN_PATH = "./MarkImage/Origin/"
MARK_IMAGE_PATH = "./MarkImage/"
AVATAR_MARK_COLOR = 0xffff00  # 地球的框框颜色
B1_MARK_COLOR = 0x000000  # 其他需要躲避障碍的框框颜色
B2_MARK_COLOR = 0xff0000
B3_MARK_COLOR = 0x00ffff
B4_MARK_COLOR = 0xff00ff

MARK_NAME = [
	"Avatar",
	"B1",
	"B2",
	"B3",
	"B4",
]

# 裱框颜色汇总
MARK_COLORS = {
	AVATAR_MARK_COLOR: 0,
	B1_MARK_COLOR: 1,
	B2_MARK_COLOR: 2,
	B3_MARK_COLOR: 3,
	B4_MARK_COLOR: 4,
}

# 各个图像的平均直径(在320x240的图片中)
MARK_DIAMETER = [
	9,
	6,
	8,
	10,
	12,
]

MARK_FEATURE_COLOR = [
	# RGB, ave_cnt, (R,G,B)
	[(1878236, 29.08, (28, 168, 220)), (9228404, 23.91,(140, 208, 116)), (1609912, 5.14, (24, 144, 184))],  # Avatar
	[(8947848, 13.1, (136, 136, 136)), (5789784, 6.6, (88, 88, 88)), (12632256, 4.4, (192, 192, 192))],
	[(16532548, 23.48, (252, 68, 68)), (10496040, 8.34, (160, 40, 40)), (16560304, 6.74, (252, 176, 176))],
	[(12608524, 34.71, (192, 100, 12)), (8668168, 12.04, (132, 68, 8)), (16547852, 9.50, (252, 128, 12))],
	[(8388772, 56.56, (128, 0, 164)), (12321004, 20.96, (188, 0, 236)), (16547852, 14.32, (252, 128, 12))],
]


COLOR_NEIGHBOR_DIST = 4  # 将rgb / 4后判断是不是一种颜色

