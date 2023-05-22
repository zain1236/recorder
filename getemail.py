import os
import ctypes

def get_logged_in_user_email():
    try:
        domain = os.environ['USERDOMAIN']
        username = os.environ['USERNAME']
        size = ctypes.c_ulong(0)
        ctypes.windll.kernel32.GetComputerNameExW(5, None, ctypes.byref(size))
        buffer = ctypes.create_unicode_buffer(size.value)
        ctypes.windll.kernel32.GetComputerNameExW(5, buffer, ctypes.byref(size))
        email = f"{username}@{buffer.value}"
        return email
    except Exception as e:
        print(f"Error: {e}")
        return None
#
# user_email = get_logged_in_user_email()
# print(f"User email: {user_email}")

