class DataSeries:
    def __init__(self, ys, xs=None):
        self._ys = ys
        if xs is None:
            self._xs = range(len(ys))
        else:
            if len(xs) != len(ys):
                raise ValueError('Length of xs must match length of ys')
            self._xs = xs

    @property
    def zipped(self):
        return zip(self._xs, self._ys)
