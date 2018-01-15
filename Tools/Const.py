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
AVATAR_MARK_COLOR = 0xffff00  # 地球的框框颜色
B1_MARK_COLOR = 0x000000  # 其他需要躲避障碍的框框颜色
B2_MARK_COLOR = 0xff0000
B3_MARK_COLOR = 0x00ffff
B4_MARK_COLOR = 0xff00ff

# 裱框颜色汇总
MARK_COLORS = [
	AVATAR_MARK_COLOR,
	B1_MARK_COLOR,
	B2_MARK_COLOR,
	B3_MARK_COLOR,
	B4_MARK_COLOR,
]

# 各个图像的平均直径(在320x240的图片中)
MARK_DIAMETER = [
	(),
	(),
	(),
	(),
	(),
]

