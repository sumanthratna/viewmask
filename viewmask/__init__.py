__version__ = '0.1.8'


from viewmask.utils import (xml_to_contours,
                            centers_of_contours,
                            xml_to_image,
                            get_stroke_color,
                            mask_to_contours,
                            centers_to_image)
__all__ = ['xml_to_contours',
           'centers_of_contours',
           'xml_to_image',
           'get_stroke_color',
           'mask_to_contours',
           'centers_to_image']
