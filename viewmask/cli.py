#!/usr/bin/env python

import click
import napari
import xml.etree.ElementTree as ET
import numpy as np
from viewmask.utils import (
    file_to_dask_array,
    xml_to_contours,
    centers_of_contours,
    xml_to_image,
    get_stroke_color,
    mask_to_contours,
    centers_to_image
)
from os.path import splitext


# TODO: eventually napari will rename is_pyramid to multiscale:
# https://github.com/napari/napari/commit/1adff3e467768076643e8e02a12d4bf726f563a9

INTERACTIVE_OPTION_HELP = 'If passed, the annotations will be rendered as ' + \
    'napari objects rather than rendered together and displayed as an image.'


@click.group()
def cli():
    pass


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
    help=INTERACTIVE_OPTION_HELP
)
def view_annotations(annotations, interactive):
    if splitext(annotations)[1] == '.npy' and interactive is True:
        raise ValueError(
            "The interactive flag cannot be passed with a numpy mask.")

    # TODO: get rid of this, some XMLs might actually be unparseable:
    try:
        tree = ET.parse(annotations)
    except ET.ParseError:
        pass
    with napari.gui_qt():
        viewer = napari.Viewer()
        if interactive:
            regions = xml_to_contours(tree, 'napari')
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
            if splitext(annotations)[1] == '.npy':
                rendered_annotations = np.load(annotations)
                viewer.add_image(
                    rendered_annotations,
                    name='annotations',
                    blending='additive',
                    is_pyramid=False,
                )
            else:
                rendered_annotations = xml_to_image(tree)
                viewer.add_image(
                    rendered_annotations,
                    name='annotations',
                    blending='additive',
                    is_pyramid=False,
                )
            centers = centers_of_contours(
                mask_to_contours(rendered_annotations))
            viewer.add_image(
                centers_to_image(centers),
                name='centers',
                rgb=True,
                blending='additive',
                is_pyramid=False,
            )


@cli.command(name='image')
@click.argument('image', type=click.Path(exists=True, dir_okay=False))
def view_image(image):
    da_img = file_to_dask_array(image)
    with napari.gui_qt():
        _ = napari.view_image(da_img, name='image', is_pyramid=False)


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
    help=INTERACTIVE_OPTION_HELP
)
def view_overlay(image, annotations, interactive):
    # TODO: use assert?
    # TODO: use annotations.endswith('.npy')?
    if splitext(annotations)[1] == '.npy' and interactive is True:
        raise ValueError(
            "The interactive flag cannot be passed with a numpy mask.")

    da_img = file_to_dask_array(image)

    with napari.gui_qt():
        viewer = napari.Viewer()

        viewer.add_image(
            da_img,
            name='image',
            blending='additive',
            is_pyramid=False,
        )

        if interactive:
            tree = ET.parse(annotations)
            regions = xml_to_contours(tree, 'napari')
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
            if splitext(annotations)[1] == '.npy':
                rendered_annotations = np.load(annotations)
                viewer.add_image(
                    rendered_annotations,
                    name='annotations',
                    blending='additive',
                    is_pyramid=False,
                )
            else:
                tree = ET.parse(annotations)
                rendered_annotations = xml_to_image(tree)
                viewer.add_image(
                    rendered_annotations,
                    name='annotations',
                    blending='additive',
                    is_pyramid=False,
                )
            centers = centers_of_contours(
                mask_to_contours(rendered_annotations))
            viewer.add_image(
                centers_to_image(centers),
                name='centers',
                rgb=True,
                blending='additive',
                is_pyramid=False,
            )


if __name__ == '__main__':
    cli()
