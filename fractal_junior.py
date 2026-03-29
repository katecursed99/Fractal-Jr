#imports
import math
import os
import time
import json
import pygame
from clrprint import *
import numpy as np


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
    if mode == "mandelbrot":
        z = complex(z_axis, 0)
        c = complex(cx, cy)
    elif mode == "julia":
        z = complex(cx+z_axis, cy+w_axis)
        c = complex(c_var_r, c_var_i)
            
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
    #sorts coordinates to trace by distance from last.
    #probably needs to be reworked
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
    #sorts coordinates to trace by distance from last.
    #probably needs to be reworked
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
    for x in range(width):
        x_ticker+=1
        y_ticker=0
        for y in range(height):
            inside=False
            #dyn_update(dyn_var_dict, dyn_pointer, x, y, c_var, z_axis, w_axis)
            scale_x = 3.5 / zoom
            scale_y = 2.0 / zoom
            

            cx = viewX + (x - width/2) * scale
            cy = viewY + (y - height/2) * scale
            
                
            cy*=(height/width)
           
            color_ticker=0
            if mode == "mandelbrot":
                z = complex(z_axis, w_axis)
                c = complex(cx, cy)
            elif mode == "julia":
                z = complex(cx+z_axis, cy+w_axis)
                c = complex(c_var_r, c_var_i)
            y_ticker+=1
            #print(x,y) #Sanity check
            total_ticker+=1
            magnitude_z = (z.real**2+z.imag**2)**0.5
            while abs(magnitude_z) < 2 and color_ticker<=max_iter:
                #if is_in_main_cardioid(cx,cy):   #Removed because idk how reliable it is when shifting in 5 dimensions, that's a mandelbrot thing I think?
                #    inside=True
                #    break
                color_ticker+=1
                z = z**power+(c)
                magnitude_z = (z.real**2+z.imag**2)**0.5
                if color_ticker >= max_iter:
                    inside=True
                    #frac_matrix_f.append(fill_color)

                    #print(x,y) #Sanity check

                    
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
                        #print(x,y) #Sanity check
                        frac_tracer_list.append(x)
                        frac_tracer_list.append(y)
                    
                        
                    
                    #print('nope')
                    break
            fill_color = 1 #default
            if inside==True:
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
                #print(frac_matrix_f)
                        
                
            
            
            #frac_canv.append(m_path)
            #canvas.append(frac_canv)
    
    #frac_tracer = draw.Lines(frac_tracer_list[0]*scale+xpos+width//2, frac_tracer_list[1]*scale+ypos+height//2,stroke='yellow',stroke_width=1,fill='none',closed='true')
    point_list_x = []
    point_list_y = []
    projected_point_list = []
    for i in range(0, len(frac_tracer_list), 2):
        #frac_canv2.append(draw.Circle(frac_tracer_list[i]*scale+xpos+width//2, frac_tracer_list[i+1]*scale+ypos+height//2, 0.5, fill='yellow',stroke='yellow',stroke_width=stroke_large))
        #frac_canv2.append(frac_tracer.T(frac_tracer_list[i]*scale+xpos+width//2, frac_tracer_list[i+1]*scale+ypos+height//2))
        #print(frac_tracer_list[i]*scale+xpos+width//2, frac_tracer_list[i+1]*scale+ypos+height//2)
        point_list_x.append(frac_tracer_list[i]*scale+xpos+width//2)
        point_list_y.append(frac_tracer_list[i+1]*scale+ypos+height//2)
        current_point = (frac_tracer_list[i]*scale+xpos+width//2,frac_tracer_list[i+1]*scale+ypos+height//2)
        projected_point_list.append(current_point)
    array_data = np.array(projected_point_list)

    #print(len(array_data))
    #last_point = array_data[0] 
    
    #print(array_data)
    #canvas.append(frac_canv2)

    list_data_new = connect_dots(array_data)
    
    for i in range(0,(len(list_data_new)//2)+2,2):
        
        pass

    draw_to_terminal(frac_matrix_f,width,height,dict_catchers,frac_matrix_s)
    


def draw_to_terminal(frac_matrix_f,width,height,dict_catchers,frac_matrix_s):
    #Variable number of buckets, in dict_catchers. When one starts being filled, the
    #other dumps to the terminal
    #
    #Set up

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
dyn_pointer = 'y'
dev_mode = False
mode = 'mandelbrot'

def save_settings(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,c_var_i,c_var_r,max_iter,mode):


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

    data.append(save_data)

    with open('presets.json', 'w') as f:
        json.dump(data, f, indent=2)

def load_preset():
    global xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,c_var_i,c_var_r,max_iter,mode

    with open('presets.json','r') as preset_store:
        data_temp = preset_store.read()
        data_store = json.loads(data_temp)
        for diction in data_store:
            print('Presets: '+diction["name"], end=' ')
        #print(dict(data_store))
        preset_name = str(input('\nEnter a preset to load'))
        i=0
        for diction in data_store:
            
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

                



def dyn_update(dyn_var_dict, pointer, x, y, const, z_axis, w_axis):
    
# Note: My first idea for this structure was just exec() and arbitrary code execution
# and today I learned a valuable lesson in program security :)

# This isn't actually implemented right now because it was easier to just do
# Mandelbrot and Julia mode, but if I add a third axis later it might be useful
# to keep around
    dyn_var_dict["y-axis"]["pointer"] = pointer
    if dyn_var_dict["y-axis"]["pointer"] == 'y':
        dyn_var_dict["y-axis"]["value"] = y
    if dyn_var_dict["y-axis"]["pointer"] == 'xy':
        dyn_var_dict["y-axis"]["value"] = x*y
    elif dyn_var_dict["y-axis"]["pointer"] == 'const':
        dyn_var_dict["y-axis"]["value"] = const
    elif dyn_var_dict["y-axis"]["pointer"] == 'w':
        dyn_var_dict["y-axis"]["value"] = w_axis
        if y==height-1:
            w_axis += 1
    elif dyn_var_dict["y-axis"]["pointer"] == 'z':
        dyn_var_dict["y-axis"]["value"] = z_axis
        if y==height-1:
            z_axis += 1


dyn_var_dict = {"y-axis":  {"value": 0, "update": dyn_update, "pointer": "z"}}

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
        "thresh":max_iter
            }
        ]

for dicti in dict_catchers:
    dicti["thresh"] = max_iter//len(dict_catchers)*dicti["id"]//4
    
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


draw_title(ascii_colors,20)

while True:
    
    mandelbrot_set(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,dict_catchers,max_iter)
    

    
    while True:
        clrprint('command:',clr='white',end='')
        read_comm = input(' -')
        if read_comm == 'help':
            print('\n       Enter commands, then hit enter to run!                           ')
            print('       W +              -   +          -   +            -   +         ')
            print('     A<->D = x,y axes | X<->Z = zoom | V<->F = Z-axis | G<->B = kata/ana')
            print('     - S    ')
            print('     N<->H = power | M<->J = c-factor (real)')
            print('     You can issue multiple 1-char commands per entry to be more efficient')
            print('       Capital letters have the same function but are 10x as powerful')
            print('     Keyword commands: mandelbrot, julia, resize, help, save, load, quit')
            clrprint('\n       command:',clr='white',end='')
            read_comm = input(' -')
        if read_comm == 'resize':
            try:
                new_size = int(input('\n       New size: '))
                width = new_size
                height = new_size
                #clrprint('\n       command:',clr='white',end='')
                #read_comm = input(' -')
                continue
            except ValueError:
                print('<- Back')
                continue
            
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
        if read_comm == 'save':
            save_settings(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,c_var_i,c_var_r,max_iter,mode)
            sound_list[0].play()
            break
        if read_comm == 'load':
            load_preset()
            sound_list[0].play()
            break
        if read_comm == 'delete':
            pass
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
                viewX+=control_factor*(2+zoom)
                continue
            elif read_key == 's':
                if ticker == 1:
                    sound_list[2].play()
                viewX-=control_factor*(2+zoom)
                continue
            elif read_key == 'a':
                if ticker == 1:
                    sound_list[2].play()
                viewY-=control_factor*(2+zoom)
                continue
            elif read_key == 'd':
                if ticker == 1:
                    sound_list[2].play()
                viewY+=control_factor*(2+zoom)
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
            
        break
           
        
    if read_comm == 'quit':
        print('Have a lovely day <3')
        time.pause(2)
        sys.exit(0)
        break
time.sleep(0.05)
mandelbrot_set(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,power,dict_catchers,max_iter)



#mandelbrot_set(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom)
