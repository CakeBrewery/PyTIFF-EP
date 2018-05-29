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
    @unittest.skip('skip')
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
    
    @unittest.skip('skip')
    def test_raw_strip_offset(self):
        with open(TEST_FILE, 'rb') as f:
            tiffep = tiff_ep.TiffEp(f)

            raw_strip_offsets, ifd = tiff_ep.get_raw_strip_offsets(tiffep, f)

            raise NotImplementedError(raw_strip_offsets)

    def test_strips_generator(self):
        with open(TEST_FILE, 'rb') as f:
            tiffep = tiff_ep.TiffEp(f)

            strips = tiff_ep.Strips(tiffep, f)

            for strip in strips:
                print(strip)

