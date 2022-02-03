from PIL import Image, ImageDraw, ImageFont
import csv
import random
from matplotlib.pyplot import draw
from rectpack import newPacker
import rectpack

img_path = "input_car.jpeg"
# available font sizes and them weights (how often random choice that one)
# Examples:
# font_sizes = [12,20,64]
# font_weights = [70,20,10]
font_sizes = [8,10,12,14,16,18,20,22,24,26,28,32,40,64]
font_weights = [2,2,2,2,2,2,2,1,1,1,1,0.5,0.5,0.5]
font_name = "Roboto-Regular.ttf"

news_posts=[]
with open('news.csv', encoding='unicode_escape') as csv_file:
    reader = csv.reader(csv_file, delimiter=';')
    for row in reader:
        news_posts.append("%s (%s)" % (row[0], row[1]))
    for row in reader:
        news_posts.append("%s" % (row[1]))
random.shuffle(news_posts)


news= []
id = 0
for post in news_posts:
    font_size = random.choices(population=font_sizes, weights=font_weights, k=1)[0]
    font = ImageFont.truetype(font_name, font_size)
    size = font.getsize(post)
    news.append({"text": post, "font_size": font_size, "size": size, "id": id})
    id+=1


bg = Image.open(img_path).convert("RGBA")
img = Image.new(size=(bg.size[0] + 256, bg.size[1]), mode="RGBA", color="rgba(0,0,0,255)")
draw = ImageDraw.Draw(img)

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

all_rects = packer.rect_list()
for rect in all_rects:
    b, x, y, w, h, rid = rect
    post = [post for post in news if post['id'] == rid][0]
    print(w,h, post['size'],post['font_size'])
    font = ImageFont.truetype(font_name, post['font_size'])
    # draw.rectangle((x,y,x+w,y+h), fill="#000", outline="#aaa")
    draw.text((x,y),post['text'], "rgba(255,255,255,20)", font)
img = img.crop(box=(0,0,img.width - 256,img.height))
bg = Image.alpha_composite(bg, img)
bg.save("rectpack.png")