import cv2
import numpy as np


def xml_to_contours(xml_tree, contour_drawer):
    """Extract contours from a TCGA XML annotations file.

    Parameters
    ----------
    xml_tree : xml.etree.ElementTree
        The XML tree of the TCGA annotations file.
    contour_drawer : {'napari', 'cv2'}
        If `contour_drawer` is `'napari'` then the contours will be transposed
        over its main diagonal. When `contour_drawer` is `'cv2'`, no changes
        will be made to the returned contours.

    Returns
    -------
    contours : list of numpy.ndarray
        A list of contours, where each contour is a list of coordinates,
        where each coordinate is a list with exactly 2 integers, representing
        the X and Y coordinates, respectively.

    Notes
    -----
    The main diagonal is defined as the line that connects the top-left corner
    and the bottom right corner.
    """
    if contour_drawer not in ['napari', 'cv2']:
        raise ValueError("contour_drawer must be 'cv2' or 'napari'")
    root = xml_tree.getroot()
    contours = []
    for region in root.iter("Vertices"):
        coords = []
        for vertex in region:
            if contour_drawer == 'napari':
                # convert each coordinate to (y, x) to transpose
                coords.append(
                    [float(vertex.get("Y")), float(vertex.get("X"))])
            else:  # contour_drawer is 'cv2'
                coords.append(
                    [float(vertex.get("X")), float(vertex.get("Y"))])
        # int32 dtype is necessary for cv2.drawContours
        contour = np.array(coords, dtype=np.int32)
        contours.append(contour)
    return contours


def centers_of_contours(contours):
    """Return the centers of a list of OpenCV contours.

    Parameters
    ----------
    contours : list of numpy.ndarray
        A list of cv2 contours; each contour's center will be calculated. Each
        contour is a list with 1 element, which is a list with 2 elements,
        representing the X and Y coordinates as integers, respectively.

    Returns
    -------
    centers : list of tuple of int
        A list of coordinates, where each coordinate is a tuple with exactly 2
        ints, representing the X and Y coordinates, respectively. Each
        coordinate represents the center of the corresponding contour in
        `contours`. In this method, the center is defined as the centroid of
        the contour.
    """
    centers = []
    for contour in contours:
        # centroid of contour:
        M = cv2.moments(contour)
        center_x = int(M["m10"] / M["m00"])
        center_y = int(M["m01"] / M["m00"])
        centers.append((center_x, center_y))
    return centers


# TODO: remove default for shape,
# instead guess image based on min/max coordinates
def xml_to_image(xml_tree, shape=(1000, 1000, 3)):
    """Convert a TCGA annotations file to a binary mask.

    Parameters
    ----------
    xml_tree : xml.etree.ElementTree
        The XML tree of the TCGA annotations file.
    shape : tuple of int, optional
        The shape of the mask. `shape` defaults to `(1000, 1000, 3)`, since
        most images in the TCGA dataset have a height and width of 1000 pixels
        and have 3 channels (red, green, and blue).

    Returns
    -------
    rendered_annotations : numpy.ndarray
        An N-dimensional NumPy array representing the RGB output image with the
        shape defined as `shape`.
    """
    contours = xml_to_contours(xml_tree, 'cv2')
    rendered_annotations = np.zeros(shape, dtype=np.uint8)
    cv2.drawContours(rendered_annotations, contours, -1, [0, 255, 0])
    for contour in contours:
        cv2.fillPoly(rendered_annotations, np.array(
            [contour], dtype=np.int32), [230, 230, 230])
    return rendered_annotations


def get_stroke_color(xml_tree):
    """Determine the line color for annotations from a TCGA annotations file.

    Parameters
    ----------
    xml_tree : xml.etree.ElementTree
        The XML tree of the TCGA annotations file.

    Returns
    -------
    line_color : str
        A string representing the proper hex code to use for the stroke color.
        The output is always 6 characters and does not include the hashtag.
    """
    # TODO: verify that the output actually is always 6 characters
    decimal_color = xml_tree.find('./Annotation').attrib['LineColor']
    line_color = hex(int(decimal_color)).replace('0x', '').zfill(6)
    return line_color


def mask_to_contours(mask):
    """Determine the line color for annotations from a TCGA annotations file.

    Parameters
    ----------
    mask : numpy.ndarray
        A NumPy N-dimensional array representing the image. If `mask` has 3
        dimensions, the image is assumed to be RGB, and will be converted to
        grayscale. If `mask` only has 2 dimensions, the image is assumed to be
        grayscale. The values in the input should be in the range [0, 255].

    Returns
    -------
    contours : list of numpy.ndarray
        A list of contours, where each contour is a list of coordinates, where
        each coordinate is a list of a list of X and Y integers.
    """
    if mask.ndim == 3:
        if mask.shape[2] == 3:
            graymask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
        else:
            raise ValueError("If mask has 3 dimensions, it must be RGB.")
    elif mask.ndim == 2:
        graymask = np.uint8(mask)
    else:
        raise ValueError("mask must be 2-D or 3-D.")

    contours, _ = cv2.findContours(
        graymask,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_NONE
    )
    return contours


def centers_to_image(centers, shape=(1000, 1000, 3), radius=4):
    """Determine the line color for annotations from a TCGA annotations file.

    Parameters
    ----------
    centers : list of tuple of int
        A list of coordinates, where each coordinate is a tuple with exactly 2
        ints, representing the X and Y coordinates, respectively. Each
        coordinate represents the center of the corresponding contour in
        `contours`.
    shape : tuple of int, optional
        The shape of the mask. `shape` defaults to `(1000, 1000, 3)`, since
        most images in the TCGA dataset have a height and width of 1000 pixels
        and have 3 channels (red, green, and blue). If `shape` provides a 3rd
        value with value 3, the centers will be drawn in red; otherwise, if
        shape has only 2 values, the centers will be drawn in white.
    radius : int, optional
        The radius of each center, defaults to `4`.

    Returns
    -------
    rendered_annotations : numpy.ndarray
        An N-dimensional NumPy array representing the RGB output image with the
        shape defined as `shape`.async
    """
    rendered_annotations = np.zeros(shape, dtype=np.uint8)
    if rendered_annotations.ndim == 3:
        if rendered_annotations.shape[2] == 3:
            write_color = [255, 0, 0]
        else:
            raise ValueError(
                "If shape has length 3, the 3rd value must be 3 for RGB.")
    elif rendered_annotations.ndim == 2:
        write_color = 255
    else:
        raise ValueError("shape must have length 2 or 3.")

    for center in centers:
        cv2.circle(rendered_annotations, center, radius, write_color, -1)
    return rendered_annotations
