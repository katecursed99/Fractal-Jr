from clrprint import *
import pygame

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



#Initialize Pygame, screen, and clock
pygame.init()


screen_width = 64
screen_height = 64
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
FPS = 60
clock = pygame.time.Clock()
cycle_loop = True
print(list(range(ord('a'), ord('z') + 1)))

#Game engine loop
while cycle_loop:
    
    for event in pygame.event.get():
        #Keyboard triggers
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                cycle_loop = not cycle

            if event.key == pygame.K_SPACE:
                rainbow_print("hi I'm Kate ")
        #Resize screen
        if event.type == pygame.VIDEORESIZE:
            screen_width, screen_height = event.w, event.h
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    
    clock.tick(FPS)
    pygame.display.flip()
    
