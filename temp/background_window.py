
lParam = win32api.MAKELONG(x, y)
win32api.PostMessage(hWnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
win32api.PostMessage(hWnd, win32con.WM_LBUTTONUP, None, lParam)



def click(x, y):
	hWnd = win32gui.FindWindow(None, "BlueStacks")
	lParam = win32api.MAKELONG(x, y)

	hWnd1= win32gui.FindWindowEx(hWnd, None, None, None)
	win32gui.SendMessage(hWnd1, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
	win32gui.SendMessage(hWnd1, win32con.WM_LBUTTONUP, None, lParam)
click(100,100)


