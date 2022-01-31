from turtle import width
from PIL import Image, ImageDraw, ImageFont
import csv
import random
import math

from sklearn.metrics import consensus_score
from image_util import ImageText
from itertools import cycle

min_width = 1920 / 10
min_height = 1080 / 10
max_width = 512
max_height = 128

def divide(rectangles:list):
    x,y,width,height = rectangles[-1]
    found = False
    while found == False:
        orientation = random.choice(['h','w'])
        proportion = random.choice([2,4])
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

img = Image.open('example.jpeg').convert('RGBA')
rectangles = [(0,0,img.width,img.height)]

count = 1
news = []
with open('news.csv', encoding='unicode_escape') as csv_file:
    reader = csv.reader(csv_file, delimiter=';')
    for row in reader:
        news.append("%s (%s)" % (row[0], row[1]))
        count+=1

for i in range(20):
    divide(rectangles)
# rectangles = [(0,0,250,250),(250,0,250,250),(500,0,250,250), (750,0,250,250)]

i = 0
# lines.sort(key=lambda l: len(l), reverse=False)
pad = 20
fill_color = "rgba(0,0,0,255)"
font_color = "rgba(255,255,255,0)"

# fill_color = "rgba(0,0,0,0)"
# font_color = "rgba(255,255,255,100)"

for rect in rectangles:
    x,y,w,h = rect

    # draw.rectangle((x,y,x+w-2,y+h-2), fill="rgba(0,0,0,0)", outline="#fff", width=1)
    font_size = random.choice([24,32,48])
    if w < 100:
        font_size = 12

    # if font_size>32:
    #     fill_color = "rgba(0,0,0,100)"
    #     font_color = "rgba(255,255,255,100)"
    # else:
    #     fill_color = "rgba(0,0,0,255)"
    #     font_color = "rgba(255,255,255,0)"
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
    # if block_h < h:
    lines.append(line_words)

    ty = 0
    print(text, len(lines))
    for line in lines:
        t = ' '.join(line)
        tw, th = font.getsize(t)


        draw.text((0+8,ty+8), t, fill=font_color, font=font)
        tw, th = font.getsize(t)
        ty += th + 2
    # text_area = ImageText((w, h), background="rgba(0,0,0,0)") 
    # text_area.write_text_box((pad, pad), text, box_width=w-pad, font_filename='Roboto-Regular.ttf', font_size=font_size, color="#fff", place='justify', position='middle')
    img.paste(img2, (x,y), img2)
   

img.save("test.png")