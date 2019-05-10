''' 
Render layer into PNG image
'''
from qgis_ipython.startup import  start_qgis_application

# Needed for setting paths
start_qgis_application(verbose=True)

from qgis.PyQt.QtGui import QColor, QImage
from qgis.PyQt.QtCore import QSize, QBuffer, QIODevice

from qgis.core import QgsMapRendererParallelJob
from qgis.core import Qgis, QgsProject, QgsMapSettings

from pathlib import Path 

def render_layer():

    projectpath = Path('./data/france_parts.qgs')

    prj = QgsProject()
    prj.read(str(projectpath.absolute()))

    layers = layers = prj.mapLayersByName('france_parts')

    xt     = layers[0].extent()
    width  = 1200
    height = int(width*xt.height()/xt.width())

    options = QgsMapSettings()
    options.setLayers(layers)
    options.setBackgroundColor(QColor(255, 255, 255))
    options.setOutputSize(QSize(width, height))
    options.setExtent(xt)
           
    render = QgsMapRendererParallelJob(options)
    render.start()
    render.waitForFinished()

    image = render.renderedImage()

    return image


def to_png(image):
    """ Get as PNG
    """
    imgbuf= QBuffer()
    imgbuf.open(QIODevice.ReadWrite)
    image.save(imgbuf,"PNG")
    # Return a QByteArray
    return imgbuf.data()


def to_np_array(image):
    """ Get as numpy array
    """
    import numpy as np

    width, height = image.width(), image.height()

    img = image.convertToFormat(QImage.Format_RGBA8888)
    ptr = img.constBits()
    ptr.setsize(height * width * 4)
    arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))

    return arr


if __name__ == '__main__':
    import os

    image = to_png(render_layer())

    with open('france_parts.png','wb') as fp:
        fp.write(image)






