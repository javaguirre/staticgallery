"""
Small web service for static gallery generation.

"""

import flask
from flask import Flask
from flask import render_template
from PIL import Image
import os

app = Flask(__name__)
app.config.from_pyfile("configuration.py")

#FIXME Provisional
static_name = app.config['STATIC_NAME']
gallery_name = app.config['GALLERY_NAME']
thumbs_name = app.config['THUMBS_NAME']
index_gallery_name = app.config['INDEX_GALLERY_NAME']
secret_prefix_name = app.config['SECRET_PREFIX_NAME']

# url parse is ugly
static_url = '/%s/'
gallery_base_url = '/%s/%s/%s/'
thumbs_base_url = '/%s/%s/%s/%s/'

static_base_path = '%s/%s/'
gallery_base_path = '%s/%s/%s/'
thumbs_base_path = '%s/%s/%s/%s/'

thumbs_size = (180, 120)
image_format = "JPEG"

class Item(object):
	def __init__(self, title, url):
		self.title = title
		self.url = url

def get_gallery_urls(folder):
	"""
	Get gallery and thumbs url

	"""

	gallery_url = gallery_base_url % (static_name, gallery_name, folder)
	thumbs_url = thumbs_base_url % (static_name, gallery_name, folder, thumbs_name)

	return gallery_url, thumbs_url

def get_gallery_path(folder):
	"""
	Get gallery and thumbs path

	"""

	gallery_path = os.path.join(app.config['ACTUAL_PATH'], gallery_base_path % (static_name, gallery_name, folder))
	thumbs_path = os.path.join(app.config['ACTUAL_PATH'], thumbs_base_path % (static_name, gallery_name, folder, thumbs_name))

	return gallery_path, thumbs_path

@app.route('/')
def do_menu():
	"""
	Generate dynamic menu

	"""

	index_image_url = (gallery_base_url % (static_name, gallery_name, app.config['INDEX_IMAGE_NAME']))[:-1]
	static_path =os.path.normcase(os.path.join(app.config['ACTUAL_PATH'], static_base_path % (static_name, gallery_name)))
	galleries = os.listdir(static_path)

	items = []

	for gallery in galleries:
		# check each gallery
		if gallery.startswith(secret_prefix_name) == False and gallery != app.config['INDEX_IMAGE_NAME']:
			# do not display secret one
			gallery_url, thumbs_url = get_gallery_urls(gallery)
			items.append(Item(gallery, gallery_url))

	return render_template('menu.jinja2', title=app.config['INDEX_TITLE'], items=items, image_url=index_image_url)

@app.route('/do_gallery/')
def do_gallery():
    for elem in os.listdir(os.path.join(app.config['ACTUAL_PATH'], static_name, gallery_name)):
        if os.path.isdir(os.path.join(app.config['ACTUAL_PATH'], static_name, gallery_name, elem)):
            gallery_path, thumbs_path = get_gallery_path(elem)
            image_list = os.listdir(gallery_path)

            if thumbs_name in image_list:
                # suppress thumbnail folder
                image_list.remove(thumbs_name)

            if index_gallery_name in image_list:
                # simply remove
                image_list.remove(index_gallery_name)

            if os.path.exists(thumbs_path) == False:
                # create thumbs directory
                os.mkdir(thumbs_path)

            image_list.sort()

            for image in image_list:
                # create thumbs
                image_path = os.path.join(gallery_path, image)
                image_thumb_path = os.path.join(thumbs_path, image)

                image_full = Image.open(os.path.normcase(image_path))
                image_full.thumbnail(thumbs_size, Image.ANTIALIAS)
                image_full.save(image_thumb_path, image_full.format)

            # generate template
            gallery_url, thumbs_url = get_gallery_urls(elem)
            template = render_template('base.jinja2', title=elem, thumbs_url=thumbs_url, gallery_url=gallery_url, image_list=image_list)

            # save static file
            new_file = file(os.path.join(gallery_path, index_gallery_name), 'w')
            new_file.write(template)
            new_file.close()

    # FIXME Provisional
    gallery_url = "index.html"

    return flask.redirect(gallery_url + index_gallery_name, code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

