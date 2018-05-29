from __future__ import unicode_literals
import fractions
import struct
import six

from collections import OrderedDict


IFD_SIZE = 12  # in bytes


# (size in bytes, type name)
IFD_FIELD_TYPES = [(1, 'BYTE'), (1, 'ASCII'), (2, 'SHORT'), (4, 'LONG'), (8, 'RATIONAL'),
        (1, 'SBYTE'), (1, 'UNDEFINED'), (2, 'SSHORT'), (4, 'SLONG'), (8, 'SRATIONAL'),
        (4, 'FLOAT'), (8, 'DOUBLE')]


IFD_TAGS = OrderedDict({
    'NewSubfileType': 254,
    'SubfileType': 255,
    'ImageWidth': 256,
    'ImageLength': 257,
    'BitsPerSample': 258,
    'Compression': 259,
    'PhotometricInterpretation': 262,
    'ImageDescription': 270,
    'Make': 271,
    'Model': 272,
    'StripOffsets': 273,
    'Orientation': 274,
    'SamplesPerPixel': 277,
    'RowsPerStrip': 278,
    'StripByteCounts': 279,
    'MinSampleValue': 280,
    'MaxSampleValue':281,
    'XResolution': 282,
    'YResolution': 283,
    'PlanarConfiguration': 284,
    'FreeOffsets': 288,
    'FreeByteCounts': 289,
    'SubIFDs': 330,
    'Copyright': 33432,
    'ExifIFD': 34665,
    'ExposureTime': 33434,
    'FNumber': 33437,
    'ExposureProgram': 34850,
    'ISOSpeedRatings': 34855,
    'ExifVersion': 36864,
    'DateTimeOriginal': 36867,
    'DateTimeDigitized': 36868,
    'ComponentsConfiguration': 37121,
    'CompressedBitsPerPixel': 37122,
    'BrightnessValue': 37379,
    'ExposureBiasValue': 37380,
    'MaxApertureValue': 37381,
    'MeteringMode': 37383,
    'LightSource': 37384,
    'Flash': 37385,
    'FocalLength': 37386,
    'MakerNote': 37500,
    'UserComment': 37510,
    'FlashpixVersion': 40960,
    'ColorSpace': 40961,
    'PixelXDimension': 40962,
    'PixelYDimension': 40963,
    'InteroperabilityIFD': 40965,
    'FileSource': 41728,
    'SceneType': 41729,
    'CustomRendered': 41985,
    'ExposureMode': 41986,
    'WhiteBalance': 41987,
    'DigitalZoomRatio': 41988,
    'FocalLengthIn35mmFilm': 41989,
    'SceneCaptureType': 41990,
    'Contrast': 41992,
    'Saturation': 41993,
    'Sharpness': 41994,
})


COMPRESSION_CODES_NAMES = {
    1: 'Uncompressed',
    2: 'CCITTRLE',
    3: 'CCITTRLE',
    4: 'CCITT Group 4',
    5: 'LZW',
    6: '"Old Style" JPEG',
    7: '"New Style" JPEG',
    8: 'DEFLATE',
    9: 'JBIG',
    10: 'JBIG',
    32766: 'NeXT 2-bit RLE',
    32767: 'Sony ARW',
    32769: 'Packed RAW / NIKON_PACK',
    32770: 'Samsung SRW',
    32771: 'CCITTRLEW',
    32773: 'PackBits',
    32809: 'ThunderScan',
    32867: 'Kodak KDC',
    32895: 'T8CTPAD, IT8LW, IT8MP, IT8BL',
    32896: 'T8CTPAD, IT8LW, IT8MP, IT8BL',
    32897: 'T8CTPAD, IT8LW, IT8MP, IT8BL',
    32898: 'T8CTPAD, IT8LW, IT8MP, IT8BL',
    32946: 'DEFLATE',
    32947: 'Kodak DCS',
    33003: 'Aperio SVS',
    33005: 'Aperio SVS',
    34661: 'JBIG',
    34676: 'SGILOG',
    34677: 'SGILOG24',
    34692: 'LuraDocument Format',
    34712: 'JPEG 2000',
    34713: 'Nikon NEF',
    34715: 'JBIG2',
    34718: 'MDI',
    34719: 'MDI',
    34720: 'MDI',
    34892: 'Lossy JPEG (DNG)'
}


FIRST_4_BYTES_HEX = {
    # Big Endian
    'TIFF (Big-Endian)': ['4d', '4d', '00', '2a'],
    'BigTIFF (Big-Endian': ['4d', '4d', '00', '2b'],
    'Panasonic RAW/RW2 (Big-Endian)': ['4d', '4d', '00', '55'],
    'DNG Camera Profile (Big-Endian)': ['4d', '4d', '43', '52'],
    'Olympus ORF (Big-Endian)': ['4d', '4d', '4f', '52'],
    'Olympus ORF alternate (Big-Endian)': ['4d', '4d', '53', '52'],

    # Little Endian
    'TIFF (Little-Endian)': ['49', '49', '2a', '00'],
    'BigTIFF (Little-Endian)': ['49', '49', '2b', '00'],
    'Panasonic RAW/RW2 (Little-Endian)': ['49', '49', '55', '00'],
    'JPEG XR (Little-Endian)': ['49', '49', 'bc', '01'],
    'NIFF (Little-Endian)': ['49', '49', '4e', '31'],
    'DNG Camera Profile (Little-Endian)': ['49', '49', '52', '43'],
    'Olympus ORF (Little Endian)': ['49', '49', '52', '4f'],
    'Olympus ORF alternate (Little Endian)': ['49', '49', '52', '53'],
    'MDI (Little-Endian)': ['45', '50', '2a', '00']


}


# Also keep an inverted IFD_TAGS lookup for convenience.
# The key, value pairs from d.values() and d.keys() 
# will be ordered since IFD_TAGS is an OrderedDict
def invert_key_values(d):
    return type(d)(zip(d.values(), d.keys()))
IFD_TAGS_INVERTED = invert_key_values(IFD_TAGS)


# These are all TIFF-defined data types
def get_ifd_field_type(type_number):
    return IFD_FIELD_TYPES[type_number-1]


def read_byte(data, endianness='<'):
    # 1 byte
    return struct.unpack('{}B'.format(endianness), data)[0]


def read_sbyte(data, endianness='<'):
    # 1 signed byte
    return struct.unpack('{}b'.format(endianness), data)[0]


def read_integer(data, endianess='<'):
    # 4 byte integer
    return struct.unpack('{}I'.format(endianess), data)[0]


def read_integer(data, endianess='<'):
    # 4 byte signed integer
    return struct.unpack('{}i'.format(endianess), data)[0]


def read_short(data, endianness='<'):
    # 2 byte short
    return struct.unpack('{}H'.format(endianness), data)[0]


def read_sshort(data, endianness='<'):
    # 2 byte signed short
    return struct.unpack('{}h'.format(endianness), data)[0]


def read_long(data, endianness='<'):
    # 4 byte long
    return struct.unpack('{}L'.format(endianness), data)[0]
 

def read_slong(data, endianness='<'):
    # 4 byte signed long
    return struct.unpack('{}l'.format(endianness), data)[0]


def read_rational(data, endianness='<'):
    # two 4 byte longs.
    # Represents a fraction according to TIFF implementation.
    # The first long is the numerator
    # The second long is the denominator
    numerator = read_long(data[:4], endianness)
    denominator = read_long(data[4:], endianness)
    return fractions.Fraction(numerator, denominator)


def read_srational(data, endianness='<'):
    # Same as read_rational, but two 4 byte SIGNED longs
    numerator = read_slong(data[:4], endianness)
    denominator = read_slong(data[4:], endianness)
    return fractions.Fraction(numerator, denominator)
 

def get_endianness(open_file):
    open_file.seek(0)
    return '<' if 'I' == open_file.read(1).decode('utf-8') else '>';


def get_ifd_offset(open_file, endianness=None):
    endianness = endianness or get_endianness(open_file)
    open_file.seek(4)
    return read_integer(open_file.read(4), endianness)


def get_ifd(open_file, offset, endianness=None):
    ifd = IFD(open_file, offset, endianness)
    return ifd, ifd.next
        

_PARSE_FNS = {
    'ASCII': lambda x, *args, **kwargs: x.decode('ascii'),
    'SHORT': read_short,
    'LONG': read_long,
    'BYTE': read_byte,
    'RATIONAL': read_rational,
    'SBYTE': read_sbyte,
    'UNDEFINED': read_byte,
    'SSHORT': read_sshort,
    'SRATIONAL': read_srational
}


def parse_field_type(data, field_type, endianness):
    return _PARSE_FNS[field_type](data, endianness) 


def _get_offset_values(open_file, offset, size, num_vals, field_type, endianness):
    open_file.seek(offset)
    return [parse_field_type(open_file.read(size), field_type, endianness) for i in range(0, num_vals)] 


class IFDField(object):

    def __init__(self, data, endianness):
        self._data = data

        self.endianness = endianness

        self.tag = read_short(self._data[:2], self.endianness)
        type_data = read_short(self._data[2:4], self.endianness)
        self.size, self.field_type = get_ifd_field_type(type_data)
        self.num_vals = read_integer(self._data[4:8], self.endianness)

        self._offset_or_value = data[8:12] 

    def requires_file(self):
        return self.size*self.num_vals > 4

    def values(self, open_file=None):
        # Field values can be defined in two ways:
        # a) If the values are <= 4 bytes in total, the trailing bytes
        #   of the field represent the value itself (or values ??? ) 
        # b) If they don't fit, (aka, over 4 bytes) the trailing bytes
        #  describe an offest defining the location of the values
        #  within the image file.
        #
        # Requires an open file if the value is defined as an offset
        # An offset (rather than a value) defines an offset within 
        # the open image file, so we must pass such open image file.
        # No need to pass a file otherwise.
        values = []
        if not self.requires_file():
            n = 0
            while n < 4:
                val = parse_field_type(self._offset_or_value[n:n+self.size], 
                        self.field_type, self.endianness)
                values.append(val)
                n += self.size
        else:
            if not open_file:
                raise ValueError('Requires open file')
            offset = read_integer(self._offset_or_value, self.endianness)
            values = _get_offset_values(open_file, offset, self.size, 
                    self.num_vals, self.field_type, self.endianness)

        return values

    def __repr__(self):
        val = None
        _name = IFD_TAGS_INVERTED.get(self.tag)
        tag_name = '{} ({})'.format(self.tag, _name) if _name else self.tag
        if self.requires_file():
            val = 'offset={}'.format(read_integer(self._offset_or_value, 
                self.endianness))
        else:
            val = self.values()
        return 'IFDField({}, {}, {}, {}, {})'.format(tag_name, 
                self.field_type, self.size, self.num_vals, val);
    

class IFD(OrderedDict):

    def __init__(self, open_file, ifd_offset, endianness):
        self.endianness = endianness or get_endianness(open_file)
        self.__load_ifd(open_file, ifd_offset, endianness)
        
    def __load_ifd(self, open_file, ifd_offset, endianness):
        open_file.seek(ifd_offset)
        num_entries = read_short(open_file.read(2), endianness)

        for i in range(0, num_entries):
            ifd_field = IFDField(open_file.read(12), endianness)
            if self.get(ifd_field.tag):
                raise ValueError('Repeated IFD tag')
            self[int(ifd_field.tag)] = ifd_field

        self.next = read_integer(open_file.read(4), endianness)

    def __getitem__(self, key):
        if isinstance(key, six.string_types):
            return self[IFD_TAGS[key]]
        return super(IFD, self).__getitem__(key)

    def get(self, key, default=None):
        # Apparently __getitem__ doesn't apply for "get"...
        if isinstance(key, six.string_types):
            return self.get(IFD_TAGS[key], default)
        return super(IFD, self).get(key, default)

    def sub_ifd_offsets(self):
        return self.get('SubIFDs') 

    def exif_ifd_offsets(self):
        return self.get('ExifIFD') 

    def sub_ifds(self, open_file):
        offsets = self.sub_ifd_offsets()
        if offsets:
            offsets = offsets.values(open_file)
            return [IFD(open_file, offset, self.endianness) for offset in offsets] 

    def exif_ifds(self, open_file):
        offsets = self.exif_ifd_offsets()
        if offsets:
            offsets = offsets.values(open_file)
            return [IFD(open_file, offset, self.endianness) for offset in offsets] 


def _get_raw_strip_offsets(ifd, open_file):
    subfile_type = sub_ifd.get('NewSubfileType').values(open_file)[0]
    if subfile_type == 0 and sub_ifd.get('StripOffsets'):
        return sub_ifd.get('StripOffsets').values()

def get_raw_strip_offset(tiff_ep, open_file):
    # Search for the strip offsets of the first raw image.
    for ifd in tiff_ep.ifd_chain:
        offsets = get_strip_offsets(ifd, open_file)
        if offsets:
            return offsets, ifd

        for sub_ifd in ifd.sub_ifds(open_file):
            offsets = get_strip_offsets(sub_ifd, open_file)
            if offsets:
                return offsets, sub_ifd 

        for exif_ifd in ifd.exif_ifds(open_file):
            offsets = get_strip_offsets(sub_ifd, open_file)
            if offsets:
                return offsets, exif_ifd


class TiffEp(object):

    def __init__(self, f):
        self.endianness = get_endianness(f)
        self.ifd_chain = self._parse_ifd_chain(f, self.endianness)

    def _parse_ifd_chain(cls, f, endianness):
        result = []
        root_offset = get_ifd_offset(f, endianness)
        next_ifd = root_offset

        while next_ifd:
            ifd, next_ifd = get_ifd(f, next_ifd, endianness)
            result.append(ifd)

        return result

