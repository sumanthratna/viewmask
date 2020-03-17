#!/usr/bin/env python

import click
import napari
import xml.etree.ElementTree as ET
from PIL import Image
import numpy as np
from viewmask.utils import (xml_to_contours,
                            centers_of_contours,
                            xml_to_image,
                            get_stroke_color,
                            mask_to_contours,
                            centers_to_image)
from os.path import splitext


@click.group()
def cli():
    pass


@cli.command()
@click.argument('annotations', type=click.Path(exists=True, dir_okay=False))
@click.option(
    '-i',
    '--interactive',
    default=False,
    show_default=True,
    type=bool,
    is_flag=True
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
                    is_pyramid=False
                )
            else:
                rendered_annotations = xml_to_image(tree)
                viewer.add_image(
                    rendered_annotations,
                    name='annotations',
                    is_pyramid=False
                )
            centers = centers_of_contours(
                mask_to_contours(rendered_annotations))
            viewer.add_image(
                centers_to_image(centers),
                name='centers',
                rgb=True
            )


@cli.command()
@click.argument('image', type=click.Path(exists=True, dir_okay=False))
def view_image(image):
    with napari.gui_qt():
        if splitext(image)[1] == '.npy':
            np_img = np.load(image)
        else:
            np_img = np.array(Image.open(image))
        _ = napari.view_image(np_img, name='image')


@cli.command()
@click.argument('image', type=click.Path(exists=True, dir_okay=False))
@click.argument('annotations', type=click.Path(exists=True, dir_okay=False))
@click.option(
    '-i',
    '--interactive',
    default=False,
    show_default=True,
    type=bool,
    is_flag=True
)
def view_overlay(image, annotations, interactive):
    if splitext(annotations)[1] == '.npy' and interactive is True:
        raise ValueError(
            "The interactive flag cannot be passed with a numpy mask.")

    with napari.gui_qt():
        viewer = napari.Viewer()
        if splitext(image)[1] == '.npy':
            np_img = np.load(image)
        else:
            np_img = np.array(Image.open(image))
        viewer.add_image(np_img, name='image')

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
                    is_pyramid=False
                )
            else:
                tree = ET.parse(annotations)
                rendered_annotations = xml_to_image(tree)
                viewer.add_image(
                    rendered_annotations,
                    name='annotations',
                    is_pyramid=False
                )
            centers = centers_of_contours(
                mask_to_contours(rendered_annotations))
            viewer.add_image(
                centers_to_image(centers),
                name='centers',
                rgb=True
            )


if __name__ == '__main__':
    cli()
