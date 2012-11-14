#!/usr/bin/python
# -*- coding: UTF-8 -*-
from StepperGUI import StepperGUI
from config import config

if __name__ == "__main__":
	config()
	g = StepperGUI()
	g.main()
