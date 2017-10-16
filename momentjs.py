from datetime import datetime,timedelta
class momentjs(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def dist8(self):
        timenow = (self.timestamp + timedelta(hours=8))
        return timenow.strftime("%Y/%m/%d/%H:%M")