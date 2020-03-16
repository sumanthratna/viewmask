#!/usr/bin/env python

import click
import napari
import xml.etree.ElementTree as ET
from PIL import Image
import numpy as np
from viewmask.utils import xml_to_contours, centers_of_contours, xml_to_image


@click.group()
def cli():
    pass


@cli.command()
@click.argument('annotations', type=click.Path(exists=True, dir_okay=False))
@click.option('-i', '--interactive', default=False, show_default=True, type=bool, is_flag=True)
def view_annotations(annotations, interactive):
    tree = ET.parse(annotations)
    with napari.gui_qt():
        viewer = napari.Viewer()
        tree = ET.parse(annotations)
        if interactive:
            regions = xml_to_contours(tree, 'napari')
            decimal_color = tree.find('./Annotation').attrib['LineColor']
            line_color = hex(int(decimal_color)).replace('0x', '').zfill(6)
            viewer.add_shapes(
                regions, shape_type='path', edge_color=f"#{line_color}")
            viewer.add_points(centers_of_contours(regions))
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
        _ = napari.view_image(np.asarray(Image.open(image)), name='image')


@cli.command()
@click.argument('image', type=click.Path(exists=True, dir_okay=False))
@click.argument('annotations', type=click.Path(exists=True, dir_okay=False))
@click.option('-i', '--interactive', default=False, show_default=True, type=bool, is_flag=True)
def view_overlay(image, annotations, interactive):
    with napari.gui_qt():
        viewer = napari.Viewer()
        np_img = np.array(Image.open(image))
        viewer.add_image(np_img, name='image')

        tree = ET.parse(annotations)
        if interactive:
            root = tree.getroot()
            regions = []
            for region in root.iter("Vertices"):
                coords = []
                for vertex in region:
                    # convert each coordinate to (y, x) to fix the orientation
                    coords.append(
                        [float(vertex.get("Y")), float(vertex.get("X"))])
                coords = np.array(coords)
                regions.append(coords)
            decimal_color = tree.find('./Annotation').attrib['LineColor']
            line_color = hex(int(decimal_color)).replace('0x', '').zfill(6)
            viewer.add_shapes(
                regions, shape_type='path', edge_color=f"#{line_color}")
            viewer.add_points(centers_of_contours(regions), size=4)
        else:
            rendered_annotations = xml_to_image(tree, shape=np_img.shape)
            viewer.add_image(
                rendered_annotations,
                name='annotations',
                is_pyramid=False
            )


if __name__ == '__main__':
    cli()
