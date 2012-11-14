# -*- coding: UTF-8 -*-
import usb

class ExceptionStepperNotFound(Exception):
	pass

class StepperDevice:
	def __init__(self):
		self.dev = self.locate()
		if (not self.dev):
			raise ExceptionStepperNotFound("Device not found")

		self.initDevice()

	def locate(self):
		busses = usb.busses()

		for bus in busses:
			devices = bus.devices
			for dev in devices:
				if (dev.idVendor == 0x04f3 and dev.idProduct == 0xa003):
					return dev

		return None

	def initDevice(self):
		self.__devhandle = self.dev.open()
		self.__devhandle.setConfiguration(1)
		self.__devhandle.claimInterface(0)
		self.__devhandle.setAltInterface(0)

	def __del__(self):
		try:
			self.__devhandle.releaseInterface()
			del self.__devhandle
		except:
			pass

	def readDevice(self):
		self.__devhandle.controlMsg(requestType = 0x40,
			request = 0x06,
			value = 0,
			index = 0,
			buffer = chr(0x55))

		data = []
		for i in range(0,128):
			y = self.__devhandle.interruptRead(1, 8, 5000)
			data.extend(y)
			
		return data

	def eraseDevice(self):
		self.__devhandle.controlMsg(requestType = 0x40,
			request = 0x06,
			value = 0,
			index = 0,
			buffer = chr(0xaa))
