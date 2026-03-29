from clrprint import *

ascii_colors = [0,"red", "yellow", "green", "blue", "purple", "pink" ]

def cycle_list(input_list):
    for i in range(len(input_list)):
        
        try:
            input_list[i] = input_list[i+1]
        except IndexError:
            input_list[i] = input_list[0]
            break

def rainbow_print(text):
    text_split = list(text)
    for i in range(len(text)):
        cycle_list(ascii_colors)

        clrprint(text_split[i], clr= ascii_colors[0],end='')

def rainbow_print_anim(text):
    text_split = list(text)
    for i in range(len(text)):
        cycle_list(ascii_colors)

        clrprint(text_split[i], clr= ascii_colors[0],end='')
    
rainbow_print("hi I'm Kate")
