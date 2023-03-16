from kivy.config import Config
Config.set('graphics', 'resizable', True)
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.clock import mainthread

from gtts import gTTS
from pygame import mixer
import threading
import os
import re


class WindowManager(ScreenManager):
	def __init__(self, **kwargs):
		super(WindowManager, self).__init__(**kwargs)


class Speaker(Screen):
	def __init__(self, **kwargs):
		super(Speaker, self).__init__(**kwargs)


	def openAlert(self, title:str, text:str):
		def closeAlert(*args):
			self.dialog.dismiss()

		self.dialog = MDDialog(
			title=title,
			text=text,
			buttons=[
				MDRectangleFlatButton(
					text='Aceptar',
					on_press=closeAlert
				)
			]
		)
		self.dialog.open()

	def load(self):
		active:bool = not self.ids.loading.active
		self.ids.loading.active = active
		for id in ['save', 'play', 'stop']:
			self.ids[id].disabled = active

	@mainthread
	def saveAudio(self, file:str, text:str):# -> mp3
		ofile = file
		otext = text
		file = file.text
		text = text.text
		try:
			if file != '':
				if re.compile(r'(.?)+\.mp3').fullmatch(file):
					if text != '':	
						gTTS(text=text, lang="es", slow=False).save(f"{file}.mp3")
						
					else:
						self.openAlert(
							title='Atención',
							text='El campo: \'Enunciado\', esta vacío.'
						)
				else:
					self.openAlert(
						title='Atención',
						text='El formato del archivo no es valido.'
					)
			else:
				self.openAlert(
					title='Atención',
					text='El campo: \'Nombre_del_Archivo.mp3\', esta vacío.'
				)

		except:
			self.openAlert(
				title='¡Lo Sentimos!',
				text='Ah ocurrido un error al guardar el audio.'
			)
		finally:
			self.load()


	def playAudio(self, file:str, stop):
		if file != '':
			file += ".mp3"
			try:
				mixer.init()
				mixer.music.load(file)
				mixer.music.play()
				stop.disabled = False
				self.playing = mixer.music
			except:
				self.openAlert(
					title='Error',
					text=f'Audio ({file}) no encontrado.'
				)
		else:
			self.openAlert(
				title='Atención',
				text='Debes agregar el nombre del archivo (En caso de que el archivo no se encuentre en esta carpeta: c:/directorio/del/archivo/nombre_del_archivo.mp3).'
			)
kv = """
#: import threading threading

WindowManager:
	Speaker:

<Speaker>:
	id: speaker
	name: 'speaker'

	MDFloatLayout:
		cols: 1

		MDGridLayout:
			id: background
			name: 'background'

			cols: 1
			pos_hint: {'center_x': .5, 'center_y': .5}
			spacing: dp(10)
			padding: dp(10), dp(5), dp(5), dp(5)
			md_bg_color: (1, 1, 1, 1)#(39/255, 169/255, 76/255, 1)

			MDLabel:
				text: '[b][color=#1C5E7C]Convertidor de Texto a MP3[/color][/b]'
				font_size: dp(30)
				markup: True
				halign: 'left'
				valign: 'center'
				size_hint: (1, .1)

			MDFloatLayout:
				cols: 1
				size_hint: 1, .15
				
				MDTextFieldRect:
					id: file
					name: 'file'

					hint_text: 'Nombre_del_Archivo.mp3'
					on_text: file.text = file.text.replace(' ', '')
					pos_hint: {'center_x': .5, 'center_y': .5}

				MDIconButton:
					icon: 'alpha-x-box'
					theme_text_color: 'Custom'
					text_color: (.7, .7, .7, 1)
					pos_hint: {'top': 1}
					x: root.size[0]-45
					on_press: file.text = ''

			MDFloatLayout:
				cols: 1
				
				MDTextFieldRect:
					id: text
					name: 'text'

					hint_text: 'Enunciado (Opcional solo para reproducir)'
					pos_hint: {'center_x': .5, 'center_y': .5}

				MDIconButton:
					icon: 'alpha-x-box'
					theme_text_color: 'Custom'
					text_color: (.7, .7, .7, 1)
					pos_hint: {'top': 1}
					x: root.size[0]-45
					on_press: text.text = ''

			MDGridLayout:
				id: buttons
				name: 'buttons'

				cols: 3
				spacing: dp(10)
				size_hint: (1, .1)

				MDRaisedButton:
					id: save
					name: 'save'

					text: 'Guardar'
					md_bg_color: (0, 0, 0, 0)
					size_hint_y: 1
					on_press:
						load = threading.Thread(target=root.load)
						load.start()
						load.join()
						save = threading.Thread(target=root.saveAudio, args=(file, text,))
						save.start()

					canvas.before:
						Color:
							rgba: (77/255, 160/255, 243/255, 1)

						RoundedRectangle:
							size: self.size
							pos: self.pos

					canvas.after:
						Color:
							rgba: (1, 1, 1, 1)

						Line:
							rounded_rectangle: (self.pos[0], self.pos[1], self.size[0], self.size[1], 10, 10, 10, 10, 100)
							width: 1
				Button:
					id: play
					name: "play"

					text: 'Reproducir Audio'
					color: (77/255, 160/255, 243/255, 1)
					background_color: (0, 0, 0, 0)
					size_hint: 2, 1
					on_press: root.playAudio(file.text, stop)

					canvas.before:
						Color:
							rgba: (1, 1, 1, 1)

						RoundedRectangle:
							size: self.size
							pos: self.pos

					canvas.after:
						Color:
							rgba: (77/255, 160/255, 243/255, 1)

						Line:
							rounded_rectangle: (self.pos[0], self.pos[1], self.size[0], self.size[1], 10, 10, 10, 10, 100)
							width: 1

				Button:
					id: stop
					name: "stop"

					text: 'Stop'
					disabled: True
					color: (1, 1, 1, 1)
					background_color: (0, 0, 0, 0)
					on_press:
						root.playing.stop()
						del root.playing
						stop.disabled = True

					canvas.before:
						Color:
							rgba: (.7, 0, 0, .8)
						RoundedRectangle:
							size: self.size
							pos: self.pos

					canvas.after:
						Color:
							rgba: (1, 1, 1, 1)


						Line:
							rounded_rectangle: (self.pos[0], self.pos[1], self.size[0], self.size[1], 10, 10, 10, 10, 100)
							width: 1

		MDSpinner:
			id: loading
			name: 'loading'

			active: False
			pos_hint: {'center_x': .5, 'center_y': .5}
			size_hint: None, None
			size: dp(50), dp(50)
"""
class main(MDApp):
	def build(self):
		self.title = 'Converter'
		Window.size = (600, 690)
		#Window.top = 0
		#Window.left = .2
		return Builder.load_string(kv)

	def on_start(self):
		pass


if __name__ == "__main__":
	main().run()