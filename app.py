from pydoc import ispath
import random
from PIL import Image
import os
import time
import configparser
import argparse
from config import create_config
from typing import Tuple, List, Dict
from utils import csv_load, measure, pack, trans_paste, draw_boxes, algorithms_dict

Image.MAX_IMAGE_PIXELS = None

if __name__ == "__main__":
    # Create config if not exists
    if not os.path.exists('config.ini'):
        create_config('config.ini')
    config_file = configparser.ConfigParser()
    config_file.read('config.ini')
    config = config_file['default']

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--test-pack', help='Test all algs other input images', default=False, action='store_true')
    arg_parser.add_argument('-i', '--input', help='Input image file path', metavar='path', action='append')
    arg_parser.add_argument('-out', '--output', help='Path to output folder', metavar='path')
    arg_parser.add_argument('--remeasure', help='Remeasure font-size for each image', default=None, action='store_true')
    arg_parser.add_argument('--shuffle', help='Shuffle news blocks for each image', default=None, action='store_true')
    args = arg_parser.parse_args()

    # Input can be multiple files or multiple folders
    image_paths = args.input or config.get('image_files').split(',')
    image_files = []
    for path in image_paths:
        if not os.path.exists(path):
            print('Notice: Not a real file %s' % path)
            break
        if os.path.isfile(path):
            ext = path.rsplit('.', 1)
            if len(ext) == 2 and ext[1] not in ['jpeg', 'jpg', 'png']:
                print('Notice: Unsupported file format for "%s"' % path)
                break
            image_files.append(path)
        elif os.path.isdir(path):
            for file in os.listdir(path):
                ext = file.rsplit('.', 1)
                if len(ext) ==2 and ext[1] in ['jpeg', 'jpg', 'png']:
                    image_files.append("%s/%s" % (path.rstrip('/'),file))

    if len(image_files) == 0:
        print('No input')
        exit()

    out_dir = args.output or config.get('out_dir')
    # create out if not exists
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    file_path = config.get('text_file')
    columns_count = int(config.get('csv_columns'))
    delimeter = config.get('csv_delimeter')
    encoding = config.get('text_encoding')
    news_multiply_by = int(config.get('news_multiply_by', 1))
    news_shuffle = args.shuffle or bool(config.get('news_shuffle', False))
    font_name = config.get('font')
    font_sizes = [int(size) for size in config.get('font_sizes').split(',')]
    font_weights = [float(weight) for weight in config.get('font_weights').split(',')]
    bg_color = 'rgba(%s)' % config.get('bg_color', '0,0,0,255')
    font_color = 'rgba(%s)' % config.get('font_color', '255,255,255,0')
    mode = config.get('mode', 'composite')
    algorithm = config.get('algorithm', 'MaxRectsBssf')
    file_suffix = config.get('file_suffix')
    img_width_gap = 256
    remeasure = args.remeasure or bool(config.get('news_remeasure', False))


    t = time.process_time()
    news = []
    if file_path.endswith('.csv'):
        news = csv_load(file_path, columns_count, delimeter, encoding)
    
    if news_shuffle == True:
        random.shuffle(news)

    if news_multiply_by > 1:
        for i in range(news_multiply_by-1):
            news+= news

    print("csv loaded %.2fs" % (time.process_time() - t))

    measured = False
    news_boxes = []
    for image in image_files:
        print("\nimage: '%s'" % image)

        if not measured or remeasure:
            t = time.process_time()
            news_boxes = measure(news, font_name, font_sizes, font_weights)
            measured = True
            print("text measured %.2fs" % (time.process_time() - t))
        if news_shuffle:
            random.shuffle(news_boxes)
        

        test_flag = False
        statistic = []
        if args.test_pack == True:
            algs = list(algorithms_dict.values())
            test_flag = True
        else:
            algs = [algorithms_dict[algorithm]]

        text_areas = [(box['size'][0],box['size'][1],box['id']) for box in news_boxes]
        for alg in algs:
            bg = Image.open(image).convert("RGBA")
            # Add some value to width for text covers whole result
            img = Image.new(size=(bg.size[0] + img_width_gap, bg.size[1]), mode="RGBA", color=bg_color)

            bins = [img.size]

            if test_flag == True:
                file_suffix = "_%s" % alg.__name__

            t = time.process_time()
            boxes = pack(text_areas, bins, algo=alg)
            statistic.append({alg.__name__: time.process_time() - t})
            print("rectpack %.2fs" % (time.process_time() - t))

            t = time.process_time()
            draw_boxes(img, boxes, news_boxes, font_name, font_color)
            img = img.crop(box=(0,0,img.width - img_width_gap,img.height))

            if mode == 'composite':
                bg = trans_paste(bg,img)
            else:
                bg.paste(img, (0,0), img)

            file_name = image.split('/')[-1].rsplit('.', 1)[0]
            out_path = "%s/%s%s.png" % (out_dir, file_name, file_suffix )
            bg.save(out_path)
            print("draw %.2fs" % (time.process_time() - t))
            print("saved to %s" % out_path)

        statistic_out_path = "%s/%s_log.txt" % (out_dir, file_name)
        statistic.sort(key=lambda alg: list(alg.values())[0])
        if test_flag == True:
            with open(statistic_out_path, 'w') as f:
                for s in statistic:
                    f.write("%s: %.2fs\n" % tuple(s.items())[0])
    
    # pack

    # TODO: provide file from args

# img_path = "input_avengers.png"
# # available font sizes and them weights (how often random choice that one)
# # Examples:
# # font_sizes = [12,20,64]
# # font_weights = [70,20,10]
# font_sizes = [8,12,16,24,48]
# font_weights = [5,5,5,1,0.25]
# font_name = "Arial"
# # anchor for drawing (lt is better then default la I think)
# anchor= "lt"
# # Hack to reduce bounding box of text with font greater then
# big_font_size_after = 30
# big_font_size_reduce_factor = 0.75
# # modes
# # 'paste' - works like overlay, more whatermark style
# # 'composite' - composite by alpha chanel with temp layer (better, default)
# mode = 'composite'
# bg_color = "rgba(0,0,0,255)" #color under text (default black not transparent)
# font_color = "rgba(255,255,255,0)" #full transparent for effect like lookig through window
# # multiple news array by (because for big images it can be not enough) have effect on performance
# # Note hack: I'm also populate news array fith source (small strings) one more time
# news_multiply = 2

# news_posts=[]
# with open('news.csv', encoding='unicode_escape') as csv_file:
#     reader = csv.reader(csv_file, delimiter=';')
#     for row in reader:
#         news_posts.append("%s (%s)" % (row[0], row[1]))
#     # for row in reader:
#     #     news_posts.append("%s" % (row[1]))

# for i in range(news_multiply-1):
#     news_posts += news_posts

# random.shuffle(news_posts)

# bg = Image.open(img_path).convert("RGBA")
# img = Image.new(size=(bg.size[0] + 256, bg.size[1]), mode="RGBA", color=bg_color)
# draw = ImageDraw.Draw(img)

# news= []
# id = 0
# founded = False
# for i,post in enumerate(news_posts):
#     font_size = random.choices(population=font_sizes, weights=font_weights, k=1)[0]
#     font = ImageFont.truetype(font_name, font_size)
#     size = font.getsize(post)
#     if font_size>big_font_size_after:
#         size = (size[0], math.ceil(big_font_size_reduce_factor*size[1]))
#     news.append({"text": post, "font_size": font_size, "size": size, "id": id})
#     id+=1

# print("Text Measurement complete\nStart packing")

# rectangles = [(post['size'][0],post['size'][1],post['id']) for post in news]
# bins = [img.size]

# packer = newPacker(rotation=False, sort_algo=rectpack.SORT_NONE, pack_algo=rectpack.GuillotineBafLas)

# # Add the rectangles to packing queue
# for r in rectangles:
#     packer.add_rect(*r)

# # Add the bins where the rectangles will be placed
# for b in bins:
# 	packer.add_bin(*b)

# # Start packing
# packer.pack()

# print("Packing complete\nStart drawing")

# def trans_paste(bg_img,fg_img,box=(0,0)):
#     fg_img_trans = Image.new("RGBA",bg_img.size)
#     fg_img_trans.paste(fg_img,box,mask=fg_img)
#     new_img = Image.alpha_composite(bg_img,fg_img_trans)
#     return new_img

# all_rects = packer.rect_list()
# for rect in all_rects:
#     b, x, y, w, h, rid = rect
#     post = [post for post in news if post['id'] == rid][0]
#     # print(w,h, post['size'],post['font_size'])
#     font = ImageFont.truetype(font_name, post['font_size'])
#     # draw.rectangle((x,y,x+w,y+h), fill="#000", outline="#aaa")
#     draw.text((x,y),post['text'], fill=font_color, font=font, anchor=anchor)
# img = img.crop(box=(0,0,img.width - 256,img.height))

# if mode == 'composite':
#     bg = trans_paste(bg,img)
# else:
#     bg.paste(img, (0,0), img)

# bg.save("rectpack.png")