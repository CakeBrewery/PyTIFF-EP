import math


def strips_per_image(image_length, rows_per_strip):
    return math.floor((image_length + rows_per_strip - 1) / rows_per_strip)

