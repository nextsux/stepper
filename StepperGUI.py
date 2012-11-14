# -*- coding: UTF-8 -*-
import pygtk
pygtk.require('2.0')
import gtk
import os
import sqlite3 as sqlite

from Logs import Logs
from StepperDevice import *
from config import config

class StepperGUI:
	drawingAreaW = 450
	drawingAreaH = 350
	rulerH = 20

	def logListRepopulate(self):
		self.listStoreLogs.clear()
		self.logs.reload()

		for log in self.logs.logs:
			self.listStoreLogs.append([log[0], log[1]])
			

	def __init__(self):
		# init
		self.logs = Logs(self)
		self.currentLog = None

		# window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title("Stepper")
		self.window.set_border_width(10)

		self.window.set_icon(gtk.gdk.pixbuf_new_from_file(os.path.join(config.dataDir, "stepper.jpg")))

		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)

		self.hbox1 = gtk.HBox(False, 5)
		self.window.add(self.hbox1)

		# graph area
		self.vbox2 = gtk.VBox(False, 5)
		self.hbox1.pack_start(self.vbox2, True, True, 0)

		self.drawingArea = gtk.DrawingArea()
		self.drawingArea.set_size_request(self.drawingAreaW, self.drawingAreaH)

		self.vbox2.pack_start(self.drawingArea, True, True, 0)

		self.logInfoGrid = gtk.Table(2, 4, False)
		self.logInfoStepCntLabel = gtk.Label(u'Počet kroků:')
		self.logInfoStepCntLabel.set_alignment(0, 0.5)
		self.logInfoGrid.attach(self.logInfoStepCntLabel, 0, 1, 0, 1)

		self.logInfoStepCnt = gtk.Label(u'-')
		self.logInfoStepCnt.set_alignment(1, 0.5)
		self.logInfoGrid.attach(self.logInfoStepCnt, 1, 2, 0, 1)

		self.logInfoSampleCntLabel = gtk.Label(u'Počet vzorků:')
		self.logInfoSampleCntLabel.set_alignment(0, 0.5)
		self.logInfoGrid.attach(self.logInfoSampleCntLabel, 0, 1, 1, 2)

		self.logInfoSampleCnt = gtk.Label(u'-')
		self.logInfoSampleCnt.set_alignment(1, 0.5)
		self.logInfoGrid.attach(self.logInfoSampleCnt, 1, 2, 1, 2)

		self.logInfoDistLabel = gtk.Label(u'Vzdálenost v km:')
		self.logInfoDistLabel.set_alignment(0, 0.5)
		self.logInfoGrid.attach(self.logInfoDistLabel, 0, 1, 2, 3)

		self.logInfoDist = gtk.Label(u'-')
		self.logInfoDist.set_alignment(1, 0.5)
		self.logInfoGrid.attach(self.logInfoDist, 1, 2, 2, 3)

		self.logInfoKcalLabel = gtk.Label(u'Kalorií:')
		self.logInfoKcalLabel.set_alignment(0, 0.5)
		self.logInfoGrid.attach(self.logInfoKcalLabel, 0, 1, 3, 4)

		self.logInfoKcal = gtk.Label(u'-')
		self.logInfoKcal.set_alignment(1, 0.5)
		self.logInfoGrid.attach(self.logInfoKcal, 1, 2, 3, 4)

		self.vbox2.pack_end(self.logInfoGrid, True, True, 0)

		# log list
		self.listStoreLogs = gtk.ListStore(int, str)
		self.treeViewLogs = gtk.TreeView(self.listStoreLogs)
		self.tvColumnLogsId = gtk.TreeViewColumn(u'ID')
		self.tvColumnLogsDate = gtk.TreeViewColumn(u'Pořízení logu')
		self.treeViewLogs.append_column(self.tvColumnLogsId)
		self.treeViewLogs.append_column(self.tvColumnLogsDate)
		self.cellLogsId = gtk.CellRendererText()
		self.cellLogsDate = gtk.CellRendererText()
		self.tvColumnLogsId.pack_start(self.cellLogsId, True)
		self.tvColumnLogsDate.pack_start(self.cellLogsDate, True)
		self.tvColumnLogsId.add_attribute(self.cellLogsId, 'text', 0)
		self.tvColumnLogsDate.add_attribute(self.cellLogsDate, 'text', 1)

		self.treeViewLogsScrolledWin = gtk.ScrolledWindow()
		self.treeViewLogsScrolledWin.add_with_viewport(self.treeViewLogs)
		self.treeViewLogsScrolledWin.set_size_request(200, 200)
		self.treeViewLogsScrolledWin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

		self.hbox1.pack_start(self.treeViewLogsScrolledWin, True, True, 0)

		self.treeViewLogs.get_selection().connect('changed', self.logSelected)

		# button vbox
		self.vbox1 = gtk.VBox(False, 5)
		self.hbox1.pack_end(self.vbox1, True, True, 0)

		# download device
		self.buttonDownload = gtk.Button("Download")
		self.buttonDownload.connect("clicked", self.downloadData)
		self.vbox1.pack_start(self.buttonDownload, False, False, 0)

		# about dialog
		self.buttonAbout = gtk.Button("O aplikaci")
		self.buttonAbout.connect("clicked", self.aboutDialog)
		self.vbox1.pack_start(self.buttonAbout, False, False, 0)


		# exit button
		self.buttonExit = gtk.Button("Exit")
		self.buttonExit.connect_object("clicked", gtk.Widget.destroy, self.window)
		self.vbox1.pack_end(self.buttonExit, False, False, 0)

		self.accelGroup = gtk.AccelGroup()
		self.window.add_accel_group(self.accelGroup)
		self.buttonExit.add_accelerator("activate",
			self.accelGroup,
			ord('q'),
			gtk.gdk.CONTROL_MASK,gtk.ACCEL_LOCKED)

		# delete log
		self.buttonDeleteLog = gtk.Button("Delete log")
		self.buttonDeleteLog.connect("clicked", self.deleteSelectedLog)
		self.vbox1.pack_end(self.buttonDeleteLog, False, False, 0)

		# settings
		self.buttonSettings = gtk.Button("Nastavení")
		self.buttonSettings.connect("clicked", self.showSettings)
		self.vbox1.pack_end(self.buttonSettings, False, False, 0)

		self.window.show_all()

	def logSelected(self, data = None):
		selection = self.treeViewLogs.get_selection()
		if (selection.count_selected_rows() == 1):
			model, rows = selection.get_selected()
			log = self.logs.getLog(model[rows][0])

			self.logInfoStepCnt.set_text("%i" % log.steps)
			self.logInfoSampleCnt.set_text("%u" % len(log.samples))
			self.logInfoDist.set_text("%.2f km" % (float(log.steps) * config.stepLenCm / 100 / 1000))
			self.logInfoKcal.set_text("%i kcal" % (round(float(log.steps) * config.stepLenCm * config.kCalKm / 100 / 1000)))
			self.currentLog = log

		else:
			self.logInfoStepCnt.set_text(u"-")
			self.logInfoSampleCnt.set_text(u"-")
			self.logInfoDist.set_text(u"-")
			self.logInfoKcal.set_text(u"-")
			self.currentLog = None
			
		self.redrawDeawingArea()

	def aboutDialog(self, data = None):
		about = gtk.AboutDialog()
		about.set_program_name("Stepper")
		about.set_version("0.2")
		about.set_copyright("(c) Martin -nexus- Filip")
		about.set_comments("Simple tool for downloading logs from Dream Cheeky USB pedometer.\n\nDedicated to <3 Evisek")
		about.set_website("http://www.smoula.net/stepper")
		about.set_logo(gtk.gdk.pixbuf_new_from_file(os.path.join(config.dataDir, "stepper.jpg")))
		about.run()
		about.destroy()

	def deleteSelectedLog(self, data = None):
		selection = self.treeViewLogs.get_selection()
		if (selection.count_selected_rows() == 1):
			dialog = gtk.MessageDialog(
				self.window,
				gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
				gtk.MESSAGE_WARNING,
				gtk.BUTTONS_YES_NO,
				u'Opravdu chcete smazat log?'
			)
			dialog.format_secondary_text(u'Tato akce je nevratná!')
			response = dialog.run()
			dialog.destroy()

			if (response == gtk.RESPONSE_YES):
				model, rows = selection.get_selected()
				self.logs.deleteLog(model[rows][0])

	def downloadData(self, data = None):
		try:
			s = StepperDevice()
			log = self.logs.parseData(s.readDevice())

			if (len(log.samples) == 0):
				dialog = gtk.MessageDialog(
					self.window,
					gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_INFO ,
					gtk.BUTTONS_OK ,
					u'Zařízení neobsahuje žádná data'
				)
				dialog.run()
				dialog.destroy()

			else:
				dialog = gtk.MessageDialog(
					self.window,
					gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_QUESTION,
					gtk.BUTTONS_YES_NO,
					u'Stažení dat ze zařízení'
				)
				dialog.format_secondary_text(u"Zařízení obsahuje %i kroků v %i vzorcích. Opravdu si je přejete stáhnout?" % (log.steps, len(log.samples)))
				response = dialog.run()
				dialog.destroy()

				if (response == gtk.RESPONSE_YES):
					log = self.logs.parseData(s.readDevice())
					log.saveLog()

					s.eraseDevice()
					self.logListRepopulate()

			del s

		except ExceptionStepperNotFound, e:
			dialog = gtk.MessageDialog(
				self.window,
				gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
				gtk.MESSAGE_WARNING ,
				gtk.BUTTONS_OK,
				u'Zařízení nenalezeno'
			)
			dialog.run()
			dialog.destroy()

	def createSettingsDialog(self, stepLenCmVal, kCalKmVal):
		settings = gtk.Dialog(
			u'Nastavení',
			self.window,
			gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
		)
		settings.add_buttons(
			gtk.STOCK_APPLY, gtk.RESPONSE_OK,
			gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE
		)

		cont = settings.get_content_area()

		grid = gtk.Table(2, 4, False)

		stepLenLabel = gtk.Label(u'Délka kroku [cm]:')
		stepLenLabel.set_alignment(0, 0.5)
		grid.attach(stepLenLabel, 0, 1, 0, 1)

		stepLen = gtk.Entry(max=3)
		stepLen.set_text("%s" % stepLenCmVal)
		grid.attach(stepLen, 1, 2, 0, 1)

		kCalKmLabel = gtk.Label(u'Kalorií na km [kcal]:')
		kCalKmLabel.set_alignment(0, 0.5)
		grid.attach(kCalKmLabel, 0, 1, 1, 2)

		kCalKm = gtk.Entry(max=3)
		kCalKm.set_text("%s" % kCalKmVal)
		grid.attach(kCalKm, 1, 2, 1, 2)
		
		cont.pack_start(grid, True, True, 0)

		cont.show_all()

		return (settings, stepLen, kCalKm)

	def showSettings(self, data = None):
		exit = False
		stepLenCm = config.stepLenCm
		kCalKm = config.kCalKm

		while not exit:
			(d, stepLenEntry, kCalKmEntry) = self.createSettingsDialog(stepLenCm, kCalKm)
			r = d.run()

			if (r == gtk.RESPONSE_OK):
				try:
					stepLenCm = int(stepLenEntry.get_text())
				except ValueError, e:
					stepLenCm = 0

				try:
					kCalKm = int(kCalKmEntry.get_text())
				except ValueError, e:
					kCalKm = 0

				if (
					stepLenCm > 10 and
					stepLenCm < 200 and
					kCalKm > 10 and
					kCalKm < 150
				):
					con = sqlite.connect(config.DB)
					cur = con.cursor()
		
					cur.execute("UPDATE settings SET steplencm = ?, kcalperkm = ?;", (stepLenCm, kCalKm))
					con.commit()
					cur.close()

					config.stepLenCm = stepLenCm
					config.kCalKm = kCalKm

					exit = True
			else:
				exit = True

			d.destroy()

		self.logSelected()

	def eraseDrawingArea(self):
		drawable = self.drawingArea.window
		colorBG		= drawable.get_colormap().alloc_color(65535, 65535, 65535)
		colorRulers	= drawable.get_colormap().alloc_color(0, 0, 0)

		gc = drawable.new_gc()

		# clear
		gc.set_background(colorBG)
		gc.set_foreground(colorBG)

		drawable.draw_rectangle(gc, True, 0, 0, self.drawingAreaW, self.drawingAreaH)

		gc.set_foreground(colorRulers)
		drawable.draw_line(gc, 0, self.drawingAreaH - self.rulerH, self.drawingAreaW, self.drawingAreaH - self.rulerH)

		if (self.currentLog):
			hourY = int(self.drawingAreaH - 0.05 * self.rulerH)
			halfHourY = int(self.drawingAreaH - 0.50 * self.rulerH)
			qHourY = int(self.drawingAreaH - 0.85 * self.rulerH)

			for i in range(0, len(self.currentLog.samples) + 1):
				stepW = int(self.drawingAreaW / len(self.currentLog.samples) * i)

				if (i % 4) == 0:
					y = hourY
				elif (i % 4) == 1 or (i % 4) == 3:
					y = qHourY
				else:
					y = halfHourY

				drawable.draw_line(gc, stepW, self.drawingAreaH - self.rulerH, stepW, y)
				
		
	def redrawDeawingArea(self):
		self.eraseDrawingArea()

		drawable = self.drawingArea.window
		colorBG		= drawable.get_colormap().alloc_color(65535, 65535, 65535)
		colorLine	= drawable.get_colormap().alloc_color(65535, 0, 0)

		gc = drawable.new_gc(line_width = 2)
		gc.set_background(colorBG)
		gc.set_foreground(colorLine)

		lastX = 0
		lastY = 0

		if (self.currentLog):
			stepW = float(self.drawingAreaW) / len(self.currentLog.samples)
			stepH = float(self.drawingAreaH - self.rulerH) / self.currentLog.steps

			sumSteps = 0
			for sampleNo, steps in self.currentLog.samples.iteritems():
				sampleNoX = sampleNo + 1
				sumSteps = sumSteps + steps

				lineX = int(sampleNoX * stepW)
				lineY = int(sumSteps * stepH)

				drawable.draw_line(gc, lastX, self.drawingAreaH - lastY - self.rulerH, lineX + 0, self.drawingAreaH - lineY - self.rulerH)

				lastX = lineX
				lastY = lineY

	def main(self):
		self.logListRepopulate()
		gtk.main()

	def delete_event(self, widget, event, data=None):
		return False

	def destroy(self, widget, data=None):
		gtk.main_quit()
