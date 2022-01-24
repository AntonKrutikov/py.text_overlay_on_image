Put transparent text layer from input (txt file for now) on top of image.

Can configure font, font size, font color.

Text is __'justified'__ over all image width and height. If text less then canvas size - it will be repeated by words (using cycle list)

Depends on font size and original image size - font measure can take a time:

Some results for python3.10 on MacBook M1 and font-size=14:

    fullhd image: ~3 sec
    5k image: ~ 25 sec


![einshtein](einshtein_with_text.png)