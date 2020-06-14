from collections import UserList
__version__ = '0.2.0'

from viewmask import utils  # noqa  # pylint: disable=unused-import


class Annotations(UserList):
    def __init__(self, initlist=()):
        UserList.__init__(self)
        if isinstance(initlist, Annotations):
            # Already deduped, copy without duplicate checking
            self.data[:] = Annotations.data
        else:
            self.extend(initlist)

    @classmethod
    def from_tcga(cls, xml_tree):
        """Extract contours from a TCGA XML annotations file.

        Parameters
        ----------
        xml_tree : xml.etree.ElementTree
            The XML tree of the TCGA annotations file.

        Returns
        -------
        contours : viewmask.Annotations
            A list of contours, where each contour is a 1-dimensional NumPy
            array of coordinate pairs, where each coordinate pair is a list
            with exactly 2 integers, representing the X and Y coordinates,
            respectively.
        """
        from numpy import array as to_numpy_array, int32 as npint32
        contours = [
            to_numpy_array(
                [[float(vertex.get("X")), float(vertex.get("Y"))]
                    for vertex in region],
                # np.int32 is necessary for cv2.drawContours
                dtype=npint32)
            for region in xml_tree.getroot().iter("Vertices")
        ]
        return cls(initlist=contours)

    @classmethod
    def from_qpdata(cls, filepath):
        pass

    @classmethod
    def from_asap(cls, xml_tree):
        """Extract contours from a TCGA XML annotations file.

        Parameters
        ----------
        xml_tree : xml.etree.ElementTree
            The XML tree of the ASAP annotations file.

        Returns
        -------
        contours : viewmask.Annotations
            A list of contours, where each contour is a 1-dimensional NumPy
            array of coordinate pairs, where each coordinate pair is a list
            with exactly 2 integers, representing the X and Y coordinates,
            respectively.
        """
        pass

    def export(self, mode):
        """Export the annotations to a usable format.

        Parameters
        ----------
        mode : {'napari', 'opencv'}
            If mode is 'napari', the annotations will be transposed over their
            main diagonal. This is done by reverting the x and y coordinates.
            If mode is 'opencv', the exported annotations will be unchanged.

        Returns
        -------
        contours : list of numpy.ndarray
            A list of contours, where each contour is a list of coordinates,
            where each coordinate is a list with exactly 2 integers,
            representing the X and Y coordinates, respectively.

        Notes
        -----
        The main diagonal is defined as the line that connects the top-left
        corner and the bottom right corner of an image.
        """
        if mode == 'napari':
            from numpy import flip
            return [flip(coordinate_pair) for coordinate_pair in self.data]
        elif mode == 'opencv':
            return self.data

    def as_image(self):
        """Convert an annotations object to an annotation mask.

        Returns
        -------
        rendered_annotations : numpy.ndarray
            A 3-dimensional NumPy array representing the RGB output image.
        """
        import numpy as np
        from cv2 import drawContours, fillPoly
        contours = self.export('opencv')
        x_max = np.amax([x for contour in contours for x, _ in contour])
        y_max = np.amax([y for contour in contours for _, y in contour])
        shape = (y_max, x_max, 3)
        rendered_annotations = np.zeros(shape, dtype=np.uint8)
        drawContours(rendered_annotations, contours, -1, [0, 255, 0])
        for contour in contours:
            fillPoly(
                rendered_annotations,
                np.array([contour], dtype=np.int32),
                [230, 230, 230]
            )
        return rendered_annotations

    def check(self, v):
        from numpy import ndarray
        if not isinstance(v, ndarray):
            raise TypeError(f'item is not of type {ndarray}')

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
    'utils.centers_of_contours',
    'utils.get_stroke_color',
    'utils.mask_to_contours',
    'utils.centers_to_image',
    'Annotations'
]
