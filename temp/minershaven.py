
from __future__ import annotations

import pywinauto
import pywinauto.controls as pwa_controls
import os
import psutil
import cv2
import numpy as np

from dataclasses import dataclass
from time import sleep
from PIL import Image

FILE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
ROBLOX_PROCESS_NAME = 'RobloxPlayerBeta.exe'

def find_processes_by_name( name : str ) -> list[psutil.Process]:
	return list( filter( lambda x : name in x.name(), psutil.process_iter() ) )

def get_image_path( filename : str ) -> str:
	return os.path.join( FILE_DIRECTORY, filename )

# # sorts monitor by left to right
# def get_monitors( ) -> list[ tuple ]:
#	import win32api
# 	monitors = [ win32api.GetMonitorInfo(item[0])['Work'] for item in win32api.EnumDisplayMonitors() ]
# 	return sorted(monitors, key=lambda tup: tup[0])

@dataclass
class Rect:
	x : int = 0
	y : int = 0
	w : int = 0
	h : int = 0

class ImageUtility:

	@staticmethod
	def convert_to_cv2_img( img : Image.Image ) -> np.ndarray:
		return np.array( img.convert('RGB') )[:, :, ::-1].copy()

	@staticmethod
	def find_matches_in_image( img : Image.Image, target : Image.Image, threshold : float | int = 0.6 ) -> list[Rect]:
		img_cv : np.ndarray = ImageUtility.convert_to_cv2_img( img )
		target_cv : np.ndarray = ImageUtility.convert_to_cv2_img( target )

		w, h = target_cv.shape[:-1]
		res = cv2.matchTemplate(img_cv, target_cv, cv2.TM_CCOEFF_NORMED)

		loc = np.where(res >= threshold)
		return [ Rect(x=x, y=y, w=w, h=h) for (x, y) in zip(*loc[::-1]) ]

class ApplicationWrapper:
	pid : int
	app = pywinauto.Application
	handler : pwa_controls.hwndwrapper.HwndWrapper

	def __init__( self, pid : int ) -> ApplicationWrapper:
		self.pid = pid
		self.app = pywinauto.Application().connect(process=roblox_pid)
		self.handler = self.app.window().wrapper_object()

	def screenshot_window( self ) -> Image.Image:
		# self.handler.set_focus()
		return self.handler.capture_as_image()

	def locateFileOnWindow( self, filepath : str, threshold : float | int = 0.6 ) -> Rect | None:
		target = Image.open( filepath )
		source : Image.Image = self.screenshot_window()
		locations : list[Rect] = ImageUtility.find_matches_in_image( source, target, threshold=threshold )
		if len(locations) == 0:
			return None
		return locations[0]

try:
	processes = find_processes_by_name(ROBLOX_PROCESS_NAME)
	print( processes )
	roblox_pid = processes[0].pid
except:
	raise Exception('Roblox process could not be found!')

wrapper = ApplicationWrapper( roblox_pid )

def has_no_ores( ) -> bool:
	rect = wrapper.locateFileOnWindow( get_image_path('ore_limit_0.PNG'), threshold=0.95 )
	return rect != None

def has_no_money( ) -> bool:
	rect = wrapper.locateFileOnWindow( get_image_path('default_money.PNG'), threshold=0.9 )
	return rect != None

def open_settings( keybind : str = 'c' ) -> None:
	rect = wrapper.locateFileOnWindow( get_image_path('settings_button.PNG'), threshold=0.8 )
	if rect != None:
		return
	wrapper.handler.type_keys(keybind, set_foreground=False, vk_packet=False)
	sleep(0.2)
	rect = wrapper.locateFileOnWindow( get_image_path('settings_button.PNG'), threshold=0.8 )
	if rect == None:
		raise Exception('Failed to open the settings widget with keybind "C"!')

def open_layouts( keybind='l' ) -> None:
	rect = wrapper.locateFileOnWindow( get_image_path('layout_1.PNG') )
	if rect != None:
		return
	wrapper.handler.type_keys(keybind, set_foreground=False, vk_packet=False)
	sleep(0.2)
	rect = wrapper.locateFileOnWindow( get_image_path('layout_1.PNG') )
	if rect == None:
		raise Exception('Failed to open the settings widget with keybind "C"!')

def move_mouse( x, y ) -> None:
	wrapper.handler.drag_mouse_input((40, 40), (50, 40), button='middle')
	wrapper.handler.release_mouse_input(absolute=False, button='middle')

def click_at_coords( x, y, click, absolute : bool = False ) -> None:
	move_mouse( x, y )
	wrapper.handler.click_input(click, (x, y), absolute=absolute, key_down=False, key_up=False)

def load_layout_1( ) -> None:
	open_layouts( )
	rect = wrapper.locateFileOnWindow( get_image_path('layout_1.PNG'), threshold=0.5 )
	if rect == None:
		raise Exception('Cannot find the layout 1 button.')
	click_at_coords( rect.x + 600, rect.y + 60, 'left' )
	wrapper.handler.type_keys('l', set_foreground=False, vk_packet=False)
	sleep(3)

def press_rebirth( ) -> None:
	open_settings( )

	rect2 = wrapper.locateFileOnWindow( get_image_path('red_yes.PNG'), threshold=0.8 )
	if rect2 != None:
		move_mouse( rect.x + 30, rect.y + 10 )
		wrapper.handler.click_input('left', (rect2.x + 30, rect2.y + 10), absolute=False, key_down=False, key_up=False)
		wrapper.handler.click_input('left', (rect2.x + 30, rect2.y + 10), absolute=False, key_down=False, key_up=False)
		sleep(3)
		return

	rect = wrapper.locateFileOnWindow( get_image_path('reborn_button.PNG'), threshold=0.8 )
	if rect == None:
		raise Exception('Cannot find the rebirth button.')
	move_mouse( rect.x + 30, rect.y + 10 )
	wrapper.handler.click_input('left', (rect.x + 30, rect.y + 10), absolute=False, key_down=False, key_up=False)
	rect2 = wrapper.locateFileOnWindow( get_image_path('red_yes.PNG'), threshold=0.8 )
	if rect2 != None:
		wrapper.handler.click_input('left', (rect2.x + 30, rect2.y + 10), absolute=False, key_down=False, key_up=False)
		wrapper.handler.click_input('left', (rect2.x + 30, rect2.y + 10), absolute=False, key_down=False, key_up=False)
		sleep(3)
	else:
		print('Could not rebirth because not enough money!')

while True:
	if has_no_ores() == True:
		print('Loading Layout - no ores!')
		load_layout_1( )

	while has_no_money( ):
		print('Waiting for Money!')
		sleep(1)

	print('Has money, keep pressing rebirth!')
	while not has_no_ores( ):
		press_rebirth( )
		sleep(0.1)

	sleep(1)
