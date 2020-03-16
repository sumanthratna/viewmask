#!/usr/bin/env python

import click
import napari
import xml.etree.ElementTree as ET
from PIL import Image
import numpy as np
from viewmask.utils import xml_to_image


@click.group()
def cli():
    pass


@cli.command()
@click.argument(u'annotations', type=click.Path(exists=True, dir_okay=False))
@click.option('-i', '--interactive', default=False, show_default=True, type=bool, is_flag=True)
def view_annotations(annotations, interactive):
    tree = ET.parse(annotations)
    with napari.gui_qt():
        viewer = napari.Viewer()
        if interactive:
            root = tree.getroot()
            regions = []
            for region in root.iter("Vertices"):
                coords = []
                for vertex in region:
                    coords.append(
                        [float(vertex.get("X")), float(vertex.get("Y"))])
                    # coords.append(list(map(float, vertex.attrib.values())))
                coords = np.array(coords)
                regions.append(coords)
            decimal_color = tree.find('./Annotation').attrib['LineColor']
            line_color = hex(int(decimal_color)).replace('0x', '').zfill(6)
            _ = viewer.add_shapes(
                regions, shape_type='path', edge_color=f"#{line_color}")
        else:
            rendered_annotations = xml_to_image(tree)
            _ = viewer.add_image(
                rendered_annotations,
                'annotations',
                pyramid=False
            )


@cli.command()
@click.argument(u'image', type=click.Path(exists=True, dir_okay=False))
def view_image(image):
    with napari.gui_qt():
        _ = napari.view_image(np.asarray(Image.open(image)), name='image')


@cli.command()
@click.argument(u'image', type=click.Path(exists=True, dir_okay=False))
@click.argument(u'annotations', type=click.Path(exists=True, dir_okay=False))
@click.option('-i', '--interactive', default=False, show_default=True, type=bool, is_flag=True)
def view_overlay(image, annotations, interactive):
    with napari.gui_qt():
        viewer = napari.Viewer()
        viewer.add_image(np.asarray(Image.open(image)), name='image')

        tree = ET.parse(annotations)
        if interactive:
            root = tree.getroot()
            regions = []
            for region in root.iter("Vertices"):
                coords = []
                for vertex in region:
                    coords.append(
                        [float(vertex.get("X")), float(vertex.get("Y"))])
                    # coords.append(list(map(float, vertex.attrib.values())))
                coords = np.array(coords)
                regions.append(coords)
            decimal_color = tree.find('./Annotation').attrib['LineColor']
            line_color = hex(int(decimal_color)).replace('0x', '').zfill(6)
            _ = viewer.add_shapes(
                regions, shape_type='path', edge_color=f"#{line_color}")
        else:
            rendered_annotations = xml_to_image(tree)
            _ = viewer.add_image(
                rendered_annotations,
                'annotations',
                pyramid=False
            )


if __name__ == '__main__':
    cli()
