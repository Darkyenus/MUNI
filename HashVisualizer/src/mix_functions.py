import math


def sin(x):
    return math.sin(x * math.pi)

def double_sin(x):
    return (math.sin(x * (math.pi * 2)) + 1) / 2


def lin(x):
    return x


def smooth_step(x):
    return 3 * (x ** 2) - 2 * (x ** 3)


def staircase(x):
    return math.floor(x * 10) / 10


def jaggies(x):
    return (x * 10) % 1


def crenellation(x):
    return 0 if int(x * 10) % 2 == 0 else 1

ALL_BASE = [sin, double_sin, lin, smooth_step, staircase, jaggies, crenellation]


def mod_identity(func):
    return func


def mod_inverse(func):
    return lambda x: 1 - func(x)


def mod_mirror(func):
    return lambda x: func(x * 2) if x < 0.5 else func((1-x) * 2)


def mod_inverse_mirror(func):
    return lambda x: 1 - func(x * 2) if x < 0.5 else 1 - func((1-x) * 2)


def mod_pixel(func):
    return lambda x: func(round(x * 16) / 16)

ALL_MOD = [mod_identity, mod_inverse, mod_mirror, mod_inverse_mirror, mod_pixel]

ALL_UNARY = []

for base in ALL_BASE:
    for mod in ALL_MOD:
        ALL_UNARY.append(mod(base))

PATTERNS = []


def to_pattern_from_functions(x_func, y_func):
    def pattern_function(draw, off_x, off_y, color, size=256):
        r, g, b, _ = color
        for px in range(0, size):
            for py in range(0, size):
                x_func_result = x_func(px / size)
                y_func_result = y_func(py / size)
                combined_result = int(x_func_result * y_func_result * 255)
                draw.pixel(px + off_x, py + off_y, (r, g, b, combined_result))
    return pattern_function


for unary_x in ALL_UNARY:
    for unary_y in ALL_UNARY:
        PATTERNS.append(to_pattern_from_functions(unary_x, unary_y))

print("Created ", len(PATTERNS), "patterns, from ", len(ALL_UNARY), " mix functions from ", len(ALL_BASE),
      " bases and ", len(ALL_MOD), " mods")


def to_pattern(index, seed):
    import random
    rnd = random.Random()
    rnd.seed(index * seed)
    return rnd.choice(PATTERNS)


def test_mix_functions():
    import PIL.Image
    from image_draw import ImageDraw

    image = PIL.Image.new("RGBA", [256 * len(ALL_UNARY), 256])
    d = ImageDraw(image)
    for func_index in range(0, len(ALL_UNARY)):
        x_off = func_index * 256
        for x in range(0, 256):
            y = int(ALL_UNARY[func_index](x / 255) * 255)
            d.rect(x + x_off, 0, 1, y, (255, 0, 0, y))
        d.text(x_off + 20, 20, ALL_UNARY[func_index].__name__)
    image.show()

# test_mix_functions()