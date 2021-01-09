#!/usr/bin/env python

import click
import xml.etree.ElementTree as ET
import numpy as np
from viewmask.utils import (
    file_to_dask_array,
    centers_of_contours,
    get_stroke_color,
    mask_to_contours,
    centers_to_image
)
from os.path import splitext
try:
    import napari
except ImportError:
    napari = None


NAPARI_NOT_INSTALLED_WARNING = "The package `napari` is not installed. " + \
    "We recommend installing `napari`, which will enable viewing outputs " + \
    "in an interactive image viewer."


def validate_interactive_napari(ctx, param, value):
    if value is None and napari is None:
        raise click.BadParameter(
            'The `interactive` flag cannot be passed '
            'without `napari` in the environment. Please install the `napari` '
            'package if you would like to use the `napari` interactive '
            'viewer.')
    return value


@click.group()
@click.version_option()
def cli():
    if napari is None:
        from warnings import warn
        warn(NAPARI_NOT_INSTALLED_WARNING)


@cli.command(name='annotations')
@click.argument(
    'annotations',
    type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    '-o',
    '--output',
    default=None,
    type=click.File(mode='wb'),
    callback=validate_interactive_napari,
)
def view_annotations(annotations, output):
    from viewmask import Annotations

    if output is None:  # interactive viewer
        try:
            tree = ET.parse(annotations)
        except ET.ParseError:
            # TODO: don't just do nothing, some XMLs might actually be
            # unparseable
            pass
        annotations_data = Annotations.from_tcga(tree)
        annotations_data = annotations_data.fit_spline()
        regions = annotations_data.export('napari')
        line_color = get_stroke_color(tree)

        with napari.gui_qt():
            viewer = napari.Viewer()
            viewer.add_shapes(
                regions,
                shape_type='path',
                edge_color=f"#{line_color}",
            )
            viewer.add_points(
                centers_of_contours(regions),
                name='centers',
            )
    else:
        _, annotations_ext = splitext(annotations)
        if annotations_ext == '.npy':
            rendered_annotations = np.load(annotations)
        elif annotations_ext == '.png':
            from dask.array import squeeze
            rendered_annotations = squeeze(file_to_dask_array(annotations))
        elif annotations_ext == '.xml':
            try:
                tree = ET.parse(annotations)
            except ET.ParseError:
                # TODO: don't just do nothing, some XMLs might actually be
                # unparseable
                pass
            annotations_data = Annotations.from_tcga(tree)
            annotations_data = annotations_data.fit_spline()
            rendered_annotations = annotations_data.as_image()
        else:
            # TODO: raise ValueError
            pass

        from cv2 import inRange as select_color, countNonZero
        pure_blue = np.asarray([0, 0, 255])
        mask = select_color(  # select pure blue
            rendered_annotations,
            pure_blue,
            pure_blue,
        )
        if countNonZero(mask) == 0:  # if all black
            # TODO: it'd be nice if we could check this before computing
            # the blue-based nuclei mask. the current flow control seems
            # unintuitive
            mask = rendered_annotations

        centers = centers_of_contours(annotations_data.export('opencv'))
        # TODO: white pixels over-write red pixels so centers can't be seen
        rendered_annotations += centers_to_image(
            centers, shape=rendered_annotations.shape)

        from PIL.Image import fromarray as array_to_pil_image
        array_to_pil_image(rendered_annotations).save(output)


@cli.command(name='image')
@click.argument('image', type=click.Path(exists=True, dir_okay=False))
def view_image(image):
    if napari is None:
        raise click.UsageError("The `image` command cannot be used without "
                               "the `napari` package installed.")
    da_img = file_to_dask_array(image)
    with napari.gui_qt():
        napari.view_image(da_img, name='image', multiscale=False)


@cli.command(name='overlay')
@click.argument('image', type=click.Path(exists=True, dir_okay=False))
@click.argument('annotations', type=click.Path(exists=True, dir_okay=False))
@click.option(
    '-o',
    '--output',
    default=None,
    type=click.File(mode='wb'),
    callback=validate_interactive_napari,
)
def view_annotations(image, annotations, output):
    from dask.array import squeeze
    from viewmask import Annotations

    da_img = squeeze(file_to_dask_array(image))

    if output is None:  # interactive viewer
        try:
            tree = ET.parse(annotations)
        except ET.ParseError:
            # TODO: don't just do nothing, some XMLs might actually be
            # unparseable
            pass
        annotations_data = Annotations.from_tcga(tree)
        annotations_data = annotations_data.fit_spline()
        regions = annotations_data.export('napari')
        line_color = get_stroke_color(tree)

        with napari.gui_qt():
            viewer = napari.Viewer()
            viewer.add_image(
                da_img,
                name='image',
                blending='additive',
                multiscale=False,
            )
            viewer.add_shapes(
                regions,
                shape_type='path',
                edge_color=f"#{line_color}",
            )
            viewer.add_points(
                centers_of_contours(regions),
                name='centers',
            )
    else:
        rendered_annotations = da_img

        _, annotations_ext = splitext(annotations)
        if annotations_ext == '.npy':
            rendered_annotations += np.load(annotations)
        elif annotations_ext == '.png':
            rendered_annotations += squeeze(file_to_dask_array(annotations))
        elif annotations_ext == '.xml':
            try:
                tree = ET.parse(annotations)
            except ET.ParseError:
                # TODO: don't just do nothing, some XMLs might actually be
                # unparseable
                pass
            annotations_data = Annotations.from_tcga(tree)
            annotations_data = annotations_data.fit_spline()
            rendered_annotations += annotations_data.as_image()
        else:
            # TODO: raise ValueError
            pass

        from cv2 import inRange as select_color
        from dask.array import asarray as as_da_array, from_delayed as delayed_to_da, count_nonzero
        from dask import delayed
        pure_blue = as_da_array((0, 0, 255))
        mask = delayed_to_da(delayed(select_color, pure=True)(  # select pure blue
            rendered_annotations,
            pure_blue,
            pure_blue,
        ), rendered_annotations.shape[:2], dtype=int)
        if count_nonzero(mask) == 0:  # if no blue
            # TODO: it'd be nice if we could check this before computing
            # the blue-based nuclei mask. the current flow control seems
            # unintuitive
            mask = rendered_annotations

        centers = centers_of_contours(annotations_data.export('opencv'))
        # TODO: displays bright green heatmap instead of mask
        rendered_annotations += centers_to_image(
            centers, shape=rendered_annotations.shape)

        from PIL.Image import fromarray as array_to_pil_image
        array_to_pil_image(rendered_annotations.compute()).save(output)


if __name__ == '__main__':
    cli()
