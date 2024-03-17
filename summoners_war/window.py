
from __future__ import annotations
from typing import overload

import psutil

class NoProcessFound(Exception): pass

class ProcessUtility:

	@staticmethod
	def find_by_name( name : str ) -> psutil.Process | None:
		for process in psutil.process_iter():
			if process.name() == name:
				return process
		raise NoProcessFound(f'Could not find the process of name: {str(name)}')

	@staticmethod
	def find_by_pid( pid : int ) -> psutil.Process | None:
		for process in psutil.process_iter():
			if process.pid == pid:
				return process
		raise NoProcessFound(f'Could not find the process of id: {str(pid)}')

class ControllerInterface:

	window : Window = None

	def __init__( self : ControllerInterface ) -> ControllerInterface:
		self.__import__() # run imports

	def __import__( self : ControllerInterface ) -> None:
		raise NotImplementedError

	# hook the target window
	def hook_window( self : ControllerInterface, window : Window ) -> None:
		self.window = window

	def is_window_hooked( self : ControllerInterface ) -> bool:
		return self.window != None

	# click actions
	def mouse_click( self : ControllerInterface, button : str | int, x : int, y : int ) -> None:
		raise NotImplementedError

	# key up
	@overload
	def key_up( self : ControllerInterface, key_name : str ) -> None:
		...

	@overload
	def key_up( self : ControllerInterface, key_id : int ) -> None:
		...

	def key_up( self : ControllerInterface, key_value : str | int ) -> None:
		raise NotImplementedError

	# key down
	@overload
	def key_down( self : ControllerInterface, key_name : str ) -> None:
		...

	@overload
	def key_down( self : ControllerInterface, key_id : int ) -> None:
		...

	def key_down( self : ControllerInterface, key_value : str | int ) -> None:
		raise NotImplementedError

	# key press
	@overload
	def key_press( self : ControllerInterface, key_name : str ) -> None:
		...

	@overload
	def key_press( self : ControllerInterface, key_id : int ) -> None:
		...

	def key_press( self : ControllerInterface, key_value : str | int ) -> None:
		raise NotImplementedError

class ControllerWin32API(ControllerInterface):

	win32gui = None

	def __init__(self) -> ControllerWin32API:
		super().__init__()

	def __import__( self : ControllerInterface ) -> None:
		import win32gui
		self.win32gui = win32gui

class Window:
	process : psutil.Process
	controller : ControllerInterface

	def __init__( self ) -> Window:
		pass

	@overload
	def hook_process( self : Window, process_id : int ) -> psutil.Process:
		'''Try hook the target process by its PID (process id)'''
		...

	@overload
	def hook_process( self : Window, process_name : str ) -> psutil.Process:
		'''Try hook the target process by its name.'''
		...

	def hook_process( self : Window, process_identifier : int | str ) -> None:
		if isinstance(process_identifier, int):
			self.process = ProcessUtility.find_by_pid(process_identifier)
		elif isinstance(process_identifier, str):
			self.process = ProcessUtility.find_by_name(process_identifier)
		else:
			raise ValueError('Can only attempt to hook processee by PID or Name.')

	def set_controller( self : Window, controller : ControllerInterface ) -> None:
		self.controller = controller

	def release_process( self ) -> None:
		self.process = None

	def is_process_hooked( self ) -> bool:
		return self.process is not None

if __name__ == '__main__':

	window = Window()

	try:
		window.hook_process('SummonersWar.exe')
	except NoProcessFound:
		print('Could not find the target process.')

	if not window.is_process_hooked():
		print('The target process could not be hooked.')
		exit()

	print('The target process has been hooked.')
