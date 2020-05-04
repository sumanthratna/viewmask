import cv2
import numpy as np


# https://github.com/jlevy44/PathFlowAI/blob/888f0867eeed4e1265cafed9b9f0f42bebd6a6ae/pathflowai/utils.py#L86-L129
def file_to_dask_array(
    path,
    tile_size=1000,
    overlap=0,
    remove_last=True,
    allow_unknown_chunksizes=False
):
    """Load an image to a dask array.

    Parameters
    ----------
    path : str
        The path to the image file as a string.
    tile_size : int, optional
        Size of chunk to be read in.
    overlap : int, optional
        Do not modify, overlap between neighboring tiles.
    remove_last : bool, optional
        Remove last tile because it has a custom size.
    allow_unknown_chunksizes : bool, optional
        Allow different chunk sizes, more flexible, but slowdown.

    Returns
    -------
    arr : dask.array.Array
        A Dask Array representing the contents of the image file.

    Examples
    --------
    >>> da_img = file_to_dask_array(path)
    >>> npa_img = arr.compute()  # convert from dask array to numpy array
    >>> pil_img = to_pil(cv2.resize(
    ...     npa_img,
    ...     dsize=(1440, 700),
    ...     interpolation=cv2.INTER_CUBIC
    ... ))
    >>> pil_img.save(test_image_name)
    """
    if path.endswith('.npy'):
        import dask.array as da

        da.from_array(np.load(path))
    else:
        import openslide
        import dask.array as da

        img = openslide.open_slide(path)
        # TODO: use isinstance
        if isinstance(img, openslide.OpenSlide):
            from openslide import deepzoom
            import dask.delayed

            gen = deepzoom.DeepZoomGenerator(
                img,
                tile_size=tile_size,
                overlap=overlap,
                limit_bounds=True
            )
            max_level = len(gen.level_dimensions) - 1
            n_tiles_x, n_tiles_y = gen.level_tiles[max_level]

            @dask.delayed(pure=True)
            def get_tile(level, column, row):
                tile = gen.get_tile(level, (column, row))
                return dask.array.transpose(
                    dask.array.from_array(np.array(tile)),
                    axes=(1, 0, 2)
                )

            sample_tile_shape = get_tile(max_level, 0, 0).shape.compute()
            rows = range(n_tiles_y - (0 if not remove_last else 1))
            cols = range(n_tiles_x - (0 if not remove_last else 1))
            tiles = [da.concatenate(
                [da.from_delayed(
                    get_tile(max_level, col, row),
                    sample_tile_shape,
                    np.uint8
                ) for row in rows],
                allow_unknown_chunksizes=allow_unknown_chunksizes,
                axis=1
            ) for col in cols]
            arr = da.concatenate(
                tiles,
                allow_unknown_chunksizes=allow_unknown_chunksizes
            ).transpose([1, 0, 2])
            return arr
        else:  # img is instance of openslide.ImageSlide
            import dask_image.imread

            return dask_image.imread.imread(path)


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
                coords.append([
                    float(vertex.get("Y")),
                    float(vertex.get("X"))
                ])
            else:  # contour_drawer == 'cv2'
                coords.append([
                    float(vertex.get("X")),
                    float(vertex.get("Y"))
                ])
        # np.int32 is necessary for cv2.drawContours
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
        the contour. If the centroid cannot be calculated, the circumcenter of
        the center is used.
    """
    centers = []
    for contour in contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            # centroid of contour:
            center_x = M["m10"] / M["m00"]
            center_y = M["m01"] / M["m00"]
        else:
            # circumcenter of contour:
            (center_x, center_y), _ = cv2.minEnclosingCircle(contour)
        centers.append((int(center_x), int(center_y)))
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
        cv2.fillPoly(
            rendered_annotations,
            np.array([contour], dtype=np.int32),
            [230, 230, 230]
        )
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
        shape defined as `shape`.
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
