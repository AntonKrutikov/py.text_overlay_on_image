import csv
import math
import random
import rectpack
from PIL import ImageFont, Image, ImageDraw
from typing import Tuple, List, Dict
from rectpack import newPacker

# CSV
# format_chars used only for second column
def process_row(row, data_column_count:int, format_chars:Tuple[str,str,str]):
    text = ''
    for i in range(data_column_count):
        if len(row[i].strip()) > 0:
            if i == 1:
                text += format_chars[0] + ' ' + row[i] + ' ' + format_chars[1] +' '
            else:
                text += row[i] + ' '
    if text == '':
        return None
    else:
        return text

def csv_load(path:str, data_column_count:int, delimeter:str, encoding:str = 'latin', format_chars:Tuple[str,str,str]=('(',')','|')) -> List[Dict]:
    text = None
    posts = []
    try:
        with open(path, encoding=encoding) as csv_file:
            reader = csv.reader(csv_file, delimiter=delimeter)
            for row in reader:
                text = process_row(row, data_column_count, format_chars)
                if text is not None:
                    posts.append({'text': text})
    # fallback to broken csv encoding
    except UnicodeDecodeError:
        with open(path, encoding='unicode_escape') as csv_file:
            reader = csv.reader(csv_file, delimiter=delimeter)
            for row in reader:
                text = process_row(row, data_column_count, format_chars)
                if text is not None:
                    posts.append({'text': text})
    return posts


# Measure
def measure(news:list, font_name:str, font_sizes:list, font_weights:list = None, big_font:int = 30, scale:float = 0.75) -> List:
    boxes = []
    id = 0
    for post in news:
        text = post['text']
        if 'font_size' in post:
            font_size = post['font_size']
        else:
            font_size = random.choices(population=font_sizes, weights=font_weights, k=1)[0]
        font = ImageFont.truetype(font_name, font_size)
        size = font.getsize(text)
        if font_size>big_font:
            size = (size[0], math.ceil(scale*size[1]))
        boxes.append({"text": text, "font_size": font_size, "size": size, "id": id})
        id+=1
    return boxes

algorithms_dict:Dict = {
    'MaxRectsBl': rectpack.MaxRectsBl, 
    'MaxRectsBssf': rectpack.MaxRectsBssf,
    'MaxRectsBaf': rectpack.MaxRectsBaf, 
    'MaxRectsBlsf': rectpack.MaxRectsBlsf,
    'GuillotineBssfSas': rectpack.GuillotineBssfSas,
    'GuillotineBssfLas': rectpack.GuillotineBssfLas,
    'GuillotineBssfSlas': rectpack.GuillotineBssfSlas, 
    'GuillotineBssfLlas': rectpack.GuillotineBssfLlas, 
    'GuillotineBssfMaxas': rectpack.GuillotineBssfMaxas,
    'GuillotineBssfMinas': rectpack.GuillotineBssfMinas, 
    'GuillotineBlsfSas': rectpack.GuillotineBlsfSas, 
    'GuillotineBlsfLas': rectpack.GuillotineBlsfLas,
    'GuillotineBlsfSlas': rectpack.GuillotineBlsfSlas,
    'GuillotineBlsfLlas': rectpack.GuillotineBlsfLlas,
    'GuillotineBlsfMaxas': rectpack.GuillotineBlsfMaxas,
    'GuillotineBlsfMinas': rectpack.GuillotineBlsfMinas,
    'GuillotineBafSas': rectpack.GuillotineBafSas, 
    'GuillotineBafLas': rectpack.GuillotineBafLas,
    'GuillotineBafSlas': rectpack.GuillotineBafSlas, 
    'GuillotineBafLlas': rectpack.GuillotineBafLlas,
    'GuillotineBafMaxas': rectpack.GuillotineBafMaxas,
    'GuillotineBafMinas': rectpack.GuillotineBafMinas
}

def pack(boxes:List, bins:List, algo = rectpack.MaxRectsBssf, sort = rectpack.SORT_NONE) -> List:
    packer = newPacker(rotation=False, sort_algo=sort, pack_algo=algo)
     # Add the rectangles to packing queue
    for r in boxes:
        packer.add_rect(*r)

    # Add the bins where the rectangles will be placed
    for b in bins:
        packer.add_bin(*b)

    # Start packing
    packer.pack()

    return packer.rect_list()

def trans_paste(bg_img,fg_img,box=(0,0)):
    fg_img_trans = Image.new("RGBA",bg_img.size)
    fg_img_trans.paste(fg_img,box,mask=fg_img)
    new_img = Image.alpha_composite(bg_img,fg_img_trans)
    return new_img

def draw_boxes(img:Image.Image, boxes:List, news:List, font_name:str, font_color:str, anchor:str = 'lt'):
    draw = ImageDraw.Draw(img)
    for box in boxes:
        b, x, y, w, h, rid = box
        post = [post for post in news if post['id'] == rid][0]
        font = ImageFont.truetype(font_name, post['font_size'])
        draw.text((x,y),post['text'], fill=font_color, font=font, anchor=anchor)