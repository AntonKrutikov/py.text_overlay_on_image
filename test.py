from PIL import Image, ImageDraw, ImageFont
import csv
import random
import math

# Segments
min_width = 1920 / 8
min_height = 1080 / 8
# Divide to
divide_to = 30
# Random font sizes from:
font_size_list = [20,24,32,48]
#Image path
path = 'input_test_2.jpeg'

iterations = 0
def divide(rectangles:list):
    x,y,width,height = rectangles[-1]
    found = False
    while found == False:
        if iterations > 1000:
            break
        orientation = random.choice(['h','w'])
        proportion = random.choice([1,2,3,4,5,6])
        if orientation == 'w':
            median = width / proportion
            if median < min_width:
                continue
            one = (x,y,math.ceil(median), height)
            two = (x+math.ceil(median), y, width - math.ceil(median), height)
            found = True
        elif orientation == 'h':
            median = height / proportion
            if median < min_height:
                continue
            one = (x,y,width, math.ceil(median))
            two = (x, y+math.ceil(median), width, height-math.ceil(median))
            found = True
    rectangles.pop()
    rectangles.append(one)
    rectangles.append(two)
    # sort it to future use
    rectangles.sort(key=lambda rec: rec[2]*rec[3])

def trans_paste(bg_img,fg_img,box=(0,0)):
    fg_img_trans = Image.new("RGBA",bg_img.size)
    fg_img_trans.paste(fg_img,box,mask=fg_img)
    new_img = Image.alpha_composite(bg_img,fg_img_trans)
    return new_img

img = Image.open(path).convert('RGBA')
rectangles = [(0,0,img.width,img.height)]

count = 1
news = []
with open('news.csv', encoding='unicode_escape') as csv_file:
    reader = csv.reader(csv_file, delimiter=';')
    for row in reader:
        news.append("%s (%s)" % (row[0], row[1]))
        count+=1

for i in range(divide_to):
    divide(rectangles)

i = 0
pad = 20
fill_color = "rgba(0,0,0,245)"
font_color = "rgba(255,255,255,0)"

# fill_color = "rgba(0,0,0,0)"
# font_color = "rgba(255,255,255,150)"

for rect in rectangles:
    x,y,w,h = rect

    font_size = random.choice(font_size_list)
    if w < 100:
        font_size = 12

    img2 = Image.new(mode="RGBA", size=(w,h), color=fill_color)
    draw = ImageDraw.Draw(img2)
    font = ImageFont.truetype('Roboto-Regular.ttf', font_size)
    lines = []
    line_words = []
    tail = None
    block_h = 0
    h_found = False
    while h_found == False:
        text = news[i]
        i+=1
        for word in text.split():
            lw, lh = font.getsize(' '.join(line_words))
            if block_h >= h:
                h_found = True
                break
            if tail is not None:
                line_words.append(tail)
                tail = None
            else:
                line_words.append(word)
            
            if lw > w:
                tail = line_words.pop()
                l = line_words.copy()
                w1, h1 = font.getsize(' '.join(l))
                block_h += h1
                if block_h >= h:
                    h_found = True
                    break
                lines.append(line_words.copy())
                line_words = []
    if block_h < h:
        lines.append(line_words)

    ty = 0
    for line in lines:
        t = ' '.join(line)
        tw, th = font.getsize(t)


        draw.text((0+4,ty+4), t, fill=font_color, font=font)
        tw, th = font.getsize(t)
        ty += th + 2
    img = trans_paste(img, img2, (x,y))
   

img.save("test.png")