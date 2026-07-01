import ctypes
import ctypes.util
import os
import platform


_x_error_handler_ref = None


def _abaikan_badwindow_x11():
    global _x_error_handler_ref

    if platform.system() != "Linux" or not os.environ.get("DISPLAY"):
        return

    libx11_path = ctypes.util.find_library("X11")
    if not libx11_path:
        return

    try:
        libx11 = ctypes.CDLL(libx11_path)
        handler_type = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)

        def _handler(_display, _error_event):
            return 0

        _x_error_handler_ref = handler_type(_handler)
        libx11.XSetErrorHandler(_x_error_handler_ref)
    except Exception:
        _x_error_handler_ref = None


_abaikan_badwindow_x11()

from ui.jendela_utama import JendelaUtama

if __name__ == "__main__":
    aplikasi = JendelaUtama()
    aplikasi.mainloop()
