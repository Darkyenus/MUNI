
import PIL.ImageDraw


class ImageDraw:
    """Partial reimplementation of PIL.ImageDraw (with slightly different API), that supports alpha blending."""

    def __init__(self, image):
        self.image = image

    def lerp(self, a, b, alpha):
        return a * (1 - alpha) + b * alpha

    def pixel(self, x, y, color):
        coord = x, y
        r, g, b, a = color
        if a <= 0:
            return
        nR, nG, nB, nA = r, g, b, 255
        if a < 255:
            oR, oG, oB, oA = self.image.getpixel(coord)
            oR /= 255
            oG /= 255
            oB /= 255
            r /= 255
            g /= 255
            b /= 255
            a /= 255
            nR = round(self.lerp(oR, r, a) * 255)
            nG = round(self.lerp(oG, g, a) * 255)
            nB = round(self.lerp(oB, b, a) * 255)
        self.image.putpixel(coord, (nR, nG, nB, 255))

    def rect(self, x, y, w, h, color):
        for px in range(x, x+w):
            for py in range(y, y+h):
                self.pixel(px, py, color)

    def text(self, x, y, text, fill=None, font=None, anchor=None):
        d = PIL.ImageDraw.ImageDraw(self.image)
        d.text([x, y], text, fill, font, anchor)

