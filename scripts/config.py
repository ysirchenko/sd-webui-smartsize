import modules.scripts as scripts
import distutils.util
from pathlib import Path
import os
import xml.etree.ElementTree as ET
import numpy
import pandas as pd

basedir = scripts.basedir()


class Config:
    height_max = 1920
    width_max = 1080
    step = 8

    aspect_ratios = []
    resolutions = []

    @staticmethod
    def get_parameter(e, name, default):
        if name in e.attrib:
            attrib = e.attrib[name]
            if attrib == '':
                value = default
            else:
                if type(default) in [int, numpy.int64]:
                    value = int(attrib)
                elif type(default) in [bool, numpy.bool_]:
                    value = bool(distutils.util.strtobool(attrib))
                elif type(default) in [float, numpy.float64]:
                    # value = float(attrib)
                    value = eval(attrib)
                else:
                    value = attrib
        else:
            value = default
        return value

    @staticmethod
    def read():
        tree = ET.parse(Path(basedir, 'config.xml'))
        root = tree.getroot()

        Config.height_max = Config.get_parameter(root, 'height_max', 640)
        Config.width_max = Config.get_parameter(root, 'width_max', 640)
        Config.step = Config.get_parameter(root, 'step', 8)

        Config.aspect_ratios = []
        for e in tree.findall('aspect_ratio'):
            Config.aspect_ratios.append({
                'text': Config.get_parameter(e, 'text', '1:1'),
                'value': Config.get_parameter(e, 'value', 1.0)})

        Config.resolutions = []
        for e in tree.findall('resolution'):
            Config.resolutions.append({
                'text': Config.get_parameter(e, 'text', '1'),
                'width': Config.get_parameter(e, 'width', 640),
                'height': Config.get_parameter(e, 'height', 640)})
