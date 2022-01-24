from image_util import combine
import time

input_file_paths = ['einshtein.jpeg']
font = 'Roboto-Regular.ttf'
font_color = (255, 255, 255, 10) #alpha from 0 to 255
font_size = 14
# Example of overlay backgrounds:
# Fully transparent: background = (255,255,255,0) 
# Fully black (only font alpha used on combine process): background = (0,0,0,255) 
background = (0,0,0,255) 

text = ''
with open('input.txt') as txt_file:
    text = ' '.join(line for line in  txt_file.read().splitlines())

for path in input_file_paths:
    print('Start process: %s' % path)
    t = time.process_time()

    combine(path, text, font, font_color, font_size, background)
    print('Process finished: %s, %.2fs' % (path, time.process_time() - t))