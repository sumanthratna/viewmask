from collections import UserList
__version__ = '0.2.0'

from viewmask import utils  # noqa  # pylint: disable=unused-import


class AnnotationCoordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __eq__(self, other):
        return self.y == other.y and self.x == other.x

    def __repr__(self):
        return f"Coordinate ({self.x}, {self.y})"


class MaskContour(UserList):
    pass


class Annotations(UserList):
    def __init__(self, initlist=()):
        UserList.__init__(self)
        if isinstance(initlist, Annotations):
            # Already deduped, copy without duplicate checking
            self.data[:] = Annotations.data
        else:
            self.extend(initlist)

    def check(self, v):
        if not isinstance(v, MaskContour):
            raise TypeError(f'item is not of type {MaskContour}')

    def __add__(self, other):
        ret = self.__class__(self)  # Alt: self.copy()
        ret.extend(other)
        return ret

    def __setitem__(self, i, v):
        self.check(v)
        self.list[i] = v

    def insert(self, i, v):
        self.check(v)
        super().insert(i, v)

    def extend(self, other):
        for x in other:
            self.append(x)


__all__ = [
    'utils.file_to_dask_array',
    'utils.xml_to_contours',
    'utils.centers_of_contours',
    'utils.xml_to_image',
    'utils.get_stroke_color',
    'utils.mask_to_contours',
    'utils.centers_to_image',
    'AnnotationCoordinate',
    'MaskContour',
    'Annotations'
]
