import winreg


def get_registry_key_value(key, key_value, name):
    """
    Windows Registry Key의 특정 값을 가져옴
    :param key: 'HKEY_CURRENT_USER'
    :param key_value: 'Control Panel\\Desktop'
    :param name: 'WheelScrollLines'
    :return: list
    """
    try:
        key = getattr(winreg, key)
        value = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
        ret = winreg.QueryValueEx(value, name)
        return ret
    except Exception as e:
        return list()

