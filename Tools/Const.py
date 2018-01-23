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

# 标记数据
MARK_IMAGE_ORIGIN_PATH = "./MarkImage/Origin/"
MARK_IMAGE_PATH = "./MarkImage/"

AVATAR_ID = 0

AVATAR_MARK_COLOR = 0xffff00  # 地球的框框颜色
B1_MARK_COLOR = 0x000000  # 其他需要躲避障碍的框框颜色
B2_MARK_COLOR = 0xff0000
B3_MARK_COLOR = 0x00ffff
B4_MARK_COLOR = 0xff00ff
B5_MARK_COLOR = 0x0000ff
B6_MARK_COLOR = 0x00ff00

MARK_NAME = [
	"Avatar",
	"B1",
	"B2",
	"B3",
	"B4",
	"B5",
	"B6",
]

MARK_ID_COLORS = [
	AVATAR_MARK_COLOR,
	B1_MARK_COLOR,
	B2_MARK_COLOR,
	B3_MARK_COLOR,
	B4_MARK_COLOR,
	B5_MARK_COLOR,
	B6_MARK_COLOR,
]

# 裱框颜色汇总
MARK_COLORS = {k: v for v, k in enumerate(MARK_ID_COLORS)}

# 各个图像的平均直径(在320x240的图片中)
MARK_DIAMETER = [
	9,
	6,
	8,
	10,
	12,
	7,
	9,
]

MARK_FEATURE_COLOR = [
	# RGB, ave_cnt, (R,G,B)
	[(1878236, 29.08, (28, 168, 220)), (9228404, 23.91,(140, 208, 116)), (1609912, 5.14, (24, 144, 184))],  # Avatar
	[(8947848, 13.1, (136, 136, 136)), (5789784, 6.6, (88, 88, 88)), (12632256, 4.4, (192, 192, 192))],
	[(16532548, 23.48, (252, 68, 68)), (10496040, 8.34, (160, 40, 40)), (16560304, 6.74, (252, 176, 176))],
	[(12608524, 34.71, (192, 100, 12)), (8668168, 12.04, (132, 68, 8)), (16547852, 9.50, (252, 128, 12))],
	[(8388772, 56.56, (128, 0, 164)), (12321004, 20.96, (188, 0, 236)), (16547852, 14.32, (252, 128, 12))],
	[(6845648, 12.27, (104, 116, 208)), (4997216, 6.14, (76, 64, 96)), (5792960, 4.68, (88, 100, 192))],
	[(5556360, 33.67, (84, 200, 136)), (3967072, 14.33, (60, 136, 96)), (8172692, 9.44, (124, 180, 148))],
]


COLOR_NEIGHBOR_BIT = 2  # 将(r,g,b)各忽略COLOR_NEIGHBOR_BIT位后判断是不是一种颜色
RGB_NEIGHBOR_CREATOR = 0xfcfcfc  # rgb & COLOR_NEIGHBOR_CREATOR 可直接获得邻域


CONTROL_INTERVAL = 0.10  # (N ms为间隔进行控制)
CONTROL_CIRCLE = 2       # 一个周期N个INTERVAL

MAIN_AI_INTERVAL = 0.20  # AI的决策周期(截图+分析+控制策略)
