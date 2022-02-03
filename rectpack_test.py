from PIL import Image, ImageDraw, ImageFont
import csv
import random
from matplotlib.pyplot import draw
from rectpack import newPacker
import rectpack
import math

Image.MAX_IMAGE_PIXELS = None

img_path = "example.jpeg"
# available font sizes and them weights (how often random choice that one)
# Examples:
# font_sizes = [12,20,64]
# font_weights = [70,20,10]
font_sizes = [8,12,16,24,64]
font_weights = [5,5,5,1,0.5]
font_name = "Arial"
# anchor for drawing (lt is better then default la I think)
anchor= "lt"
# Hack to reduce bounding box of text with font greater then
big_font_size_after = 30
big_font_size_reduce_factor = 0.75
# modes
# 'paste' - works like overlay, more whatermark style
# 'composite' - composite by alpha chanel with temp layer (better, default)
mode = 'composite'
bg_color = "rgba(0,0,0,255)" #color under text (default black not transparent)
font_color = "rgba(255,255,255,0)" #full transparent for effect like lookig through window
# multiple news array by (because for big images it can be not enough) have effect on performance
# Note hack: I'm also populate news array fith source (small strings) one more time
news_multiply = 1

news_posts=[]
with open('news.csv', encoding='unicode_escape') as csv_file:
    reader = csv.reader(csv_file, delimiter=';')
    for row in reader:
        news_posts.append("%s (%s)" % (row[0], row[1]))
    for row in reader:
        news_posts.append("%s" % (row[1]))

for i in range(news_multiply):
    news_posts += news_posts

random.shuffle(news_posts)

bg = Image.open(img_path).convert("RGBA")
img = Image.new(size=(bg.size[0] + 256, bg.size[1]), mode="RGBA", color=bg_color)
draw = ImageDraw.Draw(img)

news= []
id = 0
founded = False
for i,post in enumerate(news_posts):
    font_size = random.choices(population=font_sizes, weights=font_weights, k=1)[0]
    font = ImageFont.truetype(font_name, font_size)
    size = font.getsize(post)
    if font_size>big_font_size_after:
        size = (size[0], math.ceil(big_font_size_reduce_factor*size[1]))
    news.append({"text": post, "font_size": font_size, "size": size, "id": id})
    id+=1

print("Text Measurement complete\nStart packing")

rectangles = [(post['size'][0],post['size'][1],post['id']) for post in news]
bins = [img.size]

packer = newPacker(rotation=False, sort_algo=rectpack.SORT_NONE)

# Add the rectangles to packing queue
for r in rectangles:
    packer.add_rect(*r)

# Add the bins where the rectangles will be placed
for b in bins:
	packer.add_bin(*b)

# Start packing
packer.pack()

print("Packing complete\nStart drawing")

def trans_paste(bg_img,fg_img,box=(0,0)):
    fg_img_trans = Image.new("RGBA",bg_img.size)
    fg_img_trans.paste(fg_img,box,mask=fg_img)
    new_img = Image.alpha_composite(bg_img,fg_img_trans)
    return new_img

all_rects = packer.rect_list()
for rect in all_rects:
    b, x, y, w, h, rid = rect
    post = [post for post in news if post['id'] == rid][0]
    # print(w,h, post['size'],post['font_size'])
    font = ImageFont.truetype(font_name, post['font_size'])
    # draw.rectangle((x,y,x+w,y+h), fill="#000", outline="#aaa")
    draw.text((x,y),post['text'], fill=font_color, font=font, anchor=anchor)
img = img.crop(box=(0,0,img.width - 256,img.height))

if mode == 'composite':
    bg = trans_paste(bg,img)
else:
    bg.paste(img, (0,0), img)

bg.save("rectpack.png")