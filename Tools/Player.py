# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
	kongzhao
	kongzhao135@163.com
Date:
	2018/1/18
Description:
	主控制器
----------------------------------------------------------------------------"""

import Const
import time
from Tools import Recognize, CatchScreen, Strategy
from Tools.Event import ReleaseKey, PressKey, KEY_SPACE, GKeyBoardEvent, KEY_F, KEY_ESC
import multiprocessing


class Controllor(multiprocessing.Process):
	def __init__(self, queue):
		super(Controllor, self).__init__()
		self.interval = Const.CONTROL_INTERVAL
		self.queue = queue
		self.pwm = 0
		self.cnt = 0

		self.running = True
		self.is_pressed = False

	def stop(self):
		ReleaseKey(KEY_SPACE)
		self.is_pressed = False

	def do_pwn(self):
		if not self.running:
			return
		# 这个操作居然很耗时(0.09才能完成一次)
		# t = time.time()
		# print "tick", t
		if self.cnt < self.pwm:
			if not self.is_pressed:
				PressKey(KEY_SPACE)
				self.is_pressed = True
		else:
			if self.is_pressed:
				ReleaseKey(KEY_SPACE)
				self.is_pressed = False
		# print time.time() - t

	def run(self):
		while True:
			start = time.time()
			self.cnt = (self.cnt + 1) % Const.CONTROL_CIRCLE
			if not self.queue.empty():
				val = self.queue.get(False)
				while not self.queue.empty():
					# 只处理最新的请求
					val = self.queue.get(False)
				if val == "esc":
					# print "esc"
					break
				if val == "run":
					# print "run"
					self.running = True
				elif val == "pause":
					# print "pause"
					self.running = False
					self.stop()
				elif val == "start_game":
					if self.running:
						ReleaseKey(KEY_SPACE)
						time.sleep(0.4)
						PressKey(KEY_SPACE)
						self.is_pressed = False
				else:
					self.pwm = val
			# 控制
			self.do_pwn()
			interval = max(0, self.interval - time.time() + start)
			time.sleep(interval)
		self.stop()


class Player(object):
	def __init__(self):
		self.strategy = Strategy.Strategy()
		self.queue = multiprocessing.Queue()
		self.keyHook = GKeyBoardEvent(self.keyboard_hook)
		self.keyHook.start()
		self.ctrl = Controllor(self.queue)
		self.ctrl.start()
		# 一些标志
		self.is_stopped = False

	def keyboard_hook(self, code, character, press):
		if not press:
			return
		if code == KEY_F[1]:
			self.queue.put("run")
		elif code == KEY_F[2]:
			self.queue.put("pause")
		elif code == KEY_ESC:
			self.is_stopped = True

	def loop(self):
		while True:
			if self.is_stopped:
				break
			start_time = time.time()
			# 采样
			img = CatchScreen.CatchScreen(None, Const.SCALE_DIV)
			if not img:
				continue
			if Recognize.IsInGame(img):
				# 识别
				avatar, others = Recognize.FindObjs(img)
				# 策略
				pwm = self.strategy.Update(avatar, others, start_time)
			else:
				print "Game Over!"
				self.strategy.GameOver()  # 游戏结束存盘
				pwm = "start_game"  # 开启下一局
			# print "pwm", pwm
			self.queue.put(pwm)

			use_time = time.time() - start_time
			if use_time > Const.MAIN_AI_INTERVAL:
				# 超时
				img.save("./GameData/HardRecognizeImage/img_%s.bmp" % int(time.time() * 100))
			else:
				time.sleep(max(0, Const.MAIN_AI_INTERVAL - use_time))

		self.queue.put("esc")
		self.keyHook.stop()


def Test():
	player = Player()
	player.loop()
