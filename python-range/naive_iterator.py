

class NaiveIterator:
    def __init__(self, sequence):
        self._pos = 0
        self._seq = sequence

    def next(self):
        pos = self._pos
        self._pos += 1
        return self._seq[pos]

