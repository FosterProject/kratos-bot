from os import walk
from PIL import Image


PLAYER_AREA = 0
MAP_AREA = 1

# ======== CHANGE THIS ==========
FORMAT_TYPE = MAP_AREA
# ======== ----------- ==========

BASE_PATH = "F:/Development/Projects/Bots/RAW_DATA_BANK_AND_BUILDINGS/"

# Process Images
f = []
for (_, _, fn) in walk(BASE_PATH):
    f.extend(fn)
    break

if FORMAT_TYPE == PLAYER_AREA:
    timg = Image.open(BASE_PATH + f[0])
    width = timg.width
    height = timg.height

    cx = width / 2
    cy = height / 2

    y_offset = 0
    dist = cy - y_offset

    left = cx - dist
    upper = cy - dist
    right = cx + dist
    lower = cy + dist
elif FORMAT_TYPE == MAP_AREA:
    left = 719
    upper = 7
    right = 869
    lower = 157


f = [img for img in f if img.find('.png') != -1]
for img_name in f:
    # Load
    img = Image.open(BASE_PATH + img_name)

    # Crop
    cimg = img.crop((left, upper, right, lower))

    # Rescale
    scale_width = 480
    wpercent = (scale_width / float(right - left))
    hsize = int((float(lower - upper) * float(wpercent)))
    img_scaled = cimg.resize((scale_width, hsize), Image.ANTIALIAS)

    # Show / Save
    img_scaled.save('%sscaled/%s' % (BASE_PATH, img_name))
