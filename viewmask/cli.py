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

INTERACTIVE_OPTION_HELP = 'If passed, the annotations will be rendered as ' + \
    '`napari` objects rather than rendered together and displayed as an image.'

NAPARI_NOT_INSTALLED_WARNING = "The package `napari` is not installed. " + \
    "We recommend installing `napari`, which will enable viewing outputs " + \
    "in an interactive image viewer."


def validate_interactive_napari(ctx, param, value):
    # assert isinstance(value, bool)
    if value and napari is None:
        raise click.BadParameter(
            'The `interactive` flag cannot be passed '
            'without `napari` in the environment. Please install the `napari` '
            'package if you would like to use the `napari` interactive '
            'viewer.')


def validate_interactive_xml(ctx, param, value):
    # TODO: don't rely on filepath extension, actually check file contents
    _, annotations_ext = splitext(ctx.params['annotations'])
    annotations_are_xml = annotations_ext == '.xml'
    if value and not annotations_are_xml:
        raise click.BadParameter(
            "The `interactive` flag is only supported with XML annotations.")


class ComposedCallback:
    def __init__(self, *callbacks):
        self.callbacks = callbacks

    def __call__(self, ctx, param, value):
        output = None
        for callback in self.callbacks:
            output = callback(ctx, param, value)
        return output


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
    '-i',
    '--interactive',
    default=False,
    show_default=True,
    type=bool,
    is_flag=True,
    help=INTERACTIVE_OPTION_HELP,
    callback=ComposedCallback(
        validate_interactive_napari, validate_interactive_xml),
)
def view_annotations(annotations, interactive):
    if napari is None:
        return
    _, annotations_ext = splitext(annotations)

    with napari.gui_qt():
        viewer = napari.Viewer()
        if interactive:
            try:
                tree = ET.parse(annotations)
            except ET.ParseError:
                # TODO: don't just do nothing, some XMLs might actually be
                # unparseable
                pass
            from viewmask import Annotations
            annotations = Annotations.from_tcga(tree)
            annotations = regions.fit_spline()
            regions = annotations.export('napari')
            line_color = get_stroke_color(tree)
            viewer.add_shapes(
                regions,
                shape_type='path',
                edge_color=f"#{line_color}"
            )
            viewer.add_points(
                centers_of_contours(regions),
                name='centers'
            )
        else:
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
                annotations = Annotations.from_tcga(tree)
                annotations = annotations.fit_spline()
                rendered_annotations = annotations.as_image()
            else:
                # TODO: raise ValueError
                pass
            viewer.add_image(
                rendered_annotations,
                name='annotations',
                blending='additive',
                multiscale=False,
            )
            from cv2 import inRange as select_color, countNonZero
            mask = select_color(  # select pure blue
                rendered_annotations if isinstance(rendered_annotations,
                                                   np.ndarray) \
                else rendered_annotations.compute(),
                np.array([0, 0, 255]),
                np.array([0, 0, 255])
            )
            if countNonZero(mask) == 0:
                # TODO: it'd be nice if we could check this before computing
                # the blue-based nuclei mask. the current flow control seems
                # unintuitive
                mask = rendered_annotations
            centers = centers_of_contours(mask_to_contours(mask))
            viewer.add_image(
                centers_to_image(centers, shape=rendered_annotations.shape),
                name='centers',
                rgb=True,
                blending='additive',
                multiscale=False,
            )


@cli.command(name='image')
@click.argument('image', type=click.Path(exists=True, dir_okay=False))
def view_image(image):
    if napari is None:
        return
    da_img = file_to_dask_array(image)
    with napari.gui_qt():
        napari.view_image(da_img, name='image', multiscale=False)


@cli.command(name='overlay')
@click.argument('image', type=click.Path(exists=True, dir_okay=False))
@click.argument('annotations', type=click.Path(exists=True, dir_okay=False))
@click.option(
    '-i',
    '--interactive',
    default=False,
    show_default=True,
    type=bool,
    is_flag=True,
    help=INTERACTIVE_OPTION_HELP,
    callback=ComposedCallback(
        validate_interactive_napari, validate_interactive_xml),
)
def view_overlay(image, annotations, interactive):
    if napari is None:
        return
    annotations_ext = splitext(annotations)[1]

    da_img = file_to_dask_array(image)

    with napari.gui_qt():
        viewer = napari.Viewer()

        viewer.add_image(
            da_img,
            name='image',
            blending='additive',
            multiscale=False,
        )

        if interactive:
            try:
                tree = ET.parse(annotations)
            except ET.ParseError:
                # TODO: don't just do nothing, some XMLs might actually be
                # unparseable
                pass
            from viewmask import Annotations
            annotations = Annotations.from_tcga(tree)
            annotations = annotations.fit_spline()
            regions = annotations.export('napari')
            line_color = get_stroke_color(tree)
            viewer.add_shapes(
                regions,
                shape_type='path',
                edge_color=f"#{line_color}"
            )
            viewer.add_points(
                centers_of_contours(regions),
                name='centers'
            )
        else:
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
                from viewmask import Annotations
                annotations = Annotations.from_tcga(tree)
                annotations = annotations.fit_spline()
                rendered_annotations = annotations.as_image()
            else:
                # TODO: raise ValueError
                pass
            viewer.add_image(
                rendered_annotations,
                name='annotations',
                blending='additive',
                multiscale=False,
            )
            from cv2 import inRange as select_color, countNonZero
            mask = select_color(  # select pure blue
                rendered_annotations if isinstance(rendered_annotations,
                                                   np.ndarray) \
                else rendered_annotations.compute(),
                np.array([0, 0, 255]),
                np.array([0, 0, 255])
            )
            if countNonZero(mask) == 0:
                # TODO: it'd be nice if we could check this before computing
                # the blue-based nuclei mask. the current flow control seems
                # unintuitive
                mask = rendered_annotations
            centers = centers_of_contours(mask_to_contours(mask))
            viewer.add_image(
                centers_to_image(centers, shape=rendered_annotations.shape),
                name='centers',
                rgb=True,
                blending='additive',
                multiscale=False,
            )


if __name__ == '__main__':
    cli()
