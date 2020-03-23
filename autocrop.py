from PIL import Image, ImageChops
import numpy as np
import cv2


PADDING = 10

image = Image.open('./test4.jpg')

# getpixel(0, 0) で左上の色を取得し、背景色のみの画像を作成する
bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))

# 背景色画像と元画像の差分を取得
diff = ImageChops.difference(image, bg)
# diff.show()
diff = ImageChops.add(diff, diff, 2.0, -100)
# diff.show()
# 黒背景の境界Boxを取り出す
bbox = diff.getbbox()
# 少し余白を付ける
offset = PADDING
bbox2 = (bbox[0] - offset, bbox[1] - offset,
         bbox[2] + offset, bbox[3] + offset)
# 元画像を切り出す
cropped = image.crop(bbox)
cropped.save('cropped_edge.jpg')
cropped = image.crop(bbox2)
cropped.save('cropped_edge_offset.jpg')
