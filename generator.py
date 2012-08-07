"""
    Static Gallery Generator

"""

from PIL import Image
import os
from jinja2 import Environment, PackageLoader
from configuration import *
import sys


sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
env = Environment(loader=PackageLoader('static_gallery_generator', 'templates'))


def generate_html_output(path, template_name, args):
    template = env.get_template(template_name)
    template_content = template.render(**args)

    # save static file
    new_file = file(path, 'w')
    new_file.write(template_content)
    new_file.close()


def create_menu():
        galleries = []
        gallery_path = os.path.join(ACTUAL_PATH, GALLERY_NAME)

        for gallery in os.listdir(gallery_path):
            gallery_elem_path = os.path.join(gallery_path, gallery)

            if os.path.isdir(gallery_elem_path) and gallery != "static":
                galleries.append({"title": gallery, "url": "/".join(["/" + gallery, "index.html"])})

        generate_html_output("/".join([gallery_path, "index.html"]), "menu.jinja2",
                             {"title": "Menu", "galleries": galleries})


def create_gallery():
    gallery_path = os.path.join(ACTUAL_PATH, GALLERY_NAME)

    for elem in os.listdir(gallery_path):
        gallery_elem_path = os.path.join(gallery_path, elem)

        if os.path.isdir(gallery_elem_path) and elem != "static":
            thumbs_path = os.path.join(gallery_elem_path, THUMBS_NAME)
            image_list = os.listdir(gallery_elem_path)

            if THUMBS_NAME in image_list:
                image_list.remove(THUMBS_NAME)

            if INDEX_HTML in image_list:
                image_list.remove(INDEX_HTML)

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

            gallery_url = "".join(["/",  elem, "/"])
            thumbs_url = "".join([gallery_url, THUMBS_NAME, "/"])
            generate_html_output("/".join([gallery_elem_path, "index.html"]), "base.jinja2",
                                 {"title": elem, "thumbs_url": thumbs_url, "gallery_url": gallery_url, "image_list": image_list})

if __name__ == '__main__':
    create_gallery()
    create_menu()
