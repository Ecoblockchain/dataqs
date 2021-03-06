#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright Kitware Inc. and Epidemico Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

import glob
import os
import httpretty
from django.test import TestCase
from dataqs.gistemp.gistemp import GISTEMPProcessor

script_dir = os.path.dirname(os.path.realpath(__file__))


def get_mock_image():
    """
    Return a canned test image (1 band of original NetCDF raster)
    """
    zf = os.path.join(script_dir, 'resources/gistemp1200_ERSSTv4.nc')
    with open(zf, 'rb') as gzfile:
        return gzfile.read()


class GISTEMPTest(TestCase):
    """
    Tests the dataqs.gistemp module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = GISTEMPProcessor()
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        self.processor.cleanup()

    def test_download(self):
        """
        Verify that a file is downloaded
        """
        httpretty.register_uri(httpretty.GET,
                               self.processor.base_url,
                               body=get_mock_image())
        imgfile = self.processor.download(
            self.processor.base_url,
            '{}.nc'.format(self.processor.layer_name))
        self.assertTrue(os.path.exists(
            os.path.join(self.processor.tmp_dir, imgfile)))

    def test_cleanup(self):
        httpretty.register_uri(httpretty.GET,
                               self.processor.base_url,
                               body=get_mock_image())
        self.processor.download(self.processor.base_url,
                                '{}.nc'.format(self.processor.layer_name))
        self.assertNotEqual([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
