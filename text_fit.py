import random
from PIL import Image, ImageFont, ImageDraw, ImageOps
from typing import Tuple, List, Dict
import csv
import math


bg = Image.open('input_car.jpeg').convert("RGBA")
img = Image.new(size=(bg.width,bg.height), mode='RGBA', color="rgba(0,0,0,0)")
cols = 8
rows = 16

def trans_paste(bg_img,fg_img,box=(0,0)):
    fg_img_trans = Image.new("RGBA",bg_img.size)
    fg_img_trans.paste(fg_img,box,mask=fg_img)
    new_img = Image.alpha_composite(bg_img,fg_img_trans)
    return new_img

def can_fit(size:Tuple[int,int], text:str, font_size:int, font_name:str)->Tuple[bool,List[Dict]]:
    """Try to fit given text with font in sized box"""

    width, height = size
    lines = []
    lines_heights = []
    line = []
    words = text.split()
    font = ImageFont.truetype(font_name, font_size)
    tail = None
    for word in words:
        line.append(word)
        line_width, line_height = font.getsize(' '.join(line))
        if line_height > height:
            return False, None
        if line_width > width:
            tail = line.pop()
            lines.append(line.copy())
            line=[tail]
            lines_heights.append(line_height)
            if sum(lines_heights) > height:
                return False, None
    # last line
    if len(line) > 0:
        line_width, line_height = font.getsize(' '.join(line))
        if line_width > width:
            return False, None
        lines_heights.append(line_height)
        if sum(lines_heights) > height:
            return False, None
        else:
            lines.append(line)

    return True, lines

def get_block(grid):
    for row in grid:
        for col in row:
            if col['free'] == True:
                col['free'] = False
                return col
    return None

grid = []

for i in range(rows):
    height = img.height / rows 
    if height * (i+1) > img.height:
        height = img.height - height * i
    grid.append([])
    for j in range(cols):
        width = img.width / cols
        if width * (j+1) > img.width:
            width = img.width - width * j
        grid[i].append([])
        x = j * width
        y = i * height
        grid[i][j] = {'x': x, 'y': y, 'width': width, 'height': height, 'free': True}

text = """С Александром Агапитовым и компанией Xsolla связан серьезный скандал, когда по анализу активности в рабочих мессенджерах, системах управления проектами и просто активности в сети компании было уволено около 150 человек.  

На критику со стороны общественности и уволенных работников сам Агапитов заявил, что данные сотрудники «невовлечённые и малопродуктивные» и не нужны компании. Причем в список «неэффективных» попали даже оффлайн-работники: грузчики и бариста. Скандал продолжался несколько месяцев, но к концу 2021 года угас.

Xsolla — компания, основанная Александром Агапитовым в 2005 году в Перми под названием 2Pay. В 2010 была переименована в Xsolla."""

text2 = "Some short news"

news=[]
with open('news.csv', encoding='unicode_escape') as csv_file:
    reader = csv.reader(csv_file, delimiter=';')
    for row in reader:
        news.append("%s (%s)" % (row[0], row[1]))
random.shuffle(news)

# grid[6][2]['free'] = False
# grid[7][2]['free'] = False

have_blocks = True
for text in news:
    base_font_size = random.choices(population=[8,16,20], k=1)[0]
    font_size = base_font_size
    font_name = 'Roboto-Regular.ttf'
    fit, lines = (True, None)
    blocks = []
    block = get_block(grid)
    if block is not None:
        blocks.append(block)
    else:
        have_blocks = False

    while have_blocks:
        # print(blocks)
        width = int(sum([block['width'] for block in blocks]))
        height = blocks[0]['height']#int(sum([block['height'] for block in blocks]))
        while fit:
            fit, lines = can_fit((int(width), int(height)), text, font_size, font_name)
            font_size+=1
        if font_size == base_font_size +1 and fit == False:
            c = random.choice([1,2,3])
            b = []
            for i in range(c):
                temp = get_block(grid)
                if temp is not None:
                    b.append(temp)
            if len(b) > 0:
                blocks += b
            else:
                have_blocks =  False
                break
            fit, lines = (True, None)
            font_size = base_font_size
            continue
        else:
            break

    font = ImageFont.truetype(font_name, font_size - 2)
    fit, lines = can_fit((width, height), text, font_size - 2, font_name)
    if lines and len(blocks)>0:
        x = min(block['x'] for block in blocks)
        y = min(block['y'] for block in blocks)

        # color = random.choice(["rgba(0,0,0,255)","rgba(0,0,0,0)"])
        # fill_color = "rgba(0,0,0,0)" if color == "rgba(255,0,0,0)" else "rgba(255,255,255,0)"
        part = Image.new(size=(math.floor(width)+1,math.floor(height)+1), mode="RGBA", color="rgba(10,10,10,255)")
        draw = ImageDraw.Draw(part)
        ty = 0
        
        for line in lines:
            tx = 0
            if len(line)>0:
                line_without_spaces = ''.join(line)
                w,h = font.getsize(line_without_spaces)
                space_width = (width - w) / (len(line))
                start_x = tx
                for word in line:
                    word_size = font.getsize(word)                 
                # w,h = font.getsize(line_text)
                    draw.text((start_x+10,ty), word, font=font, fill="rgba(255,255,255,0)")
                    start_x += word_size[0] + space_width
            ty += h
        img = trans_paste(img, part,(int(x),int(y)))


bg = Image.alpha_composite(bg, img.convert("RGBA"))

bg.save("text_fit.png")
img.save("test4.png")