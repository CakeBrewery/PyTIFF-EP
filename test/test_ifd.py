import os
import unittest

from PyTiffEP import tiff_ep


TEST_FILE = os.path.join('test', 'file.ARW')


def print_ifd(ifd, f):
    for field in ifd.values():
        print(field)
        if field.requires_file():
            print('\tReal values: {}'.format(field.values(f)))



class TestTiffEP(unittest.TestCase):

    def test_tiff_ep(self):
        with open(TEST_FILE, 'rb') as f:
            tiffep = tiff_ep.TiffEp(f)
            self.assertTrue(len(tiffep.ifd_chain))

            for ifd in tiffep.ifd_chain:
                print('\n==== IFD ====')
                print_ifd(ifd, f)
    
                sub_ifds = ifd.sub_ifds(f)

                if sub_ifds:
                    for sub in sub_ifds:
                        print('\n--- SubIFD ---')
                        print_ifd(sub, f)
                    
                exif_ifds = ifd.exif_ifds(f)

                if exif_ifds:
                    for exif in exif_ifds:
                        print('\n--- ExifIFD ---')
                        print_ifd(exif, f)
