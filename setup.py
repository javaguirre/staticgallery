from distutils.core import setup

setup(
    name='StaticGallery',
    version='0.1.0',
    author='Javier Aguirre',
    author_email='contacto@javaguirre.net',
    packages=['static_gallery'],
    scripts=['bin/generator.py'],
    url='http://pypi.python.org/pypi/StaticGallery/',
    license='LICENSE.txt',
    description='Static gallery generation using Jinja2 ',
    long_description=open('README.txt').read(),
    install_requires=['Jinja2 == 2.6',
                      'PIL == 1.1.7']
)
