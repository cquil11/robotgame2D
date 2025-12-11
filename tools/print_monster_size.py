from PIL import Image
from os import path
p = path.join(path.dirname(__file__), '..', 'images', 'monsters', 'monster_scary.png')
img = Image.open(path.abspath(p))
print(f"monster_scary.png size: {img.size[0]}x{img.size[1]} px")
