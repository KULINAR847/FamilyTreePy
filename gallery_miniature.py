# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtWidgets import QApplication, QMenu, QAction, QDialog, QLabel, QHBoxLayout, QFrame, QFileDialog
from PySide2.QtCore import QTranslator, QLibraryInfo, Qt, Signal
from PySide2.QtGui import QFont, QGuiApplication, QImage, QPixmap

from driver import AllTables
import datetime

import cv2
import numpy as np
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt

# Подготавливает маску, рисуя её в <antialias> раз больше и
# затем уменьшая, чтобы получилось сглаженно.
def prepare_mask(size, antialias = 2):
    mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
    return mask.resize(size, Image.ANTIALIAS)

# Обрезает и масштабирует изображение под заданный размер.
# Вообще, немногим отличается от .thumbnail, но по крайней мере
# у меня результат получается куда лучше.
def crop(im, s):
    w, h = im.size
    k = w / s[0] - h / s[1]
    if k > 0: im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
    elif k < 0: im = im.crop((0, (h - w) / 2, w, (h + w) / 2))
    return im.resize(s, Image.ANTIALIAS)

class MovableLabel(QLabel):
	getRectCoords = Signal(list)     
	def __init__(self, parent=0):
		super().__init__()
		self.setMouseTracking(True)
		self.s_point = (0,0)
		self.e_point = (0,0)
		
	
	#def mouseMoveEvent(self, ev):
	#	if self.e_point != self.s_point:
	#		self.getRectCoords.emit([self.s_point, self.e_point])

	def mousePressEvent(self, ev):
		#print('Pressed')
		self.s_point = (ev.x(), ev.y())
	
	def mouseReleaseEvent(self, ev):
		#print('Released')
		self.e_point = (ev.x(), ev.y())
		if self.e_point != self.s_point:
			self.getRectCoords.emit([self.s_point, self.e_point])

class GalleryMiniature(QDialog):
	def __init__(self, pid=0, filename=0):
		super().__init__()
		#self.resize(800,600)
		self.pid = pid
		#print(filename)
		self.filename = filename
		layout = QHBoxLayout()
		self.baseLabel = MovableLabel()
		self.baseLabel.setFrameShape(QFrame.StyledPanel)
		self.baseLabel.setAlignment(Qt.AlignCenter)
		self.baseLabel.getRectCoords.connect(self.getRectCoordsSlot)
		self.miniLabel = QLabel()
		self.miniLabel.setAlignment(Qt.AlignCenter)
		self.base_image = QImage()
		self.mini_image = QImage()
		self.base_image_scaled = 0
		#self.filename = 0
		self.pix = 0
		self.currentIndex = 0
		self.real_size = 0

		layout.addWidget(self.baseLabel)
		layout.addWidget(self.miniLabel)
	
		def openMenu(position):
			menu = QMenu()		  
			openAction = menu.addAction('Открыть') 
			saveAction = menu.addAction('Сохранить')			
			menu.addSeparator()
			nextAction = menu.addAction('Следующий')
			menu.addSeparator() 
			quitAction = menu.addAction('Выход')
			action = menu.exec_(self.mapToGlobal(position))

			if action == openAction:
				fileName = QFileDialog.getOpenFileName(self, "Изображение", "photos", "Фото (*.png *.jpg *.bmp *.JPG)")
				if len(fileName) > 1:
					self.filename = fileName[0]
					self.show_images()

			if action == saveAction:
				if self.filename:
					print('os.path.basename(self.filename)')
					path = os.path.basename(self.filename)
					root_ext = os.path.splitext(path)
					print(root_ext)
					if self.pid:
						root_ext = [str(pid) + '_001']
					minifile = os.path.join( os.path.join('photos', 'miniatures'), root_ext[0] + '.png')
					if self.pix:						
						self.pix.save(minifile, "PNG")
						print(minifile)							

			if action == nextAction:
				if self.base_image:
					self.get_face_image()
	
			if action == quitAction:
				self.close()

		self.setContextMenuPolicy(Qt.CustomContextMenu)		  
		self.customContextMenuRequested.connect(openMenu)		

		self.setLayout(layout)

		if self.filename:
			self.show_images()
		else:
			screen = QGuiApplication.primaryScreen()
			screenSize = screen.availableSize()
			sy = int( (screenSize.height()-20) / 4 )
			sx = int( (screenSize.width()-20) / 4 )
			self.setGeometry(sx, sy, int(screenSize.width()/4), int(screenSize.height()/4))

	def show_images(self):
		#print(self.filename)
		self.base_image.load(self.filename)
		self.real_size = (self.base_image.width(), self.base_image.height())
		screen = QGuiApplication.primaryScreen()
		screenSize = screen.availableSize()
		sy = int( (screenSize.height()-20) / 2 )
		sx = int( (screenSize.width()-20) / 2 )
		if not self.base_image_scaled:
			self.base_image_scaled = self.base_image.scaled(sx, sy, Qt.KeepAspectRatio)
			self.setGeometry(sx - int(self.base_image_scaled.width()), sy - int(self.base_image_scaled.height()/2), self.base_image_scaled.width() * 2 ,self.base_image_scaled.height())
		else:
			self.base_image_scaled = self.base_image.scaled(int(self.base_image_scaled.width()), int(self.base_image_scaled.height()), Qt.KeepAspectRatio)
			self.setGeometry(sx - int(self.base_image_scaled.width()), sy - int(self.base_image_scaled.height()/2), self.base_image_scaled.width() * 2 ,self.base_image_scaled.height())
		self.baseLabel.setPixmap( QPixmap.fromImage( self.base_image_scaled ) )
		#self.miniLabel.setPixmap(QPixmap.fromImage(self.base_image))
		self.get_face_image()

	def getRectCoordsSlot(self, coords):
		print(coords)
		if self.base_image:
			self.get_face_image(coords)

	def get_round_miniature(self, image):
		size = (300, 300)
		img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		im = Image.fromarray(img)
		#im = image #Image.open(image.png)
		im = crop(im, size)
		im.putalpha(prepare_mask(size, 4))
		#im.save(filename)
		qim = ImageQt(im)
		self.pix = QPixmap.fromImage(qim)
		self.miniLabel.setPixmap(self.pix)
		#self.miniature = QImage(filename)

	def get_face_image(self, coords=0): 
		with open(self.filename, 'rb') as f:
			chunk = f.read()
			chunk_arr = np.frombuffer(chunk, dtype=np.uint8)
		image = cv2.imdecode(chunk_arr, cv2.IMREAD_COLOR)      
		if coords == 0:
			print(self.filename)

			#image = cv2.imread(self.filename)
			# !!!!!!!!!!!! Обязательно указать правильный путь к файлу !!!!!!!!!!!!
			# !!!!!!!!!!!! Путь до xml есть в https://github.com/opencv/opencv/tree/master/data/haarcascades !!!!!!!!!!!! 
			face_cascade = cv2.CascadeClassifier( os.path.join('xml', 'haarcascade_frontalface_default.xml') )        
			# !!!!!!!!!!!! Необходимо настроить параметры так как находит не все лица !!!!!!!!!!!!
			faces_coord = face_cascade.detectMultiScale(image, scaleFactor=1.2, minNeighbors=5, minSize=(110, 110))        
			
			
			if (len(faces_coord) > 0):
				for i, face in enumerate(faces_coord):
					(x, y, w, h) = face                
					height, width, channels = image.shape
					s = int(min(width*0.1, height*0.1))
					if y - s >= 0:
						y = y - s
						h = h + s
					if x - s >= 0:
						x = x - s
						w = w + s                 
					h = h + s if y + h + s < height else h
					w = w + s if x + w + s < width else w
					if i == self.currentIndex:
						crop_image = image[y:y+h, x:x+w]
						#cv2.imshow("Face", crop_image)
						self.get_round_miniature(crop_image)
						break
					#cv2.waitKey(0)
				#crop_image.save()
			self.currentIndex = 0 if self.currentIndex + 1 >= len(faces_coord) else self.currentIndex + 1
		else:
			if self.real_size:
				#image = cv2.imread(self.filename)
				#x_scale =  self.base_image.width() /  self.base_image_scaled.width()
				#y_scale = self.base_image.height() / self.base_image_scaled.height()
				x_scale =  self.base_image.width() * self.base_image_scaled.width() / (self.base_image_scaled.width() * self.baseLabel.width())
				y_scale = self.base_image.height() * self.base_image_scaled.height() / (self.base_image_scaled.height() * self.baseLabel.height())
				print(( int(coords[0][1]*y_scale), int(coords[1][1]*y_scale), int(coords[0][0]*x_scale), int(coords[1][0]*x_scale) ))
				crop_image = image[int(coords[0][1]*y_scale):int(coords[1][1]*y_scale), int(coords[0][0]*x_scale):int(coords[1][0]*x_scale)]
				self.get_round_miniature(crop_image)


if __name__ == '__main__':
	app = QApplication(sys.argv)

	gm = GalleryMiniature()
	gm.showMaximized()

	sys.exit(app.exec_())