from PIL import Image

sq_size = 5  # Amount of 192x192 tiles to take so 5x5
size = 192  # Size of tile section, don't change

start_x = 31  # Closest upper left start tile x
start_y = 9  # Closest upper left start tile y

img = Image.open("./world_map.png")



cimg = img.crop((
    start_x * size,
    start_y * size,
    (start_x * size) + (sq_size * size),
    (start_y * size) + (sq_size * size)
))
cimg.save("./split/varrock_area.png")