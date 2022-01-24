from image_util import combine
import os
import sys
import csv
import time
import configparser

def create_config(path:str):
    config = configparser.ConfigParser(allow_no_value=True)
    config.add_section('default')
    config['default'] = {
        '; Path to true type font (better) or system font name': None,
        'font': 'Roboto-Regular.ttf',
        'font_size': 14,
        '; Change combinations of font and background colors with opacity to get different results':None,
        '; Resulting image layers will be combined with alpha support':None,
        '; font rgb color with opacity last value from 0 to 255, 0 - fully transparent': None,
        'font_color': '20,20,20,20',
        'bg_color': '0,0,0,255',
        '; Input can be *.txt or *.csv file path': None,
        'text_file': 'news.csv',
        '; Better to provide input in "utf-8"': None,
        'text_encoding': 'utf-8',
        '; If input is csv file, detect how many columns for each row will be treated as separate input': None,
        'csv_delimeter': ';',
        'csv_columns': 2,
        '; Use this str separator between row content from csv file': None,
        'separator' : '|',
        '; Append this suffix to resulting png file before extension': None,
        'file_suffix':'_with_text',
        '; Comma separated list of input images paths, can be quoted with \' or "': None,
        'image_files': 'example.jpeg'
    }
    with open(path, "w") as config_file:
        config.write(config_file)


# Main

if __name__ == "__main__":
    # Create config if not exists
    if not os.path.exists('config.ini'):
        create_config('config.ini')
    config_file = configparser.ConfigParser()
    config_file.read('config.ini')
    config = config_file['default']

    # Detect images files as list (can be pure string, or string with quotes)
    image_files = [f.strip().replace('"','').replace("'",'') for f in config.get('image_files').split(',')]
    if len(image_files) == 0:
        print("No image_files found in config files - exit")
        exit()

    font = config.get('font').strip().replace('"','').replace("'",'')
    font_color = tuple(int(v.strip()) for v in config.get('font_color').split(','))
    font_size = int(config.get('font_size'))
    bg_color = tuple(int(v.strip()) for v in config.get('bg_color').split(','))
    text_input = config.get('text_file').strip().replace('"','').replace("'",'')
    text_encoding = config.get('text_encoding', 'utf-8')
    file_suffix = config.get('file_suffix','_with_text')

    text = ''
    #detect txt or csv by extension
    extension = text_input.rsplit('.', 1)[1]
    if extension == 'txt':
        with open(text_input, encoding=text_encoding) as txt_file:
            text = ' '.join(line for line in  txt_file.read().splitlines())
    if extension == 'csv':
        delimeter = config.get('csv_delimeter')
        column_count = int(config.get('csv_columns'))
        separator = config.get('separator', '')
        try:
            with open(text_input, encoding=text_encoding) as csv_file:
                reader = csv.reader(csv_file, delimiter=delimeter )
                for row in reader:
                    for i in range(column_count):
                        text += row[i] + ' '
                    text += separator + ' '
        # check for broken files, WARNING: please provide good files
        except UnicodeDecodeError:
            text = ''
            with open(text_input, encoding='unicode_escape') as csv_file:
                reader = csv.reader(csv_file, delimiter=delimeter )
                for row in reader:
                    for i in range(column_count):
                        text += row[i] + ' '
                    text += separator + ' '
    else:
        print("Unknown text_input format, only *.txt and *.csv supported")
        exit()

    # Process all images from config input
    for path in image_files:
        if not os.path.isfile(path):
            print("%s is not a real file" % path)
            continue

        t = time.process_time()

        result = combine(path, text, font, font_color, font_size, bg_color)
        path_name, path_extension = path.rsplit('.', 1)
        result_path = "%s%s.png" % (path_name, file_suffix)
        result.save(result_path)
        print('Processed: %s -> %s, %.2fs' % (path, result_path, time.process_time() - t))