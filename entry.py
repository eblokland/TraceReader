from enum import Enum, auto


class LogType(Enum):
    DISPLAY_STATE = 'displaystate'
    VOLTAGE = 'voltage'
    BRIGHTNESS = 'dispbrightness'
    WIFI_STR = 'wifi'
    CURRENT = 'current'
    WIFI_ROAM = 'wifiroam'
    CELL_STR = 'cellular'


def parse_line(line: str):
    split = line.strip().split(sep=' ')
    logtype = split[1].lower()
    if logtype == LogType.DISPLAY_STATE.value:
        return DisplayState(split)
    elif logtype == LogType.VOLTAGE.value:
        return Voltage(split)
    elif logtype == LogType.BRIGHTNESS.value:
        return Brightness(split)
    elif logtype == LogType.WIFI_STR.value:
        return WifiStrength(split)
    elif logtype == LogType.CURRENT.value:
        return Current(split)
    elif logtype == LogType.WIFI_ROAM.value:
        return WifiRoam(split)
    elif logtype == LogType.CELL_STR.value:
        return CellStrength(split)
    else:
        print('unexpected line, got ' + line)


class Entry(object):
    def __init__(self, line):
        self.timestamp = line[0]
        self.logtype = line[1]
        self.data = line[2]

    def __str__(self):
        return 'Time: ' + str(self.timestamp) + ' Type: ' + str(self.logtype) + 'Data: ' + str(self.data)


class DisplayState(Entry):
    def __init__(self, line):
        Entry.__init__(self, line)
        # yes we just change self.data here, whatever
        self.data = line[3]
        self.displayNum = line[2]
        self.logtype = line[1]


class Voltage(Entry):
    def get_volts(self):
        return float(self.data) / 1000.0


class Current(Entry):
    def get_amps(self):
        return float(self.data) / 1000000.0


class WifiStrength(Entry):
    pass


class Brightness(Entry):
    pass


class CellStrength(Entry):
    pass


class WifiRoam(Entry):
    pass


class Power(Entry):
    def __init__(self, voltage: Voltage, current: Current):
        self.timestamp = voltage.timestamp if voltage.timestamp > current.timestamp else current.timestamp
        self.data = voltage.get_volts() * current.get_amps()  # gives Watts
        self.logtype = 'Power'
