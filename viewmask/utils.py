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
    >>> npa_img = arr.compute()  # convert the dask array to a numpy array
    >>> pil_img = Image.fromarray(cv2.resize(
    ...     npa_img,
    ...     dsize=(1440, 700),
    ...     interpolation=cv2.INTER_CUBIC
    ... ))
    >>> pil_img.save(test_image_name)
    """
    if path.endswith('.npy'):
        import dask.array as da

        return da.from_array(np.load(path))
    else:
        import openslide

        img = openslide.open_slide(path)
        if isinstance(img, openslide.OpenSlide):
            from openslide import deepzoom
            import dask.array as da
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
                tile = gen.get_tile(level, (column, row))  # PIL.Image
                return da.transpose(
                    da.from_array(np.array(tile)),
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
    import dask.array as da
    if isinstance(mask, da.Array):
        mask = mask.compute()  # convert to numpy array
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


def centers_to_image(centers, radius=4, write_color=[255, 0, 0], shape=None):
    """Draw coordinates of centers to a static image.

    Parameters
    ----------
    centers : list of tuple of int
        A list of coordinates, where each coordinate is a tuple with exactly 2
        ints, representing the X and Y coordinates, respectively. Each
        coordinate represents the center of the corresponding contour in
        `contours`.
    radius : int, optional
        The radius of each center, defaults to `4`.
    write_color : array_like of int, optional
        The RGB color that should be used to draw the centers, defaults to
        [255, 0, 0], which is red. `write_color` have a length of 3; each
        integer represents red, green, and blue, respectively.
    shape : tuple of int, optional
        The shape of the output image. Defaults to (x_max, y_max, 3), where
        x_max are the maximum x-coordinate and y-coordinate, respectively, of
        the centers.

    Returns
    -------
    rendered_annotations : numpy.ndarray
        An N-dimensional NumPy array representing the RGB output image with the
        shape defined as `shape`.
    """
    if shape is None:
        x_max = np.amax([x for x, _ in centers])
        y_max = np.amax([y for _, y in centers])
        shape = (y_max, x_max, 3)
    rendered_annotations = np.zeros(shape, dtype=np.uint8)
    for center in centers:
        cv2.circle(rendered_annotations, center, radius, write_color, -1)
    return rendered_annotations


def split_dask_array_by_colors(arr):
    # TODO: this is currently used in viewmask. remove this?
    import dask.array as da
    # this is equivalent to cv2.split, but cv2.split is slow.
    # https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_core/py_basic_ops/py_basic_ops.html#:~:text=cv2.split()%20is%20a%20costly%20operation%20(in%20terms%20of%20time),%20so%20only%20use%20it%20if%20necessary.%20Numpy%20indexing%20is%20much%20more%20efficient%20and%20should%20be%20used%20if%20possible.
    # https://answers.opencv.org/question/3754/how-to-split-cv2imread-to-3-separate-mats/?answer=3757#post-id-3757
    channel_r, channel_g, channel_b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    red_img = da.moveaxis(da.stack([
        channel_r, da.zeros_like(channel_r), da.zeros_like(channel_r)
    ]), 0, -1)
    green_img = da.moveaxis(da.stack([
        da.zeros_like(channel_g), channel_g, da.zeros_like(channel_g)
    ]), 0, -1)
    blue_img = da.moveaxis(da.stack([
        da.zeros_like(channel_b), da.zeros_like(channel_b), channel_b
    ]), 0, -1)
    return red_img, green_img, blue_img


def get_hematoxylin(rgb):
    """Extract the hematoxylin layer from an RGB image.

    Parameters
    ----------
    rgb : (..., 3) array_like
        The RGB input image to process.

    Returns
    -------
    arr_hema : ndarray
        A 2-dimensional array representing the hematoxylin
        intensity.

    Raises
    ------
    ValueError
        If `rgb` is not at least 2-D with shape (..., 3).

    References
    ----------
    .. [1] A. C. Ruifrok and D. A. Johnston, "Quantification of histochemical
           staining by color deconvolution.," Analytical and quantitative
           cytology and histology / the International Academy of Cytology [and]
           American Society of Cytology, vol. 23, no. 4, pp. 291-9, Aug. 2001.

    Examples
    --------
    >>> from skimage import data
    >>> from viewmask.utils import get_hematoxylin
    >>> rgb = data.immunohistochemistry()
    >>> he_layer = get_hematoxylin(rgb)
    """
    from skimage.color import rgb2hed

    # matplotlib navy is (22, 0, 134), vispy navy is (0, 0, 128)
    # cmap_hema = Colormap(['white', 'navy'])

    # matplotlib saddlebrown is (144, 66, 0), vispy saddlebrown is (139, 69, 19)
    # cmap_dab = Colormap(['white', 'saddlebrown'])

    # matplotlib darkviolet is (166, 0, 218), vispy darkviolet is (148, 0, 211)
    # cmap_eosin = Colormap(['darkviolet', 'white'])

    ihc_hed = rgb2hed(rgb)
    arr_hema = ihc_hed[:, :, 0]
    return arr_hema


def fit_spline_to_points(points):
    """Fits a B-spline through a sequence of points.

    Parameters
    ----------
    points : numpy.ndarray
        A list of sample vector arrays representing the curve.

    Returns
    -------
    spline_points : numpy.ndarray
        An N-dimensional NumPy array representing the RGB output image with the
        shape defined as `shape`.
    """
    # https://pathflowinterns.slack.com/archives/DTLUTM8NS/p1597243698287400
    # TODO: are the docstrings/types correct?
    from scipy.interpolate import splprep, splev
    tck, u = splprep(points.T, u=None, s=0.0, per=1)
    u_new = np.linspace(u.min(), u.max(), 1000)
    x_new, y_new = splev(u_new, tck, der=0)
    spline_points = np.vstack((x_new, y_new)).T
    return spline_points
