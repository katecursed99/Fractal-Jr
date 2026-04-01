
#         Program Diagram

    ##########################
    # Initialization         #
    ##########################
#               v
#####################################
# Pygame loop   v                    #  
#               v                     # 
#            Globals <---------------  #
#            vvvvvvv                 ^  #
#   ##########################       |  #
#  >#Fractal math            # -->   |  #
# | ##########################    |  |  #
# m*                      V       |  |  #
# | ##########################    |  |  #
# | #Cache pipeline          #    n* k* #
# | ##########################<-  |  |  #
# |                     V      a* |  |  #
# | ##########################->  v  |  #
#  -#Render pipeline         # <--   |  #
#   ##########################       |  #
#                                    |  #
#   ##########################       |  #
#   #Interface/control block # ----->   #
#   ##########################          #
#                                       #
# legend:                               #
# n* = non-animated                     #
# a* = animated                         #
# m* = main reset                       #
# k* = keyboard inputs                  #
#########################################




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







def save_settings(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,c_var_i,c_var_r,max_iter,mode,read_comm,max_save_slots):
    ##########################
    #asks for a name to save the file as, then writes current settings
    #to a JSON called presets.json
    ##########################
    
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
    
    save_data["name"] = read_comm
    
    if os.path.exists('presets.json'):
        with open('presets.json', 'r') as f:
            data = json.load(f)
    else:
        data = []

    if len(data) >= max_save_slots:
        print('Need to delete a preset to make room!')
    else:
        data.append(save_data)

    with open('presets.json', 'w') as f:
        json.dump(data, f, indent=2)

def show_presets(message,max_save_slots):
    with open('presets.json','r') as preset_store:
        data_temp = preset_store.read()
        data_store = json.loads(data_temp)
        message = 'Presets: \n'
        i=0
        for diction in data_store:
            i+=1
            message += diction["name"]+' '
            if i%3 == 0:
                message += '\n'
            if i >= len(data_store) or i >= max_save_slots:
                message+='\nLoad which file?:'
            if i >= max_save_slots:

                break

    
 
    return message
            
def delete_preset(user_entry,max_save_slots):
    with open('presets.json','r') as preset_store:
        data_temp = preset_store.read()
    data_store = json.loads(data_temp)

        #print(dict(data_store))
    preset_name = user_entry
    i=0
    for i,diction in enumerate(data_store):
        if user_entry == diction["name"]:
            del data_store[i]
            with open('presets.json', 'w') as f:
                json.dump(data_store, f, indent=2)
            break
                

    

def load_preset(message,read_comm):
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

        #print(dict(data_store))
        preset_name = read_comm
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
            if i>=len(data_store) or i >= max_save_slots:
                break
                
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
    scale_x = 3.5 / (width*zoom)
    scale_y = 3.5 / (height*zoom)
    scale = 3.5 / (width*zoom)
    cx = viewX + (x - width/2) * scale_x
    cy = viewY + (y - height/2) * scale_y
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
            scale_x = 3.5 / (width*zoom)
            scale_y = 3.5 / (height*zoom)
            
            #camera controls
            cx = viewX + (x - width/2) * scale_x
            cy = viewY + (y - height/2) * scale_y
            
                
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

def save_screen_surface(border_x,border_y,screen_width,screen_height):
    if frame > 0:
        rect_area = pygame.Rect(border_x, border_y, screen_width-border_x*2, screen_height-border_y*2)
        area_surf = screen.subsurface(rect_area)
        file_name = "exports/fractal"+str(frame)+".png"
        pygame.image.save(area_surf, file_name)
    

def draw_to_screen(frac_matrix_f,width,height,dict_catchers,frac_matrix_s,screen_width,screen_height,cycle,c_ticks,video_camera):
    ##########################
    #draws to the pygame screen
    ##########################

    
    x_tick = 0
    y_tick = 0
    scaled_x = screen_height // height
    scaled_y = screen_height // height
    border_x = (screen_width - (height*scaled_x)) // 2
    border_y = (screen_height - (width*scaled_y)) // 2
    #print(c_ticks)
    for i, e in enumerate(frac_matrix_f):
        
        row_end = (i + 1)% height == 0
        spill_over = (frac_matrix_s[i])


        color_hsv = pygame.Color(0) #init color

        #Color math
        
        if cycle == True:
            hue_mod = c_ticks#//10*10
        else:
            hue_mod = 0
        color_stops = len(dict_catchers)
        color_hue = int(round((360/color_stops*e)+(frac_matrix_s[i]*10)+hue_mod)%360)
        color_sat = 80
        
        
        color_var = int(round((frac_matrix_s[i] * 10)%100))

        #print(color_hue,color_var,color_sat)
        color_hsv.hsva = (color_hue,color_sat,color_var,100)
        

        
        #Generate the pixel
        generated_pixel = pygame.Rect(border_x+x_tick*scaled_x,border_y+y_tick*scaled_y,scaled_x,scaled_y)
        pygame.draw.rect(screen, color_hsv, generated_pixel)

        #Handle pixel counting
        x_tick += 1
        if row_end == True:
            x_tick=0
            y_tick+=1

    if video_camera == True:
        save_screen_surface(border_x,border_y,screen_width,screen_height)

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

def terminal_keyboard_input(event_key):
    ##########################
    #Super obtuse way of taking keyboard inputs into pygame
    #and treating it like a 'terminal'
    ##########################
    fake_terminal = ""
    if event_key == pygame.K_a:
        fake_terminal += 'A' if shift_pressed else 'a'
    elif event_key == pygame.K_b:
        fake_terminal += 'B' if shift_pressed else 'b'
    elif event_key == pygame.K_c:
        fake_terminal += 'C' if shift_pressed else 'c'
    elif event_key == pygame.K_d:
        fake_terminal += 'D' if shift_pressed else 'd'
    elif event_key == pygame.K_e:
        fake_terminal += 'E' if shift_pressed else 'e'
    elif event_key == pygame.K_f:
        fake_terminal += 'F' if shift_pressed else 'f'
    elif event_key == pygame.K_g:
        fake_terminal += 'G' if shift_pressed else 'g'
    elif event_key == pygame.K_h:
        fake_terminal += 'H' if shift_pressed else 'h'
    elif event_key == pygame.K_i:
        fake_terminal += 'I' if shift_pressed else 'i'
    elif event_key == pygame.K_j:
        fake_terminal += 'J' if shift_pressed else 'j'
    elif event_key == pygame.K_k:
        fake_terminal += 'K' if shift_pressed else 'k'
    elif event_key == pygame.K_l:
        fake_terminal += 'L' if shift_pressed else 'l'
    elif event_key == pygame.K_m:
        fake_terminal += 'M' if shift_pressed else 'm'
    elif event_key == pygame.K_n:
        fake_terminal += 'N' if shift_pressed else 'n'
    elif event_key == pygame.K_o:
        fake_terminal += 'O' if shift_pressed else 'o'
    elif event_key == pygame.K_p:
        fake_terminal += 'P' if shift_pressed else 'p'
    elif event_key == pygame.K_q:
        fake_terminal += 'Q' if shift_pressed else 'q'
    elif event_key == pygame.K_r:
        fake_terminal += 'R' if shift_pressed else 'r'
    elif event_key == pygame.K_s:
        fake_terminal += 'S' if shift_pressed else 's'
    elif event_key == pygame.K_t:
        fake_terminal += 'T' if shift_pressed else 't'
    elif event_key == pygame.K_u:
        fake_terminal += 'U' if shift_pressed else 'u'
    elif event_key == pygame.K_v:
        fake_terminal += 'V' if shift_pressed else 'v'
    elif event_key == pygame.K_w:
        fake_terminal += 'W' if shift_pressed else 'w'
    elif event_key == pygame.K_x:
        fake_terminal += 'X' if shift_pressed else 'x'
    elif event_key == pygame.K_y:
        fake_terminal += 'Y' if shift_pressed else 'y'
    elif event_key == pygame.K_z:
        fake_terminal += 'Z' if shift_pressed else 'z'
    elif event_key == pygame.K_0:
        fake_terminal += '0'
    elif event_key == pygame.K_1:
        fake_terminal += '1'
    elif event_key == pygame.K_2:
        fake_terminal += '2'
    elif event_key == pygame.K_3:
        fake_terminal += '3'
    elif event_key == pygame.K_4:
        fake_terminal += '4'
    elif event_key == pygame.K_5:
        fake_terminal += '5'
    elif event_key == pygame.K_6:
        fake_terminal += '6'
    elif event_key == pygame.K_7:
        fake_terminal += '7'
    elif event_key == pygame.K_8:
        fake_terminal += '8'
    elif event_key == pygame.K_9:
        fake_terminal += '9'
        
    return fake_terminal

def refresh_fractal_colors(ascii_colors,cycle,f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s):
    ##########################
    #refreshes the fractal for color cycling
    #
    ##########################
    if cycle == True:
        cycle_fractal_colors(dict_catchers,ascii_colors)  
        draw_to_terminal(f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s)

        
def cycle_fractal_colors(dict_catchers,ascii_colors):
    ##########################
    #handles the actual cycling of colors
    #
    ##########################
    #First cycle the ascii colors list
    cycle_list(ascii_colors)
    #Then use the list to assign the new colors to each catcher
    for catcher in dict_catchers:
        col_index = catcher["id"] % len(ascii_colors)
        catcher["color"] = ascii_colors[col_index]
    
def draw_title(ascii_color,loops):
    ##########################
    #ASCII logo for the terminal
    #
    ##########################
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


def set_up_fractal_environment():
    ##########################
    #Returns our initial 'global' variables (so they can be contained
    #in a non-global environment)
    ##########################
    xpos = 0
    ypos = 0
    width = 240
    height = 160
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
    dev_mode = False
    mode = 'mandelbrot'
    message = '© MIT LICENSE 2026 Katherina L Jesek'
    start_keyframe = {
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
                "max_iter": max_iter
                }
    end_keyframe = {
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
                "max_iter": max_iter
                }
    max_save_slots = 32 #arbitrary number essentially, but having a max stops it from
                        #searching forever in an intentionally long JSON file
    #Just a quick hidden swap because I did the original math backwards
    temp = width
    width = height
    height = temp

    return xpos, ypos, width, height, viewX, viewY, scale, z_axis, w_axis, zoom, power, c_var_i, c_var_r, c_var, y_constant, max_iter, cycle, game_cycle, trace_show, dyn_pointer, dev_mode, mode, message, max_save_slots, start_keyframe, end_keyframe

def fake_print(input_text,message):
    ##########################
    #Simple way to ctrl+r all the terminal
    #notifications into on-screen notifications
    ##########################
    message = input_text

def play_animation(start_keyframe,end_keyframe,frame,anim_length):
    ##########################
    #Handles the list/dictionary part of the animation. see
    #keyframe_formula to edit the curve (it's just linear rn)
    #
    ##########################
    normal_time = (frame) / (anim_length)
    new_keyframe = {}
    key_traits = ["xpos","ypos","width","height","viewX","viewY","scale","z_axis",
                  "w_axis","zoom","power","c_var_i","c_var_r","max_iter"]
    for trait in key_traits:
        new_keyframe[trait] = keyframe_formula(start_keyframe,end_keyframe,trait,normal_time)
   
    return new_keyframe

def keyframe_formula(start_keyframe,end_keyframe,entry_name,normal_time):
    ##########################
    #Does the main math for play_animation and returns the new
    #keyframe
    #
    ##########################
    return start_keyframe[entry_name]+(end_keyframe[entry_name]-start_keyframe[entry_name])*normal_time

def cache_animation_frame(frame,anim_length,f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s,screen_width,screen_height,anim_cache):
    ##########################
    #Prepares keyframe for the cache pipeline and saves when ready
    #
    ##########################

    #if frame == 0:
        #anim_cache = {} #clear cache

    anim_cache[str(0)] = { "frame": frame,
            "f_frac_matrix_f": f_frac_matrix_f,
            "f_width": f_width,
            "f_height": f_height,
            "f_dict_catchers": f_dict_catchers,
            "f_frac_matrix_s": f_frac_matrix_s,
            "screen_width": screen_width,
            "screen_height":screen_height
    }
    anim_cache[str(frame)] = {
        "frame": frame,
        "f_frac_matrix_f": f_frac_matrix_f,
        "f_width": f_width,
        "f_height": f_height,
        "f_dict_catchers": f_dict_catchers,
        "f_frac_matrix_s": f_frac_matrix_s,
        "screen_width": screen_width,
        "screen_height":screen_height
        }
    if frame >= anim_length-1:
        save_cache(anim_cache)

def save_cache(anim_cache):
    with open('cache.json', 'w') as f:
        json.dump(anim_cache, f, indent=2)
    
def play_cache(anim_cache,frame):
    ##########################
    #Returns the same as mandelbrot_set in order to "trick" 
    #the renderer to display from the file rather than the
    #slower main function
    ##########################
    #Returns f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s
    no_frame = False
    
    #Load cache from JSON
    if frame < 1:
        with open('cache.json','r') as cache_file:
            data_cache = cache_file.read()
            anim_cache = json.loads(data_cache)
    #print("Available keys:", anim_cache.keys())
    #print("Looking for:", str(frame))
    #print(anim_cache)
    while True:
        if no_frame == False:
            diction = anim_cache.get(str(frame))
        else:
            diction = anim_cache.get(str(1))
        if diction:
            #print(frame, diction["f_frac_matrix_f"])
            frame_data = diction
        
        try:
            return frame_data["f_frac_matrix_f"],frame_data["f_width"],frame_data["f_height"],frame_data["f_dict_catchers"],frame_data["f_frac_matrix_s"],anim_cache
            no_frame = False
        except UnboundLocalError:
            print('Unable to find frame '+str(frame))
            no_frame = True
            continue
    
#---------Global variables-------#



xpos, ypos, width, height, viewX, viewY, scale, z_axis, w_axis, zoom, power, c_var_i, c_var_r, c_var, y_constant, max_iter, cycle, game_cycle, trace_show, dyn_pointer, dev_mode, mode, message, max_save_slots, start_keyframe, end_keyframe = set_up_fractal_environment()
                




pygame.mixer.init() 
pygame.init()

sound_list = [pygame.mixer.Sound('assets/magic.wav'),pygame.mixer.Sound('assets/blip.wav'),pygame.mixer.Sound('assets/dissonant.wav')]
pygame.mixer.music.load('assets/music.mp3')
pygame.mixer.music.play(-1)
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


for dicti in dict_catchers:
    dicti["thresh"] = max_iter//len(dict_catchers)*dicti["id"]//4
    
    
#------------------------------#

anim_length = 300
anim_loops_max = 1
anim_current_loop = 0
video_camera = False

frame=0
my_font = pygame.font.Font('assets/LineBeam.ttf', 25)
#draw_title(ascii_colors,20)
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
FPS = 60
refresh_every = 1
clock = pygame.time.Clock()
animation_flag = False
resize_flag = False
load_flag = False
save_flag = False
delete_flag = False
play_animation_flag = False
anim_counter = 0
anim_cache = {}
c_ticks = 0
fake_terminal = "" #this is the onscreen terminal in the pygame window

anim_length += 2
while True:
    
    #This lil code is so disgusting but it's just grabbing data from mandelbrot_set
    #and passing it over to draw_to_terminal in the following line
    if animation_flag != True:
        f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s = mandelbrot_set(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,dict_catchers,max_iter)
    #draw_to_terminal(f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s)
    #draw_to_screen(f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s,screen_width,screen_height)
    #"Game loop" logic for color cycling
    
    if c_ticks >= 60:
        message = "Command:"
    if delete_flag == True:
        message = show_presets(message,max_save_slots)
    if save_flag == True:
        message = "Save as:"
    if load_flag == True:
        message = show_presets(message,max_save_slots)
    while game_cycle == True:
        
        if animation_flag == True:
            if play_animation_flag == True:
                f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s,anim_cache = play_cache(anim_cache,frame)
                video_camera = True
                #print(anim_current_loop)
                #print(anim_loops_max)
                if frame >= anim_length-1:
                    anim_current_loop += 1
                    frame = 0               
                    if anim_current_loop >= anim_loops_max:
                        anim_current_loop = 0
                        animation_flag = False
                        play_animation_flag = False
                        video_camera = False
                        read_comm = ''
                        break
            else:
                f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s = mandelbrot_set(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,dict_catchers,max_iter)
                cache_animation_frame(frame,anim_length,f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s,screen_width,screen_height,anim_cache)
            screen.fill((0,0,0))
            draw_to_screen(f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s,screen_width,screen_height,cycle,c_ticks,video_camera)
            
            terminal_screen = my_font.render(message+' '+fake_terminal, False, (200, 200, 200))
            if play_animation_flag == False:
                screen.blit(terminal_screen, (screen_width//13,screen_height//34*2))
            #if c_ticks % refresh_every == 0:
            #refresh_fractal_colors(ascii_colors,cycle,f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s)
            clock.tick(FPS)
            c_ticks += 1
            pygame.display.flip()
            break

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
                    #cycle = not cycle
                    
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

                #Take keystrokes
                fake_terminal += terminal_keyboard_input(event.key)
                

                
        terminal_screen = my_font.render(message+' '+fake_terminal, False, (250, 250, 250))
        
        screen.fill((0,0,0))
        draw_to_screen(f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s,screen_width,screen_height,cycle,c_ticks,video_camera)
        
        
        screen.blit(terminal_screen, (screen_width//13,screen_height//34*2))
        #if c_ticks % refresh_every == 0:
            #refresh_fractal_colors(ascii_colors,cycle,f_frac_matrix_f,f_width,f_height,f_dict_catchers,f_frac_matrix_s)
        clock.tick(FPS)
        c_ticks += 1
        pygame.display.flip()

    

    
    while True:
        if animation_flag == True:
            #This block edits the global values for an animation
            try:
                new_frame = play_animation(start_keyframe,end_keyframe,frame,anim_length)
            except NameError:
                print('No anim to play')
                animation_flag = False
                break
            #print(new_frame)

            
            xpos = new_frame["xpos"]
            ypos = new_frame["ypos"]
            #width = new_frame["width"]
            #height = new_frame["height"]
            viewX = new_frame["viewX"]
            viewY = new_frame["viewY"]
            scale = new_frame["scale"]
            z_axis = new_frame["z_axis"]
            w_axis = new_frame["w_axis"]
            zoom = new_frame["zoom"]
            power = new_frame["power"]
            c_var_i = new_frame["c_var_i"]
            c_var_r = new_frame["c_var_r"]
            max_iter = new_frame["max_iter"]

            
            frame+=1
            #print(frame)
            
            if frame >= anim_length:
                frame = 0
                animation_flag = False
            else:
                break
        
        

        if not enter:
            read_comm = input(' -')

        if delete_flag == True:
            delete_preset(read_comm,max_save_slots)
            delete_flag = False
            break
        if load_flag == True:
            show_presets(message,max_save_slots)
            
            load_preset(message,read_comm)
            load_flag = False
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
        
        if resize_flag == True:
            try:
                width = int(read_comm)
                height = int(read_comm)
                resize_flag = False
                break
            except ValueError,TypeError:
                resize_flag = False
                #do not break because it's probably another command (and is set up
                #to handle it if it's not)
        if save_flag == True:
            save_settings(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,c_var_i,c_var_r,max_iter,mode,read_comm,max_save_slots)
            save_flag = False
            break
        if read_comm == 'resize' or read_comm == 'size':
            resize_flag = True
            
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
        if read_comm == 'anim':
            print('animation')
            print(anim_counter)
            if anim_counter == 0:
                start_keyframe = {
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
                "max_iter": max_iter
                }
                anim_counter+=1
                break
            elif anim_counter == 1:
                end_keyframe = {
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
                "max_iter": max_iter
                }
                animation_flag = True
                play_animation_flag = False
                frame = 0
                anim_current_loop = 0
                anim_counter = 0
                break
        if read_comm == 'play':
            play_animation_flag = True
            animation_flag = True
            frame = 0
            break
                
            
        if read_comm == 'trace':
            trace_show = not trace_show
            break
        if read_comm == 'cycle':
            cycle = True
            game_cycle = True
        #Save/load preset features
        if read_comm == 'save':
            save_flag = True
            print
            sound_list[0].play()
            break
        if read_comm == 'load':
            load_flag = True
            show_presets(message,max_save_slots)
            sound_list[0].play()
            break
        if read_comm == 'delete':
            delete_flag = True
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
                viewX+=control_factor/(2*zoom)
                continue
            elif read_key == 's':
                if ticker == 1:
                    sound_list[2].play()
                viewX-=control_factor/(2*zoom)
                continue
            elif read_key == 'a':
                if ticker == 1:
                    sound_list[2].play()
                viewY-=control_factor/(2*zoom)
                continue
            elif read_key == 'd':
                if ticker == 1:
                    sound_list[2].play()
                viewY+=control_factor/(2*zoom)
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
