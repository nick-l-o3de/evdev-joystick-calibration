import json


class MinMaxItem:
    def __init__(self, analog, minimum, maximum, flat):
        self.minimum = int(minimum)
        self.maximum = int(maximum)
        self.analog = analog
        self.flat = flat # flat aka deadzone

    def __str__(self):
        return "analog: " + self.analog + " min:" + str(self.minimum) + " max:" + str(self.maximum) + " flat:" + str(self.flat)


class MinMaxItemEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def object_decoder(obj):
    if 'analog' in obj:
        return MinMaxItem(obj['analog'], obj['minimum'], obj['maximum'], obj['flat'])
    return obj
