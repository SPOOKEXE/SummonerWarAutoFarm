
from __future__ import annotations
from typing import overload

import psutil

class Window:

	@overload
	def __init__(self, process_name : str) -> Window:
		raise NotImplementedError

	@overload
	def __init__(self, process_id : int) -> Window:
		raise NotImplementedError

	@overload
	def attempt_hook( self, process_name : str ) -> None:
		raise NotImplementedError

	@overload
	def attempt_hook( self, process_name : str ) -> None:
		raise NotImplementedError

class SummonersWar(Window):

	def __init__(self) -> SummonersWar:
		super().__init__('SummonersWar.exe')

print(psutil.process_iter())
