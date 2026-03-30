#imports
import math
import sys
import os
import time
import json
import pygame
import threading
from clrprint import *
import numpy as np


def save_settings(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,c_var_i,c_var_r,max_iter,mode):
    ##########################
    #asks for a name to save the file as, then writes current settings
    #to a JSON called presets.json
    ##########################
    max_save_slots = 32 #arbitrary number essentially, but having a max stops it from
                        #searching forever in an intentionally long JSON file

    save_data = {
        "name": "",
        "xpos": xpos,
        "ypos": ypos,
        "width": width,
        "height": height,
        "viewX": viewX,
        "viewY": viewY,
        "scale": scale,
        "z_axis": z_axis,
        "w_axis": w_axis,
        "zoom": zoom,
        "power": power,
        "c_var_i": c_var_i,
        "c_var_r": c_var_r,
        "max_iter": max_iter,
        "mode": mode
        }
    
    save_data["name"] = str(input('Name your new preset: '))
    
    if os.path.exists('presets.json'):
        with open('presets.json', 'r') as f:
            data = json.load(f)
    else:
        data = []

    if data.len() >= max_save_slots:
        print('Need to delete a preset to make room!')
    else:
        data.append(save_data)

    with open('presets.json', 'w') as f:
        json.dump(data, f, indent=2)

def load_preset():
    ##########################
    #pulls in presets from the JSON and lists them out, then asks for one to
    #load and finally loads it
    ##########################
    max_save_slots = 32 #arbitrary number essentially, but having a max stops it from
                        #searching forever in an intentionally long JSON file
    
    global xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,c_var_i,c_var_r,max_iter,mode

    with open('presets.json','r') as preset_store:
        data_temp = preset_store.read()
        data_store = json.loads(data_temp)
        print('Presets:')
        for diction in data_store:
            print(diction["name"], end=' ')
        #print(dict(data_store))
        preset_name = str(input('\nEnter a preset to load'))
        i=0
        for diction in data_store:
            i+=1
            if i >= max_save_slots:
                break #So a ridiculously long JSON doesn't brick me
            if preset_name == diction["name"]:
                xpos = diction["xpos"]
                ypos = diction["ypos"]
                width = diction["width"]
                height = diction["height"]
                viewX = diction["viewX"]
                viewY = diction["viewY"]
                scale = diction["scale"]
                z_axis = diction["z_axis"]
                w_axis = diction["w_axis"]
                zoom = diction["zoom"]
                power = diction["power"]
                c_var_i = diction["c_var_i"]
                c_var_r = diction["c_var_r"]
                max_iter = diction["max_iter"]
                mode = diction["mode"]
                break
            if i>=data_store.len() or i >= max_save_slots:
                print('Preset not found. Check spelling maybe?')
def apply_mods(mode,cx,cy,z_axis,w_axis,c_var_r,c_var_i):
    ##########################
    #returns c and z based on mode
    ##########################
    if mode == "mandelbrot":
        z = complex(z_axis, w_axis)
        c = complex(cx, cy)
    elif mode == "julia":
        z = complex(cx+z_axis, cy+w_axis)
        c = complex(c_var_r, c_var_i)
    return c,z

def is_in_mandelbrot_set(x,y,z_axis,w_axis,zoom,width,height,viewX,viewY,power,max_iter):
    ##########################
    #basic check if a point is in the set.
    #returns True or False
    ##########################
    scale_x = 3.5 / zoom
    scale_y = 2.0 / zoom
    scale = 3.5 / (width*zoom)
    cx = viewX + (x - width/2) * scale
    cy = viewY + (y - height/2) * scale
    cy*=(height/width)
    
    color_ticker=0

    #Determines how the modifiers are applied
    c,z = apply_mods(mode,cx,cy,z_axis,w_axis,c_var_r,c_var_i)

            
    magnitude_z = (z.real**2+z.imag**2)**0.5
    while abs(magnitude_z) < 2 and color_ticker<=max_iter:
                
        color_ticker+=1
        z = z**power+(c)
        magnitude_z = (z.real**2+z.imag**2)**0.5
        if color_ticker >= max_iter:
            return True
            break
    return False

def connect_dots_inner(array_data,super_list):
    ##########################
    #sorts coordinates to trace by distance from last
    #possibly needs to be reworked
    ##########################
    last_point = array_data[0]
    
    array_data_upd = np.delete(array_data, 0, axis=0)
    distances = np.linalg.norm(array_data_upd - last_point, axis=1)
    sorted_indices = np.argsort(distances)

    sorted_points = array_data_upd[sorted_indices]
    
    sorted_distances = distances[sorted_indices]

    for dist in range(0,len(sorted_distances),1):
        if sorted_distances[dist] < sorted_distances[dist-1] and dist!= 0:
            break
    
    return sorted_points,array_data[0]


def connect_dots(array_data):
    ##########################
    #takes the inside tracer and sorts by distance from eachother
    #
    ##########################
    sorted_points = []
    while len(array_data) > 1:
        array_data,super_data = connect_dots_inner(array_data,sorted_points)
        #print(array_data)
        sorted_points.append(tuple(super_data))
    
    #print('super list'+str(sorted_points))
    converted = [(int(a), int(b)) for a, b in sorted_points]
    flattened=[]
    for a, b in converted:
        flattened.extend([a,b])
    #print(converted)
    #print(flattened)
    return flattened


def mandelbrot_set(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,dict_catchers,max_iter):
    ##########################
    #the main fractal generator code. it's actually both Julia and Mandelbrot now
    #it's designed to be relatively modular and spit out data to a rendering
    #function so that it can be hooked up to a proper drawing package later on
    #returns frac_matrix_f, width, height, dict_catchers, frac_matrix_s
    ##########################
    if zoom==0:
        zoom+=1
    c_var = complex(c_var_i,c_var_r)
    scale = 3.5 / (width*zoom)
    frac_tracer_list = []
    frac_matrix = np.array([(0,0,0)])
    frac_matrix_f = []
    frac_matrix_s = []
    total_ticker = 0
    x_ticker = 0
    y_ticker = 0

    #the pixel grid
    for x in range(width):
        x_ticker+=1
        y_ticker=0
        
        for y in range(height):
            inside=False
            inside_border=False
            scale_x = 3.5 / zoom
            scale_y = 2.0 / zoom
            
            #camera controls
            cx = viewX + (x - width/2) * scale
            cy = viewY + (y - height/2) * scale
            
                
            cy*=(height/width)
           
            color_ticker=0

            
            c,z = apply_mods(mode,cx,cy,z_axis,w_axis,c_var_r,c_var_i)

            y_ticker+=1

            total_ticker+=1
            magnitude_z = (z.real**2+z.imag**2)**0.5
            while abs(magnitude_z) < 2 and color_ticker<=max_iter:
                
                color_ticker+=1
                z = z**power+(c)
                magnitude_z = (z.real**2+z.imag**2)**0.5
                if color_ticker >= max_iter:
                    inside=True



                    
                    #Check all surrounding pixels to see if it's on the border
                    buffer_check = []
                    buffer_AND = True

                    for x2 in range(-1,2):
                        for y2 in range(-1,2):
                            if is_in_mandelbrot_set(x+x2,y+y2,z_axis,w_axis,zoom,width,height,viewX,viewY,power,max_iter):
                                buffer_check.append(True)
                            else:
                                buffer_check.append(False)
                    for buffer in buffer_check:
                        if buffer == False:
                            buffer_AND = False
                    if buffer_AND == False:
                    
                        frac_tracer_list.append(x)
                        frac_tracer_list.append(y)
                        inside_border=True
                    else:
                        inside_border = False
                    
                    
                    break

            #Uses the variables from earlier in the function to decide the color
            fill_color = 1 #default color
            if inside==True:
                if inside_border==True:
                    if trace_show == True:
                        fill_color = 4
                    else:
                        fill_color = len(dict_catchers)
                    color_ticker = max_iter
                else:
                    fill_color = len(dict_catchers)
                color_ticker = max_iter
            spill_over = 0
            
            for dict_ent in dict_catchers:
                if color_ticker <= dict_ent['thresh']:
                    fill_color = dict_ent['id']
                    spill_over = color_ticker - dict_ent['thresh']
                    
                    break
            
                
            x_path = (x+xpos+width//2)
            y_path = (y+ypos+height//2)
            frac_matrix_f.append(fill_color)
            frac_matrix_s.append(spill_over)

    
    
    point_list_x = []
    point_list_y = []
    projected_point_list = []
    for i in range(0, len(frac_tracer_list), 2):

        point_list_x.append(frac_tracer_list[i]*scale+xpos+width//2)
        point_list_y.append(frac_tracer_list[i+1]*scale+ypos+height//2)
        current_point = (frac_tracer_list[i]*scale+xpos+width//2,frac_tracer_list[i+1]*scale+ypos+height//2)
        projected_point_list.append(current_point)
    array_data = np.array(projected_point_list)



    list_data_new = connect_dots(array_data)
    
    for i in range(0,(len(list_data_new)//2)+2,2):
        
        pass

    return frac_matrix_f,width,height,dict_catchers,frac_matrix_s
    


def draw_to_terminal(frac_matrix_f,width,height,dict_catchers,frac_matrix_s):
    ##########################
    #Draws the data returned from mandelbrot_set to the terminal using
    #terminal and clrprint
    #Variable number of buckets, in dict_catchers. When one starts being filled, the
    #other dumps to the terminal
    ##########################
    os.system('cls' if os.name == 'nt' else 'clear')
    counter = 0
    print('\n       ',end='')
    
    
    
    #Loop for each pixel
    for i, e in enumerate(frac_matrix_f):
        row_end = (i + 1)% width == 0
        spill_over = (frac_matrix_s[i])%len(ascii_density)
        if spill_over > len(ascii_density):
            spill_over = 0
        for dict_ent in dict_catchers:
            
            if e == dict_ent['id']:
                if not dict_ent['flag']:
                    for dict_ent_2 in dict_catchers:
                        if dict_ent_2['catcher']:
    
                            clrprint(''.join(dict_ent_2['catcher']), clr=dict_ent_2['color'], end='')
                            dict_ent_2['catcher'] = []
                            dict_ent_2['flag'] = False
        
                    dict_ent['flag'] = True
                dict_ent['catcher'].append(ascii_density[spill_over]+ascii_density[spill_over]) #+ ('\n       ' if row_end else ''))
        if row_end:
            for dict_ent in dict_catchers:
                if dict_ent['catcher']:
                    clrprint(''.join(dict_ent['catcher']),
                             clr=dict_ent['color'],
                             end='')
                    dict_ent['catcher'] = []
                dict_ent['flag'] = False
            print('\n       ',end='')
    # flush remaining
    for dict_ent in dict_catchers:
        if dict_ent['catcher']:
            
            clrprint(''.join(dict_ent['catcher']), clr=dict_ent['color'], end='')
   
            dict_ent['catcher'] = []
        #print(e)
    clrprint('Coords: x:'+str(round(viewX,3))+'y:'+str(round(viewY,3))+'i, formula: z^'+str(round(power,3))+'+c*'+str(round(c_var_r))+'+'+str(round(c_var_i))+'i, z0:'+str(round(z_axis,3))+', c0:'+str(round(w_axis,3))+' zoom:'+str(round(zoom,3)), clr='red', end=' ')

def cycle_list(input_list):
    ##########################
    #cycles through a list for color cycling
    #
    ##########################
    for i in range(len(input_list)):
        try:
            input_list[i] = input_list[i+1]
        except IndexError:
            input_list[i] = input_list[0]
            break

#---------Global variables-------#

xpos = 0
ypos = 0
width = 32
height = 32
viewX = -0.5
viewY = 0
scale = 1
z_axis = 0
w_axis = 0
zoom = 1
power = 2.0
c_var_i = 0
c_var_r = 1
c_var = complex(c_var_i,c_var_r)
y_constant = 1
max_iter = 100
cycle = True
game_cycle = True
trace_show = True
dyn_pointer = 'y'
dev_mode = True
mode = 'mandelbrot'



                



print('loading , , ,')
pygame.mixer.init() 
pygame.init()

sound_list = [pygame.mixer.Sound('assets/magic.wav'),pygame.mixer.Sound('assets/blip.wav'),pygame.mixer.Sound('assets/dissonant.wav')]

sound_list[0].play()




ascii_density = list('░▒▓█') #.:-=+*#%@
ascii_density.reverse()
ascii_colors = ["white", "red", "yellow", "green", "blue", "purple", "pink" ]


dict_catchers = [{
        "id":1,
        "catcher":[],
        "flag":False,
        "color":'black',

        "thresh":3
            },{
        "id":2,
        "catcher":[],
        "flag":False,
        "color":'grey',

        "thresh":7
            },{
        "id":3,
        "catcher":[],
        "flag":False,
        "color":'green',

        "thresh":11
            },{
        "id":4,
        "catcher":[],
        "flag":False,
        "color":'purple',

        "thresh":15
            },{
        "id":5,
        "catcher":[],
        "flag":False,
        "color":'red',
 
        "thresh":24
            },{
        "id":6,
        "catcher":[],
        "flag":False,
        "color":'yellow',
 
        "thresh":24
            },{
        "id":7,
        "catcher":[],
        "flag":False,
        "color":'none',
        "thresh":max_iter-1
            }
        ]
def refresh_fractal_colors(ascii_colors,cycle,f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s):
    ##########################
    #reassigns colors to the fractal each refresh
    #
    ##########################
    if cycle == True:
        cycle_fractal_colors(dict_catchers,ascii_colors)  
        draw_to_terminal(f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s)

        
def cycle_fractal_colors(dict_catchers,ascii_colors):
    #First cycle the ascii colors list
    cycle_list(ascii_colors)
    #Then use the list to assign the new colors to each catcher
    for catcher in dict_catchers:
        col_index = catcher["id"] % len(ascii_colors)
        catcher["color"] = ascii_colors[col_index]
    


for dicti in dict_catchers:
    dicti["thresh"] = max_iter//len(dict_catchers)*dicti["id"]//4
    dicti["color"]
    
#------------------------------#

def draw_title(ascii_color,loops):
    i=0
    if dev_mode == False:
        while i <= loops:
            time.sleep(0.08)
            os.system('cls' if os.name == 'nt' else 'clear')
            clrprint(' ______   ______     ______     ______     ______   ______     __         ', clr=ascii_color[1])
            clrprint('/\\  ___\\ /\\  == \\   /\\  __ \\   /\\  ___\\   /\\__  _\\ /\\  __ \\   /\\ \\        ', clr=ascii_color[1])
            clrprint('\\ \\  __\\ \\ \\  __<   \\ \\  __ \\  \\ \\ \\____  \\/_/\\ \\/ \\ \\  __ \\  \\ \\ \\____   ', clr=ascii_color[2])
            clrprint(' \\ \\_\\    \\ \\_\\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\    \\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\  ', clr=ascii_color[3])
            clrprint('  \\/_/     \\/_/ /_/   \\/_/\\/_/   \\/_____/     \\/_/   \\/_/\\/_/   \\/_____/  ', clr=ascii_color[4])
            clrprint('                                                                          ', clr=ascii_color[3])
            clrprint('                                                         __     ______    ', clr=ascii_color[5])
            clrprint('                                                        /\\ \\   /\\  == \\   ', clr=ascii_color[5])
            clrprint('                                                       _\\_\\ \\  \\ \\  __<   ', clr=ascii_color[6])
            clrprint('                                                      /\\_____\\  \\ \\_\\ \\_\\ ', clr=ascii_color[0])
            clrprint('                                                      \\/_____/   \\/_/ /_/ ', clr=ascii_color[1])
            clrprint('                                                                          ', clr=ascii_color[0])
            if i >= loops//3:
                clrprint('      © Katherina L Jesek               2026                MIT License',clr='red')
            else:
                print('')
            if i >= loops//3*2:
                clrprint('      type help and hit enter for info on commands!  ',clr='yellow')
            else:
                print('')
            #os.system('cls' if os.name == 'nt' else 'clear')

            i+=1
        cycle_list(ascii_colors)
        if i != loops:
            print('')
    clrprint('      loading fractal . . .')
    time.sleep(2)

my_font = pygame.font.SysFont('Arial', 30)
draw_title(ascii_colors,20)
screen_width = 128
screen_height = 128
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
FPS = 30
refresh_every = 6
clock = pygame.time.Clock()

while True:
    #This lil code is so disgusting but it's just grabbing data from mandelbrot_set
    #and passing it over to draw_to_terminal in the following line
    f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s = mandelbrot_set(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,dict_catchers,max_iter)
    draw_to_terminal(f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s)

    #"Game loop" logic for color cycling
    c_ticks = 0
    fake_terminal = "" #this is the onscreen terminal in the pygame window
    while game_cycle == True:
        enter = False
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                shift_pressed = True
            else:
                shift_pressed = False
        #Resize screen
            if event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.w, event.h
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        #Keyboard triggers
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    cycle = not cycle
                    game_cycle = not game_cycle
                    fake_terminal = "" #clear fake terminal
                if event.key == pygame.K_RETURN:
                    read_comm = fake_terminal
                    fake_terminal = "" #clear
                    enter = True
                    game_cycle = not game_cycle
                if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    mem_term = fake_terminal[:-1]
                    fake_terminal = mem_term

                #Take keystrokes (sigh)
                if event.key == pygame.K_a:
                    fake_terminal += 'A' if shift_pressed else 'a'
                if event.key == pygame.K_b:
                    fake_terminal += 'B' if shift_pressed else 'b'
                if event.key == pygame.K_c:
                    fake_terminal += 'C' if shift_pressed else 'c'
                if event.key == pygame.K_d:
                    fake_terminal += 'D' if shift_pressed else 'd'
                if event.key == pygame.K_e:
                    fake_terminal += 'E' if shift_pressed else 'e'
                if event.key == pygame.K_f:
                    fake_terminal += 'F' if shift_pressed else 'f'
                if event.key == pygame.K_g:
                    fake_terminal += 'G' if shift_pressed else 'g'
                if event.key == pygame.K_h:
                    fake_terminal += 'H' if shift_pressed else 'h'
                if event.key == pygame.K_i:
                    fake_terminal += 'I' if shift_pressed else 'i'
                if event.key == pygame.K_j:
                    fake_terminal += 'J' if shift_pressed else 'j'
                if event.key == pygame.K_k:
                    fake_terminal += 'K' if shift_pressed else 'k'
                if event.key == pygame.K_l:
                    fake_terminal += 'L' if shift_pressed else 'l'
                if event.key == pygame.K_m:
                    fake_terminal += 'M' if shift_pressed else 'm'
                if event.key == pygame.K_n:
                    fake_terminal += 'N' if shift_pressed else 'n'
                if event.key == pygame.K_o:
                    fake_terminal += 'O' if shift_pressed else 'o'
                if event.key == pygame.K_p:
                    fake_terminal += 'P' if shift_pressed else 'p'
                if event.key == pygame.K_q:
                    fake_terminal += 'Q' if shift_pressed else 'q'
                if event.key == pygame.K_r:
                    fake_terminal += 'R' if shift_pressed else 'r'
                if event.key == pygame.K_s:
                    fake_terminal += 'S' if shift_pressed else 's'
                if event.key == pygame.K_t:
                    fake_terminal += 'T' if shift_pressed else 't'
                if event.key == pygame.K_u:
                    fake_terminal += 'U' if shift_pressed else 'u'
                if event.key == pygame.K_v:
                    fake_terminal += 'V' if shift_pressed else 'v'
                if event.key == pygame.K_w:
                    fake_terminal += 'W' if shift_pressed else 'w'
                if event.key == pygame.K_x:
                    fake_terminal += 'X' if shift_pressed else 'x'
                if event.key == pygame.K_y:
                    fake_terminal += 'Y' if shift_pressed else 'y'
                if event.key == pygame.K_z:
                    fake_terminal += 'Z' if shift_pressed else 'z'

        terminal_screen = my_font.render(fake_terminal, False, (250, 250, 250))
        screen.fill((0,0,0))
        screen.blit(terminal_screen, (0,0))
        if c_ticks % refresh_every == refresh_every-3:
            refresh_fractal_colors(ascii_colors,cycle,f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s)
        clock.tick(FPS)
        c_ticks += 1
        pygame.display.flip()
        
    while True:
        clrprint('command:',clr='white',end='')
        enter_flag = False
        if not enter:
            read_comm = input(' -')
        if enter_flag == True:
            break
        if read_comm == 'help':
            print('\n       Enter commands, then hit enter to run!                           ')
            print('       W +              -   +          -   +            -   +         ')
            print('     A<->D = x,y axes | X<->Z = zoom | V<->F = Z-axis | G<->B = kata/ana')
            print('     - S    ')
            print('     N<->H = power | M<->J = c-factor (real) | I<->K = c-factor (imaginary)')
            print('     You can issue multiple 1-char commands per entry to be more efficient')
            print('       Capital letters have the same function but are 10x as powerful')
            print('     Keyword commands: mandelbrot, julia, resize, help, save, load, quit')
            clrprint('\n       command:',clr='white',end='')
            break

        #This is where all the possible text commands live
                #IMPORTANT: every word-based command MUST conclude with a break
                #or it will apply every letter in the word as a separate command
        
        if read_comm == 'resize':
            try:
                new_size = int(input('\n       New size: '))
                width = new_size
                height = new_size
                break
            except ValueError:
                print('<- Back')
                break
            
        if read_comm == 'quit':
            break
        if read_comm == 'mandelbrot':
            xpos = 0
            ypos = 0
            viewX = -0.5
            viewY = 0
            scale = 1
            z_axis = 0
            w_axis = 0
            zoom = 1
            power = 2.0
            c_var_i = 0
            c_var_r = 1
            c_var = complex(c_var_i,c_var_r)
            y_constant = 1
            mode = 'mandelbrot'
            sound_list[0].play()
            break
        if read_comm == 'julia':
            xpos = 0
            ypos = 0
            viewX = 0
            viewY = 0
            scale = 1
            z_axis = 0
            w_axis = 0
            zoom = 1
            power = 2
            c_var_r = -0.7
            c_var_i = 0.27015
            c_var = complex(c_var_i,c_var_r)
            mode = 'julia'
            sound_list[0].play()
            break
        if read_comm == 'seahorse':
            mode = 'mandelbrot'
            viewX = -0.745
            viewY = 0.115
            zoom = 20
            power = 2
            c_var_r = 1
            c_var_i = 0
            c_var = complex(c_var_i,c_var_r)
            z_axis = 0
            w_axis = 0
            sound_list[0].play()
            break
        if read_comm == 'trace':
            trace_show = not trace_show
            break
        if read_comm == 'cycle':
            cycle = True
            game_cycle = True
        #Save/load preset features
        if read_comm == 'save':
            save_settings(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,c_var_i,c_var_r,max_iter,mode)
            sound_list[0].play()
            break
        if read_comm == 'load':
            load_preset()
            sound_list[0].play()
            break
        if read_comm == 'delete':
##NEEDS IMPLEMENTATION
            break
        if read_comm == 'mute':
            for sound in sound_list:
                sound.set_volume(0)
        ticker=0
        for read_key in list(read_comm):
            control_factor = 0.01
            ticker += 1
            if read_key.isupper():
                control_factor*=10
                read_key = read_key.lower()
            if read_key == '~':
                try:
                    if dev_mode == True:
                        dev_input = str(input('~'))
                        exec(dev_input)
                      
                except ValueError,SyntaxError,TypeError:
                    print('Hey stop poking around in there!')
            
            #zooming in and out
            if read_key == 'z':
                if ticker == 1:
                    sound_list[1].play()
                zoom*=1+(control_factor)
                if zoom == 0:
                    zoom=1
                continue
            elif read_key == 'x':
                if ticker == 1:
                    sound_list[1].play()
                zoom*=1-(control_factor)
                if zoom == 0:
                    zoom-=1
                continue
                
            elif read_key == 'w':
                if ticker == 1:
                    sound_list[2].play()
                viewX+=control_factor*(2*zoom)
                continue
            elif read_key == 's':
                if ticker == 1:
                    sound_list[2].play()
                viewX-=control_factor*(2*zoom)
                continue
            elif read_key == 'a':
                if ticker == 1:
                    sound_list[2].play()
                viewY-=control_factor*(2*zoom)
                continue
            elif read_key == 'd':
                if ticker == 1:
                    sound_list[2].play()
                viewY+=control_factor*(2*zoom)
                continue
            elif read_key == 'v':
                if ticker == 1:
                    sound_list[2].play()
                z_axis-=control_factor
                continue
            elif read_key == 'f':
                if ticker == 1:
                    sound_list[2].play()
                z_axis+=control_factor
                continue
            elif read_key == 'g':
                if ticker == 1:
                    sound_list[2].play()
                w_axis+=control_factor
                continue
            elif read_key == 'b':
                if ticker == 1:
                    sound_list[2].play()
                w_axis-=control_factor
                continue
            elif read_key == 'h':
                if ticker == 1:
                    sound_list[2].play()
                power+=control_factor
                continue
            elif read_key == 'n':
                if ticker == 1:
                    sound_list[2].play()
                power-=control_factor
                continue
            elif read_key == 'j':
                if ticker == 1:
                    sound_list[2].play()
                c_var_r+=control_factor
                continue
            elif read_key == 'm':
                if ticker == 1:
                    sound_list[2].play()
                c_var_r-=control_factor
                continue
            elif read_key == 'i':
                if ticker == 1:
                    sound_list[2].play()
                c_var_i+=control_factor
                continue
            elif read_key == 'k':
                if ticker == 1:
                    sound_list[2].play()
                c_var_i-=control_factor
                continue
        if enter == True:
            enter_flag = True
            read_comm = ''
            break
            
        break
           

    if read_comm == 'quit':
        print('Have a lovely day <3')
        time.sleep(2)
        sys.exit(0)
        break
    if enter == True:
        game_cycle = True
        continue
        
time.sleep(0.05)
draw_to_terminal(mandelbrot_set(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,dict_catchers,max_iter))



#mandelbrot_set(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom)
