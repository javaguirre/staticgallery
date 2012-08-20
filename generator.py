"""
    Static Gallery Generator

"""

from PIL import Image
import ExifTags
import os
from jinja2 import Environment, PackageLoader
from configuration import *
import sys
import argparse


sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
env = Environment(loader=PackageLoader('static_gallery_generator',
                  'templates'))


def generate_html_output(path, template_name, arguments):
    template = env.get_template(template_name)
    template_content = template.render(**arguments)

    # save static file
    new_file = file(path, 'w')
    new_file.write(template_content)
    new_file.close()


def create_menu(template_name):
        galleries = []
        gallery_path = DST_GALLERY_PATH

        for gallery in os.listdir(gallery_path):
            gallery_elem_path = os.path.join(gallery_path, gallery)

            if os.path.isdir(gallery_elem_path) and gallery != "static":
                galleries.append({"title": gallery,
                                  "url": "/".join(["/" + gallery, "index.html"])})

        generate_html_output("/".join([gallery_path, "index.html"]),
                             template_name,
                             {"title": "Album", "galleries": galleries})


def prepare_images(gallery_name, image_list):
    src_gallery = os.path.join(SRC_GALLERY_PATH, gallery_name)
    dst_gallery = os.path.join(DST_GALLERY_PATH, gallery_name)
    thumbs_path = os.path.join(dst_gallery, THUMBS_NAME)

    if not os.path.exists(dst_gallery):
        os.mkdir(dst_gallery)

    if not os.path.exists(thumbs_path):
        os.mkdir(thumbs_path)

    for image in image_list:
        # create thumbs
        image_path = os.path.join(src_gallery, image)
        image_thumb_path = os.path.join(thumbs_path, image)

        image_full = Image.open(os.path.normcase(image_path))
        image_exif_dict = image_full._getexif()

        if image_exif_dict is not None:
            exif = {}

            for k, v in image_exif_dict.items():
                try:
                    if ExifTags.TAGS[k] == 'Orientation':
                        exif[ExifTags.TAGS[k]] = v
                        break
                except KeyError:
                    print("the image has no metadata")

            if exif['Orientation'] == 3:
                image_full = image_full.rotate(180, expand=True)
            elif exif['Orientation'] == 6:
                image_full = image_full.rotate(270, expand=True)
            elif exif['Orientation'] == 8:
                image_full = image_full.rotate(90, expand=True)

        image_dst_path = os.path.join(dst_gallery, image)
        # TODO An option to rewrite images
        if not os.path.exists(image_dst_path):
            # FIXME PIL overrides original metadata when saving, we want to keep it
            image_full.save(image_dst_path, image_full.format)

        if not os.path.exists(os.path.join(image_thumb_path)):
            image_full.thumbnail(THUMBS_SIZE, Image.ANTIALIAS)
            image_full.save(image_thumb_path, image_full.format)


def create_gallery(template_name):
    gallery_path = SRC_GALLERY_PATH

    for gallery_name in os.listdir(gallery_path):
        gallery_elem_path = os.path.join(gallery_path, gallery_name)
        dst_gallery_path = os.path.join(DST_GALLERY_PATH, gallery_name)

        if os.path.isdir(gallery_elem_path):
            image_list = os.listdir(gallery_elem_path)
            image_list.sort()
            prepare_images(gallery_name, image_list)

            gallery_url = "".join(["/",  gallery_name, "/"])
            thumbs_url = "".join([gallery_url, THUMBS_NAME, "/"])

            generate_html_output("/".join([dst_gallery_path, "index.html"]),
                                 template_name,
                                 {"title": gallery_name.capitalize(),
                                  "thumbs_url": thumbs_url,
                                  "gallery_url": gallery_url,
                                  "image_list": image_list})


def process_call(arguments):
    """ Process call arguments """

    if arguments.template_gallery is not None:
        create_gallery(arguments.template_gallery)
    else:
        create_gallery("galleria.jinja2")

    if arguments.template_menu is not None:
        create_menu(arguments.template_menu)
    else:
        create_menu("menu.jinja2")


def main():
    """Parses app command line options """
    parser = argparse.ArgumentParser(description='Static Gallery Generator Options.')
    parser.add_argument('--template-gallery',
                        help='Choose the name of the template for the gallery')
    parser.add_argument('--template-menu',
                        help='Choose the template for the menu')
    parser.add_argument('--src',
                        help='Source directory for the gallery')
    parser.add_argument('--dst',
                        help='Destiny when the web gallery will be generated')

    arguments = parser.parse_args()
    process_call(arguments)


if __name__ == '__main__':
    main()
