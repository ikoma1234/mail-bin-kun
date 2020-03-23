import sys
import math
import numpy as np
import cv2
from matplotlib import pyplot as plt
import PIL
from PIL import Image, ImageChops
from PIL import ImageEnhance
from PIL import ImageDraw

IMG_SRC = 'test3.jpg'

THRESH_MIN, THRESH_MAX = (0, 255)
THRESH_MODE = cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU

FRAME = 300
CENTERING = False
PADDING = 30

BG_COLOR = (255, 255, 255)
BORDER_COLOR = (255, 255, 255)
BORDER_WIDTH = 0

AA = (1001, 1001)
CONTRAST = 1.1
SHARPNESS = 1.5
BRIGHTNESS = 1.1
SATURATION = 1.0
GAMMA = 1.0

IMG_NAME = 'output'
IMG_TYPE = 'JPEG'
IMG_QUALITY = 100
IMG_OPTIMIZE = True

img_src = cv2.imread(IMG_SRC)
img_gray = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)
img_bin = cv2.threshold(img_gray, THRESH_MIN, THRESH_MAX, THRESH_MODE)[1]
img_mask = cv2.merge((img_bin, img_bin, img_bin))

mask_rows, mask_cols, mask_channel = img_mask.shape
min_x = mask_cols
min_y = mask_rows
max_x = 0
max_y = 0

# for y in range(mask_rows):
#     for x in range(mask_cols):
#         if all(img_mask[y, x] == 255):
#             if x < min_x:
#                 min_x = x
#             elif x > max_x:
#                 max_x = x
#                 if y < min_y:
#                     min_y = y
#                 elif y > max_y:
#                     max_y = y

img_src_ = Image.fromarray(img_src)
# getpixel(0, 0) で左上の色を取得し、背景色のみの画像を作成する
bg = Image.new(img_src_.mode, img_src_.size, img_src_.getpixel((0, 0)))

# 背景色画像と元画像の差分を取得
diff = ImageChops.difference(img_src_, bg)
# diff.show()
diff = ImageChops.add(diff, diff, 2.0, -100)
# diff.show()
# 黒背景の境界Boxを取り出す
bbox = diff.getbbox()

offset = 20
bbox2 = (bbox[0] - offset, bbox[1] - offset,
         bbox[2] + offset, bbox[3] + offset)

rect_x = bbox2[0]
rect_y = bbox2[1]
rect_w = bbox2[2]
rect_h = bbox2[3]

mask = np.zeros(img_src.shape[:2], np.uint8)

bg_model = np.zeros((1, 65), np.float64)
fg_model = np.zeros((1, 65), np.float64)

rect = bbox

cv2.grabCut(img_src, mask, rect, bg_model, fg_model, 5, cv2.GC_INIT_WITH_RECT)
mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

img_grab = img_src * mask2[:, :, np.newaxis]
img_src_size = img_src.shape
img_bg = np.zeros(img_src_size, dtype=np.uint8)
img_bg[:] = BG_COLOR
img_bg = img_bg * (1 - mask2[:, :, np.newaxis])
img_blend = cv2.addWeighted(img_grab, 0.8, img_bg, 1, 0)

# cv2.imshow('image', img_blend)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


if CENTERING:
    img_rect = img_blend[rect_y: rect_y + rect_h, rect_x: rect_x + rect_w]
else:
    img_rect = img_blend
    rect_w, rect_h = img_rect.shape[:2]

rect_max = max([rect_w, rect_h])
rect_min = min([rect_w, rect_h])

temp_rect_max = FRAME - (PADDING * 2)
resize_rate = temp_rect_max / rect_max
temp_padding = int(PADDING / resize_rate)
temp_frame_max = rect_max + (temp_padding * 2)
img_temp = np.zeros([temp_frame_max, temp_frame_max, 3], dtype=np.uint8)
img_temp[:] = BG_COLOR

min_start = int((rect_max + (temp_padding * 2) - rect_min) / 2)

if rect_w <= rect_h:
    img_temp[min_start: min_start + rect_w,
             temp_padding: temp_padding + rect_h] = img_rect
else:
    img_temp[temp_padding: temp_padding + rect_w,
             min_start: min_start + rect_h] = img_rect

img_aa = cv2.GaussianBlur(img_temp, AA, cv2.BORDER_TRANSPARENT)
if GAMMA != 1.0:
    Y = np.ones((256, 1), dtype='uint8') * 0
    for i in range(256):
        Y[i][0] = 255 * pow(float(i) / 255, 1.0 / GAMMA)
        img_temp = cv2.LUT(img_temp, Y)

        img_aa = cv2.LUT(img_aa, Y)

img_front = Image.fromarray(cv2.cvtColor(
    img_temp, cv2.COLOR_BGR2RGB)).convert('RGBA')

img_back = Image.fromarray(cv2.cvtColor(
    img_aa, cv2.COLOR_BGR2RGB)).convert('RGBA')

img_trans = Image.new('RGBA', img_front.size, (0, 0, 0, 0))

width = img_front.size[0]
height = img_front.size[1]

bg_1, bg_2, bg_3 = BG_COLOR

for x in range(width):
    for y in range(height):
        pixel = img_front.getpixel((x, y))
        if pixel[0] == bg_1 and pixel[1] == bg_2 and pixel[2] == bg_3:
            continue
        img_trans.putpixel((x, y), pixel)

img_front = Image.new('RGBA', img_back.size, (bg_3, bg_2, bg_1, 0))
img_front.paste(img_trans, (0, 0), img_trans)

img_dest = Image.alpha_composite(img_back, img_front)
img_dest = img_dest.resize((FRAME, FRAME), Image.ANTIALIAS)

if CONTRAST != 1.0:
    img_dest = ImageEnhance.Contrast(img_dest)
    img_dest = img_dest.enhance(CONTRAST)

if SHARPNESS != 1.0:
    img_dest = ImageEnhance.Sharpness(img_dest)
    img_dest = img_dest.enhance(SHARPNESS)

if BRIGHTNESS != 1.0:
    img_dest = ImageEnhance.Brightness(img_dest)
    img_dest = img_dest.enhance(BRIGHTNESS)

if SATURATION != 1.0:
    img_dest = ImageEnhance.Color(img_dest)
    img_dest = img_dest.enhance(SATURATION)

if BORDER_WIDTH:
    border_half = BORDER_WIDTH / 2
    floor = math.floor(border_half)
    ceil = FRAME - math.ceil(border_half)
    draw = ImageDraw.Draw(img_dest)
    draw.line((0, floor)+(FRAME, floor), fill=BORDER_COLOR, width=BORDER_WIDTH)
    draw.line((ceil, 0)+(ceil, FRAME), fill=BORDER_COLOR, width=BORDER_WIDTH)
    draw.line((FRAME, ceil)+(0, ceil), fill=BORDER_COLOR, width=BORDER_WIDTH)
    draw.line((floor, FRAME)+(floor, 0), fill=BORDER_COLOR, width=BORDER_WIDTH)

if IMG_TYPE == 'JPEG':
    extension = 'jpg'
elif IMG_TYPE == 'PNG':
    extension = 'png'
elif IMG_TYPE == 'GIF':
    extension = 'gif'
elif IMG_TYPE == 'BMP':
    extension = 'bmp'

rgb_im = img_dest.convert('RGB')

rgb_im.save(IMG_NAME + '.' + extension, IMG_TYPE,
            quality=IMG_QUALITY, optimize=IMG_OPTIMIZE)

sys.exit()
