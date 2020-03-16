#!/usr/bin/env python

import click
import napari
import xml.etree.ElementTree as ET
from PIL import Image
import numpy as np
from viewmask.utils import xml_to_contours, centers_of_contours, xml_to_image
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
            decimal_color = tree.find('./Annotation').attrib['LineColor']
            line_color = hex(int(decimal_color)).replace('0x', '').zfill(6)
            viewer.add_shapes(
                regions, shape_type='path', edge_color=f"#{line_color}")
            viewer.add_points(centers_of_contours(regions))
        else:
            if splitext(annotations)[1] == '.npy':
                rendered_annotations = np.load(annotations)
            else:
                rendered_annotations = xml_to_image(tree)
            viewer.add_image(
                rendered_annotations,
                name='annotations',
                is_pyramid=False
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

    # TODO: get rid of this, some XMLs might actually be unparseable:
    try:
        tree = ET.parse(annotations)
    except ET.ParseError:
        pass
    with napari.gui_qt():
        viewer = napari.Viewer()
        if splitext(image)[1] == '.npy':
            np_img = np.load(image)
        else:
            np_img = np.array(Image.open(image))
        viewer.add_image(np_img, name='image')

        if interactive:
            regions = xml_to_contours(tree, 'napari')
            decimal_color = tree.find('./Annotation').attrib['LineColor']
            line_color = hex(int(decimal_color)).replace('0x', '').zfill(6)
            viewer.add_shapes(
                regions, shape_type='path', edge_color=f"#{line_color}")
            viewer.add_points(centers_of_contours(regions))
        else:
            if splitext(annotations)[1] == '.npy':
                rendered_annotations = np.load(annotations)
            else:
                rendered_annotations = xml_to_image(tree, shape=np_img.shape)
            viewer.add_image(
                rendered_annotations,
                name='annotations',
                is_pyramid=False
            )


if __name__ == '__main__':
    cli()
