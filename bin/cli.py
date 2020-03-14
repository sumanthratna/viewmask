#!/usr/bin/env python

import click
import napari
import xml.etree.ElementTree as ET
from PIL import Image
import numpy as np


@click.group()
def cli():
    pass


@cli.command()
@click.argument(u'annotations', type=click.Path(exists=True, dir_okay=False))
@click.option('-i', '--interactive', default=False, show_default=True, type=bool, is_flag=True)
def view_annotations(annotations, interactive):
    tree = ET.parse(annotations)
    root = tree.getroot()
    with napari.gui_qt():
        viewer = napari.Viewer()
        for region in root[0][1][1:]:
            coords = []
            for vertex in region[1]:
                # coords.append(list(map(float, vertex.attrib.values())))
                coords.append(np.fromiter(
                    vertex.attrib.values(), np.float64))
            coords = np.asarray(coords)
            viewer.add_points(coords)


@cli.command()
@click.argument(u'image', type=click.Path(exists=True, dir_okay=False))
def view_image(image):
    with napari.gui_qt():
        viewer = napari.Viewer()
        viewer.add_image(np.asarray(Image.open(image)), name='image')


@cli.command()
@click.argument(u'image', type=click.Path(exists=True, dir_okay=False))
@click.argument(u'annotations', type=click.Path(exists=True, dir_okay=False))
@click.option('-i', '--interactive', default=False, show_default=True, type=bool, is_flag=True)
def view_overlay(image, annotations):
    with napari.gui_qt():
        viewer = napari.Viewer()


if __name__ == '__main__':
    cli()
