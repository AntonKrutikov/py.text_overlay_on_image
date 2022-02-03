import configparser

def create_config(path:str):
    config = configparser.ConfigParser(allow_no_value=True)
    config.add_section('default')
    config['default'] = {
        '; Path to true type font (better) or system font name': None,
        'font': 'Roboto-Regular.ttf',
        '; Comma separated list of font sizes and them weights (used in random choice, mean how often to take)': None,
        'font_sizes': '8, 16',
        'font_weights': '1, 1',
        '; Change combinations of font and background colors with opacity to get different results':None,
        '; Resulting image layers will be combined with alpha support':None,
        '; font rgb color with opacity last value from 0 to 255, 0 - fully transparent': None,
        'font_color': '255,255,255,0',
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
        '; Open and close chars will be puted around content of second csv column': None,
        'source_column_open_char': '(',
        'source_column_close_char': ')',
        '; Append this suffix to resulting png file before extension': None,
        'file_suffix':'',
        '; Comma separated list of input images paths, can be quoted with \' or "': None,
        'image_files': 'input/lion.jpeg',
        'out_dir': 'output',
        '; Mode "composite" (alpha blend) or "paste". (composite is better)': None,
        'mode':'composite',
        '; GuillotineBafLas - fast with same +- result as MaxRectsBlsf (which much slower)': None,
        'algorithm':'GuillotineBafLas',
        '; Increase news list by': None,
        'news_multiply_by': 1,
        'news_shuffle': False

    }
    with open(path, "w") as config_file:
        config.write(config_file)