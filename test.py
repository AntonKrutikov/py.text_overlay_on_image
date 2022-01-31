from turtle import width
from PIL import Image, ImageDraw, ImageFont
import csv
import random
import math

from sklearn.metrics import consensus_score
from image_util import ImageText
from itertools import cycle

min_width = 100
min_height = 32
max_width = 512
max_height = 128

def divide(rectangles:list):
    x,y,width,height = rectangles[-1]
    orientation = random.choice(['h','w'])
    proportion = random.choice([2,4])
    if orientation == 'w':
        median = width / proportion
        if median < min_width:
            return
        one = (x,y,math.ceil(median), height)
        two = (x+math.ceil(median), y, width - math.ceil(median), height)
    elif orientation == 'h':
        median = height / proportion
        if median < min_height:
            return
        one = (x,y,width, math.ceil(median))
        two = (x, y+math.ceil(median), width, height-math.ceil(median))
    rectangles.pop()
    rectangles.append(one)
    rectangles.append(two)
    # sort it to future use
    rectangles.sort(key=lambda rec: rec[2]*rec[3])

img = Image.new(mode='RGBA', size=(1000,1000), color="#fff")
rectangles = [(0,0,1000,1000)]

count = 1
news = []
with open('news.csv', encoding='unicode_escape') as csv_file:
    reader = csv.reader(csv_file, delimiter=';')
    for row in reader:
        news.append("%s (%s)" % (row[0], row[1]))
        count+=1

# for i in range(15):
#     divide(rectangles)
rectangles = [(0,0,250,250),(250,0,250,250),(500,0,250,250), (750,0,250,250)]

i = 0
# lines.sort(key=lambda l: len(l), reverse=False)
pad = 20
for rect in rectangles:
    text = news[i]
    i+=1
    x,y,w,h = rect
    draw = ImageDraw.Draw(img)
    x,y,w,h = rect
    draw.rectangle((x,y,x+w-2,y+h-2), fill="rgba(0,0,0,0)", outline="#fff", width=1)
    font_size = max(min(math.ceil(h / 5), math.ceil(w / 10)), 12)
    font = ImageFont.truetype('Roboto-Regular.ttf', font_size)
    lines = []
    line_words = []
    tail = None
    for word in text.split():
        if tail is not None:
           line_words.append(tail)
           tail = None
        else:
            line_words.append(word)
        lw, lh = font.getsize(' '.join(line_words))
        if lw > w:
            tail = line_words.pop()
            lines.append(line_words.copy())
            line_words = []
    lines.append(line_words)

    ty = y
    print(text, len(lines))
    for line in lines:
        t = ' '.join(line)
        tw, th = font.getsize(t)
        # if (ty+th) <= y+h:
        draw.text((x,ty), t, fill="#fff", font=font)
        tw, th = font.getsize(t)
        ty += th
    # text_area = ImageText((w, h), background="rgba(0,0,0,0)") 
    # text_area.write_text_box((pad, pad), text, box_width=w-pad, font_filename='Roboto-Regular.ttf', font_size=font_size, color="#fff", place='justify', position='middle')
    # img.paste(text_area.image, (x,y))
   

img.save("test.png")