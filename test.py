from PIL import Image

basewidth=300

im1 = Image.open("Yahoo\Yahoo_freeshipping.png").convert("RGBA")

im2 = Image.open('Lenna.png')
wpercent = (basewidth/float(im2.size[0]))
hsize = int((float(im2.size[1])*float(wpercent)))
im2 = im2.resize((basewidth,hsize), Image.ANTIALIAS)

im2.paste(im1, (0, 0), im1)
im2.show()