from image_util import combine
import time

input_file_paths = ['einshtein.jpeg','groot.jpg','arcane.jpg','nature.jpg']
font = 'Roboto-Regular.ttf'
font_color = (255, 255, 255, 30)
font_size = 14

text = ''
with open('input.txt') as txt_file:
    text = ' '.join(line for line in  txt_file.read().splitlines())

for path in input_file_paths:
    print('Start process: %s' % path)
    t = time.process_time()

    combine(path, text, font, font_color, font_size)
    print('Process finished: %s, %.2fs' % (path, time.process_time() - t))