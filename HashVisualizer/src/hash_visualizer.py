import PIL
import PIL.Image
import PIL.ImageColor
import random
from image_draw import ImageDraw


def to_color(seed_8_bit, alpha=255):
    # https://en.wikipedia.org/wiki/8-bit_color
    # RRR GGG BB
    r = ((seed_8_bit >> 5) & 0x7) / 0x7
    g = ((seed_8_bit >> 2) & 0x7) / 0x7
    b = (seed_8_bit & 0x3) / 0x3
    return round(r * 255), round(g * 255), round(b * 255), alpha


def version_1(seed):
    image = PIL.Image.new("RGBA", (512, 512))
    d = ImageDraw(image)

    for quadrant in range(3, -1, -1):
        bits = (seed >> (quadrant * 32)) & 0xFFFFFFFF
        x = (quadrant % 2) * 256
        y = (quadrant >= 2) * 256
        bg_color = to_color(bits >> 24)
        fg_primary_color = to_color(bits >> 16)
        fg_secondary_color = to_color(bits >> 8, 128)
        from mix_functions import to_pattern
        primary_pattern = to_pattern((bits >> 4) & 0xF, seed)
        secondary_pattern = to_pattern(bits & 0xF, seed)

        d.rect(x, y, 256, 256, bg_color)
        primary_pattern(d, x, y, fg_primary_color)
        secondary_pattern(d, x, y, fg_secondary_color)

    return image


def create_and_save(seed):
    version_1(seed).save("images/"+hex(seed)+".png")

for i in range(256):
    r = random.getrandbits(128)
    create_and_save(r)
    create_and_save(r ^ (1 << random.getrandbits(7)))
    create_and_save(r ^ (1 << random.getrandbits(7)))
    create_and_save(r ^ (1 << random.getrandbits(7)))
    print("{:.1%} done".format(i/255))

