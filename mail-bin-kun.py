import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import cv2
import numpy as np
import os

from PIL import Image, ImageChops
from tkinter import ttk

from os.path import expanduser

app = tk.Tk()
app.resizable(True, True)

app.title("メール便君")
app.geometry('600x600')


fYtp = [("", "*.png")]

fileName = ""
savefolderName = ""

PADDING = 20

# FRAME bbox cordinates
RAKUTEN_FRAME_X = 0
RAKUTEN_FRAME_Y = 55
RAKUTEN_FRAME_WIDTH = 300
RAKUTEN_FRAME_HEIGHT = 244
YAHOO_FRAME_X = 6
YAHOO_FRAME_Y = 58
YAHOO_FRAME_WIDTH = 285
YAHOO_FRAME_HEIGHT = 191


def autocrop(image):

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
    # cropped = image.crop(bbox)
    # cropped.save('cropped_edge.jpg')
    cropped = image.crop(bbox2)
    # cropped.save('cropped_edge_offset.jpg')

    return cropped


def chooseFile():
    global fileName
    fileName = tkinter.filedialog.askopenfilename(
        filetypes=[("", "*.png"), ("", "*.jpg")])

    fileDone = tk.Label(frame_3, text=fileName)
    fileDone.grid(column=0, row=0, padx=5, pady=15)


def chooseFolder():
    global savefolderName
    savefolderName = tkinter.filedialog.askdirectory(
        title="保存先フォルダを選択", mustexist=True, initialdir=os.getcwd())

    savefolderName = savefolderName + os.sep
    folderDone = tk.Label(frame_3, text=savefolderName)
    folderDone.grid(column=0, row=2, padx=5, pady=15)


# resize cropped image
def scale_to_width(img, width):
    height = round(img.height * width / img.width)
    return img.resize((width, height), Image.LANCZOS)


def scale_to_height(img, height):
    width = round(img.width * height / img.height)
    return img.resize((width, height), Image.LANCZOS)


def item2frame(item_image, bg, site="Rakuten"):
    if (site == "Rakuten"):
        FRAME_X = RAKUTEN_FRAME_X
        FRAME_Y = RAKUTEN_FRAME_Y
        FRAME_WIDTH = RAKUTEN_FRAME_WIDTH
        FRAME_HEIGHT = RAKUTEN_FRAME_HEIGHT
    elif (site == "Yahoo"):
        FRAME_X = YAHOO_FRAME_X
        FRAME_Y = YAHOO_FRAME_Y
        FRAME_WIDTH = YAHOO_FRAME_WIDTH
        FRAME_HEIGHT = YAHOO_FRAME_HEIGHT
    frame = bg.copy()
# get image width and height
    im_width, im_height = item_image.size

    # print(im_width, im_height)

    if im_width >= im_height:
        scaled_im1 = scale_to_width(item_image, FRAME_WIDTH)
        # get center coordinates
        w_c, h_c = scaled_im1.size
        x = 0
        y = (FRAME_HEIGHT - h_c) // 2

    else:
        scaled_im1 = scale_to_height(item_image, FRAME_HEIGHT)
        # get center coodinates
        w_c, h_c = scaled_im1.size
        x = (FRAME_WIDTH - w_c)//2
        y = 0

    frame.paste(scaled_im1, (FRAME_X+x, FRAME_Y+y))

    # frame.show()
    return frame


def save_img(img, type="", quantity=1):
    img.load()  # required for png.split()

    bg = Image.new("RGB", img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[3])  # 3 is the alpha channel

    save_path = ""

    if type != "" and quantity > 1:
        save_path = savefolderName + janTxt.get() + "-" + str(quantity) + \
            "set-" + type + ".jpg"
    elif type != "":
        save_path = savefolderName + janTxt.get() + "-" + type + ".jpg"
    elif type == "" and quantity > 1:
        save_path = savefolderName + janTxt.get() + "-" + str(quantity) + "set.jpg"
    else:
        save_path = savefolderName + janTxt.get() + ".jpg"

    bg.save(save_path, "JPEG", quality=95)


def makeImage():

    # check jan

    if janTxt.get() == "":
        tkinter.messagebox.showerror(title="Error", message="JANコードを入力してください。")
        return

    # check shipping method
    if (normalVal.get() == True and mailVal.get() == True) or (normalVal.get() == False and mailVal.get() == False):
        tkinter.messagebox.showerror(
            title="Error", message="配送方法は一つだけチェックしてください。")
        return

    # check file

    if fileName == "":
        tkinter.messagebox.showerror(title="Error", message="ファイルを選択してください。")
        return

    #check folder

    if savefolderName == "":
        tkinter.messagebox.showerror(title="Error", message="保存先フォルダを選択してください。")
        return

    #check site

    if rakutenVal.get() == False and yahooVal.get() == False:
        tkinter.messagebox.showerror(title="Error", message="サイト名を選択してください。")
        return
    basewidth = 300

    im1 = Image.open(fileName).convert("RGBA")
    bg = Image.new('RGBA', (basewidth, basewidth), "white")

    # crop image
    cropped_im1 = autocrop(im1)

    # get quantity
    quantity = []

    for i in range(len(Check_list_val)):
        if Check_list_val[i].get() == True:
            quantity.append(i+1)

    if(rakutenVal.get() == True):
        if (mailVal.get() == True):
            for x in quantity:
                if (x != 1):
                    frame = bg.copy()
                    im_freeshipping = Image.open(
                        "./images/rakuten/freeshipping.png")
                    # 個数取得、対応画像を名前で取得
                    im_kosuu = Image.open(
                        "./images/rakuten/mail" + str(x) + "set.png")

                    final_img_1 = item2frame(cropped_im1, frame)

                    im_freeshipping.paste(im_kosuu, (0, 0), im_kosuu)
                    final_img_1.paste(im_freeshipping, (0, 0), im_freeshipping)

                    save_img(final_img_1, typeCombo.get(), x)

                else:
                    frame = bg.copy()
                    im_mail = Image.open("./images/rakuten/mail.png")
                    # メール便だったら自動で送料無料
                    im_freeshipping = Image.open(
                        "./images/rakuten/freeshipping.png")

                    final_img_2 = item2frame(cropped_im1, frame)

                    im_mail.paste(im_freeshipping, (0, 0), im_freeshipping)

                    final_img_2.paste(im_mail, (0, 0), im_mail)

                    save_img(final_img_2, typeCombo.get())

        elif (normalVal.get() == True):
            frame = bg.copy()
            for x in quantity:
                if x != 1 and freeshippingVal.get() != True:
                    im_kosuu = Image.open("./images/rakuten/"+str(x)+".png")
                    final_img_3 = item2frame(cropped_im1, frame)
                    final_img_3.paste(im_kosuu, (0, 0), im_kosuu)
                    save_img(final_img_3, typeCombo.get(), x)

                elif x != 1 and freeshippingVal.get() == True:
                    im_freeshipping = Image.open(
                        "./images/rakuten/freeshipping.png")
                    im_kosuu = Image.open("./images/rakuten/"+str(x)+".png")

                    final_img_3 = item2frame(cropped_im1, frame)
                    final_img_3.paste(im_freeshipping, (0, 0), im_freeshipping)
                    final_img_3.paste(im_kosuu, (0, 0), im_kosuu)

                    save_img(final_img_3, typeCombo.get(), x)

                else:
                    final_img_3 = item2frame(cropped_im1, frame)

                    save_img(final_img_3, typeCombo.get(), x)

    elif(yahooVal.get() == True):
        if (mailVal.get() == True):
            for x in quantity:
                if (x != 1):
                    frame = bg.copy()
                    im_freeshipping = Image.open(
                        "./images/yahoo/mail.png")
                    # 個数取得、対応画像を名前で取得
                    im_kosuu = Image.open(
                        "./images/yahoo/" + str(x) + "set.png")

                    final_img_1 = item2frame(cropped_im1, frame, "Yahoo")

                    im_freeshipping.paste(im_kosuu, (0, 0), im_kosuu)
                    final_img_1.paste(im_freeshipping, (0, 0), im_freeshipping)

                    save_img(final_img_1, typeCombo.get(), x)

                else:
                    frame = bg.copy()
                    im_mail = Image.open("./images/yahoo/mail.png")

                    final_img_2 = item2frame(cropped_im1, frame, "Yahoo")

                    final_img_2.paste(im_mail, (0, 0), im_mail)

                    save_img(final_img_2, typeCombo.get())

        elif (normalVal.get() == True):
            frame = Image.open("./images/yahoo/normal.png")
            for x in quantity:
                if x != 1 and freeshippingVal.get() != True:
                    im_kosuu = Image.open("./images/yahoo/"+str(x)+".png")
                    final_img_3 = item2frame(cropped_im1, frame)
                    final_img_3.paste(im_kosuu, (0, 0), im_kosuu)
                    save_img(final_img_3, typeCombo.get(), x)

                elif x != 1 and freeshippingVal.get() == True:
                    im_freeshipping = Image.open(
                        "./images/yahoo/freeshipping.png")
                    im_kosuu = Image.open("./images/yahoo/"+str(x)+".png")

                    final_img_3 = item2frame(cropped_im1, frame)
                    final_img_3.paste(im_freeshipping, (0, 0), im_freeshipping)
                    final_img_3.paste(im_kosuu, (0, 0), im_kosuu)

                    save_img(final_img_3, typeCombo.get(), x)

                else:
                    final_img_3 = item2frame(cropped_im1, frame)

                    save_img(final_img_3, typeCombo.get(), x)


titleLabel = tk.Label(text="メール便君", font=("Helvetica", 20))
titleLabel.grid(column=0, row=0, pady=10, sticky=tk.W + tk.E)

frame_1 = tk.LabelFrame(app)
frame_1.grid(row=1, column=0, sticky=tk.W + tk.E, padx=20)
frame_2 = tk.LabelFrame(app)
frame_2.grid(row=2, column=0, sticky=tk.W + tk.E, padx=20)
frame_3 = tk.LabelFrame(app)
frame_3.grid(row=3, column=0, sticky=tk.W + tk.E, padx=20)
frame_4 = tk.LabelFrame(app)
frame_4.grid(row=4, column=0, sticky=tk.W + tk.E, padx=20)

fileButton = tk.Button(frame_3, text="ファイル選択", command=chooseFile)
fileButton.grid(column=0, row=1, padx=10, pady=10, sticky=tk.E)

filesYet = tk.Label(frame_3, text="*ファイルが未選択です*")
filesYet.grid(column=0, row=0, padx=50, pady=10, sticky=tk.W)

folderButton = tk.Button(frame_3, text="保存先フォルダ選択", command=chooseFolder)
folderButton.grid(column=0, row=3, padx=10, pady=10, sticky=tk.E)

folderYet = tk.Label(frame_3, text="*保存先フォルダが未選択です*")
folderYet.grid(column=0, row=2, padx=50, pady=10, sticky=tk.W)

siteLabel = tk.Label(frame_1, text="サイト名")
siteLabel.grid(column=0, row=3, padx=10, pady=10, sticky=tk.W)

# check box
rakutenVal = tk.BooleanVar()
yahooVal = tk.BooleanVar()

rakutenVal.set(True)
yahooVal.set(True)

chkRakuten = ttk.Checkbutton(frame_1, text=u"Rakuten", variable=rakutenVal)
chkRakuten.grid(column=1, row=3, padx=10, pady=10, sticky=tk.W + tk.E)

chkYahoo = ttk.Checkbutton(frame_1, text=u"Yahoo", variable=yahooVal)
chkYahoo.grid(column=2, row=3, padx=10, pady=10, sticky=tk.W + tk.E)

deliveryLabel = tk.Label(frame_1, text="配送方法")
deliveryLabel.grid(column=0, row=4, padx=10, pady=10, sticky=tk.W)

mailVal = tk.BooleanVar()
normalVal = tk.BooleanVar()

mailVal.set(True)
normalVal.set(False)

typeLabel = tk.Label(frame_1, text="メール便種類")
typeCombo = ttk.Combobox(frame_1, state="readonly", values=[
    "tkg", "kkn", "ypt", "nko"], width=10)
typeLabel.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W + tk.E)
typeCombo.grid(row=5, column=1, padx=10, pady=10, sticky=tk.W)


def activateTypebox():
    if mailVal.get() == True:
        typeCombo.config(state="readonly")
    else:
        typeCombo.config(state=tk.DISABLED)


chkMail = ttk.Checkbutton(frame_1, text=u"メール便",
                          variable=mailVal, command=activateTypebox)
chkMail.grid(column=1, row=4, padx=10, pady=10, sticky=tk.W + tk.E)

chkNormal = ttk.Checkbutton(
    frame_1, text=u"普通便", variable=normalVal, command=activateTypebox)
chkNormal.grid(column=2, row=4, padx=10, pady=10, sticky=tk.W + tk.E)


freeshippingLabel = tk.Label(frame_1, text="送料")
freeshippingLabel.grid(column=0, row=6, padx=10, pady=10, sticky=tk.W)

freeshippingVal = tk.BooleanVar()
freeshippingVal.set(True)


chkFreeshipping = ttk.Checkbutton(
    frame_1, text=u"無料", variable=freeshippingVal)
chkFreeshipping.grid(column=1, row=6, padx=10, pady=10, sticky=tk.W + tk.E)


quantityLabel = tk.Label(frame_2, text="個数")
quantityLabel.grid(column=0, row=5, padx=10, pady=10, sticky=tk.W)

Check_list = []
Check_list_val = []
Check_buttn_number = 10

for i in range(Check_buttn_number):
    Check_val = tk.BooleanVar()
    Check_val.set(True)
    if(i < 5):
        Check_buttn = tk.Checkbutton(frame_2, text=str(
            len(Check_list) + 1), variable=Check_val)
    else:
        Check_val.set(False)
        Check_buttn = tk.Checkbutton(frame_2, text=str(
            len(Check_list) + 1), variable=Check_val)
    Check_buttn.grid(column=i+1, row=5, padx=5, pady=10, sticky=tk.W)
    Check_list.append(Check_buttn)
    Check_list_val.append(Check_val)

janLabel = tk.Label(frame_4, text=u"JANコード")
janLabel.grid(column=0, row=0, padx=10, pady=10)

janTxt = tk.Entry(frame_4, width=30)
janTxt.grid(column=1, row=0, padx=10, pady=10)

createButton = tk.Button(text="  画像生成  ", font=(
    "Helvetica", 15), command=makeImage)
createButton.grid(column=0, row=5, padx=10, pady=10,
                  sticky=tk.S)

tk.mainloop()
