"""
Small web service for static gallery generation.

"""

from PIL import Image
import os
from jinja2 import Environment, PackageLoader
from configuration import *
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))


def create_gallery():
    env = Environment(loader=PackageLoader('static_gallery_generator', 'templates'))
    gallery_path = os.path.join(ACTUAL_PATH, STATIC_NAME, GALLERY_NAME)

    for elem in os.listdir(gallery_path):
        gallery_elem_path = os.path.join(gallery_path, elem)
        if os.path.isdir(gallery_elem_path):
            thumbs_path = os.path.join(gallery_elem_path, THUMBS_NAME)
            image_list = os.listdir(gallery_elem_path)

            if THUMBS_NAME in image_list:
                # suppress thumbnail folder
                image_list.remove(THUMBS_NAME)

            if INDEX_GALLERY_NAME in image_list:
                # simply remove
                image_list.remove(INDEX_GALLERY_NAME)

            if not os.path.exists(thumbs_path):
                os.mkdir(thumbs_path)

            image_list.sort()

            for image in image_list:
                # create thumbs
                image_path = os.path.join(gallery_elem_path, image)
                image_thumb_path = os.path.join(thumbs_path, image)

                image_full = Image.open(os.path.normcase(image_path))
                image_full.thumbnail(THUMBS_SIZE, Image.ANTIALIAS)
                image_full.save(image_thumb_path, image_full.format)

            gallery_url = gallery_elem_path
            thumbs_url = "/".join([gallery_elem_path, THUMBS_NAME])
            template = env.get_template('base.jinja2')
            template_content = template.render(title=elem, thumbs_url=thumbs_url, gallery_url=gallery_url, image_list=image_list)

            # save static file
            new_file = file("/".join([gallery_elem_path, "index.html"]), 'w')
            new_file.write(template_content)
            new_file.close()

if __name__ == '__main__':
    create_gallery()
