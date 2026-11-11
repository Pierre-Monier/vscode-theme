# ABOUTME: Simulates protanopia, deuteranopia and tritanopia, and measures colour difference and text contrast.
# ABOUTME: Uses the Machado et al. (2009) full-severity matrices and the CIEDE2000 colour difference.
import math

# Applied to linear sRGB.
SIMULATIONS = {
    "normal vision": None,
    "protanopia": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    "deuteranopia": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    "tritanopia": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}


def linear_rgb(hex_colour):
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]


def simulate(rgb, simulation):
    matrix = SIMULATIONS[simulation]
    if matrix is None:
        return rgb
    return [min(1.0, max(0.0, sum(matrix[row][col] * rgb[col] for col in range(3)))) for row in range(3)]


def lab(rgb):
    r, g, b = rgb
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def ciede2000(lab1, lab2):
    l1, a1, b1 = lab1
    l2, a2, b2 = lab2
    c_mean = (math.hypot(a1, b1) + math.hypot(a2, b2)) / 2
    g = 0.5 * (1 - math.sqrt(c_mean ** 7 / (c_mean ** 7 + 25 ** 7)))
    a1, a2 = (1 + g) * a1, (1 + g) * a2
    c1, c2 = math.hypot(a1, b1), math.hypot(a2, b2)
    h1, h2 = math.degrees(math.atan2(b1, a1)) % 360, math.degrees(math.atan2(b2, a2)) % 360

    if c1 * c2 == 0:
        dh, h_mean = 0, h1 + h2
    else:
        dh = h2 - h1 if abs(h2 - h1) <= 180 else (h2 - h1 - 360 if h2 > h1 else h2 - h1 + 360)
        h_mean = (h1 + h2) / 2 if abs(h1 - h2) <= 180 else (h1 + h2 + 360) / 2 if h1 + h2 < 360 else (h1 + h2 - 360) / 2
    dl, dc = l2 - l1, c2 - c1
    dh_big = 2 * math.sqrt(c1 * c2) * math.sin(math.radians(dh / 2))
    l_mean, c_mean = (l1 + l2) / 2, (c1 + c2) / 2

    t = (1 - 0.17 * math.cos(math.radians(h_mean - 30)) + 0.24 * math.cos(math.radians(2 * h_mean))
         + 0.32 * math.cos(math.radians(3 * h_mean + 6)) - 0.20 * math.cos(math.radians(4 * h_mean - 63)))
    sl = 1 + 0.015 * (l_mean - 50) ** 2 / math.sqrt(20 + (l_mean - 50) ** 2)
    sc = 1 + 0.045 * c_mean
    sh = 1 + 0.015 * c_mean * t
    rt = (-2 * math.sqrt(c_mean ** 7 / (c_mean ** 7 + 25 ** 7))
          * math.sin(math.radians(60 * math.exp(-(((h_mean - 275) / 25) ** 2)))))
    return math.sqrt((dl / sl) ** 2 + (dc / sc) ** 2 + (dh_big / sh) ** 2 + rt * (dc / sc) * (dh_big / sh))


def difference(colour1, colour2, simulation):
    return ciede2000(lab(simulate(linear_rgb(colour1), simulation)), lab(simulate(linear_rgb(colour2), simulation)))


def contrast(colour1, colour2):
    def luminance(colour):
        return sum(w * c for w, c in zip((0.2126, 0.7152, 0.0722), linear_rgb(colour)))

    light, dark = sorted((luminance(colour1), luminance(colour2)), reverse=True)
    return (light + 0.05) / (dark + 0.05)
