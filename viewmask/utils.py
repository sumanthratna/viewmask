import cv2
import numpy as np


def xml_to_contours(xml_tree, contour_drawer):
    if contour_drawer not in ['napari', 'cv2']:
        raise ValueError("contour_drawer must be 'cv2' or 'napari'")
    root = xml_tree.getroot()
    regions = []
    for region in root.iter("Vertices"):
        coords = []
        for vertex in region:
            if contour_drawer == 'napari':
                # convert each coordinate to (y, x) to rotate
                coords.append(
                    [float(vertex.get("Y")), float(vertex.get("X"))])
            else:  # contour_drawer is 'cv2'
                coords.append(
                    [float(vertex.get("X")), float(vertex.get("Y"))])
        coords = np.array(coords, dtype=np.int32)
        regions.append(coords)
    return regions


def centers_of_contours(contours):
    centers = []
    for contour in contours:
        M = cv2.moments(contour)
        center_x = int(M["m10"] / M["m00"])
        center_y = int(M["m01"] / M["m00"])
        centers.append((center_x, center_y))
    return centers


def xml_to_image(xml_tree, shape=(1000, 1000, 3)):
    contours = xml_to_contours(xml_tree, 'cv2')
    centers = centers_of_contours(contours)
    rendered_annotations = np.zeros(shape, dtype=np.uint8)
    cv2.drawContours(rendered_annotations, contours, -1, [0, 255, 0])
    for center, contour in zip(centers, contours):
        cv2.fillPoly(rendered_annotations, np.array(
            [contour], dtype=np.int32), [230, 230, 230])
        cv2.circle(rendered_annotations, center, 4, [0, 0, 0], -1)
    return rendered_annotations
