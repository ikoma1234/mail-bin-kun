import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox

from PIL import Image
from tkinter import ttk

window = tk.Tk()
window.resizable(False, False)

window.title("メール便君")
window.geometry('600x400')

fYtp =[("", "*.png")]

fileName = ""

def chooseFile():
    global fileName 
    fileName = tkinter.filedialog.askopenfilename(filetypes = [("","*.png"), ("", "*.jpg")])
   
    fileDone=tk.Label(text=fileName)
    fileDone.place(x=10,y=120-5)

def makeImage():
    basewidth=300

    im1 = Image.open(fileName).convert("RGBA")
    if(im1.size[0]<=im1.size[1]):
        im1 = im1.resize(im1.size[0]*(300/im1.size[1]), 300)
    else:
        im1 = im1.resize(300, im1.size[1]*(300/im1.size[0]))

    if(siteCombo.get()=="楽天"):
        im2 = Image.open("Rakuten/Rakuten_format.png")
        if(haisouCombo.get()=="送料無料"):
            im3 = Image.open("Rakuten/Rakuten_freeshipping.png")
            im2.paste(im3, (0,0), im3)
    elif(siteCombo.get()=="Yahoo"):
        im2 = Image.open("Yahoo/Yahoo_format.png")
        if(haisouCombo.get()=="送料無料"):
            im3 = Image.open("Yahoo/Yahoo_freeshippingandmail.png")
            im2.paste(im3, (0,0), im3)

    im1.paste(im2, (0, 0), im2)
    im1.show()

titleLabel=tk.Label(text="メール便君", font=("Helvetica", 20))
titleLabel.place(x=240, y=10)
    
fileButton=tk.Button(window, text="ファイル選択", command=chooseFile)
fileButton.place(x=10,y=70-5)

filesYet=tk.Label(text="*ファイルが未選択です*")
filesYet.place(x=10,y=120-5)

haisouLabel=tk.Label(text="配送方法選択")
haisouLabel.place(x=10,y=170-5)

haisouCombo=ttk.Combobox(state="readonly", values=["送料無料", "送料別"])
haisouCombo.place(x=150,y=170-5)

kosuuLabel=tk.Label(text="個数(1~30)")
kosuuLabel.place(x=10,y=220-5)

testList=["1", "2", "3"]

kosuuCombo=ttk.Combobox(state="readonly", values=testList)
kosuuCombo.place(x=150,y=220-5)

siteLabel=tk.Label(text="サイト選択")
siteLabel.place(x=10,y=270-5)

siteCombo=ttk.Combobox(state="readonly", values=["楽天", "Yahoo"])
siteCombo.place(x=150,y=270-5)

p5Label=tk.Label(text="ポイント5倍")
p5Label.place(x=10,y=320-5)

p5ChButton=tk.Checkbutton()
p5ChButton.place(x=150,y=320-5)

seiseiButton=tk.Button(text="  生成  ", font=("Helvetica", 15), command=makeImage)
seiseiButton.place(x=270,y=350-5)

tk.mainloop()