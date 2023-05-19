import os 
from PIL import Image

package = ".\\data\\"
files = os.listdir(package)

r1, g1, b1, = 0, 0, 0

for file in files:
	if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jepg"):
		im = Image.open(package+file)
		rgb_im = im.convert('RGB')
		r, g, b = rgb_im.getpixel((1, 1))
		width, height = im.size

		for i in range(width):
			for j in range(height):
				r, g, b = rgb_im.getpixel((i, j))
				r1 += r
				g1 += g 
				b1 += b

		if r1 > b1:
			print(f"{file} = positive")
		else: 
			print(f"{file} negative")
		r1, g1, b1, = 0, 0, 0
