import math
from clrprint import *
import numpy as np
import os
import time

def is_in_mandelbrot_set(x,y,z_axis,w_axis,zoom,width,height,viewX,viewY):
    scale_x = 3.5 / zoom
    scale_y = 2.0 / zoom
    cx = ((x - viewX) / width) * scale_x - scale_x/2
    cy = ((y - viewY) / height) * scale_y - scale_y/2
    cy*=(height/width)
    max_iter=24
    if is_in_main_cardioid(cx,cy):
        return True
    c = complex(cx, cy)
    color_ticker=0
    z=complex(z_axis,w_axis)
    
            
    magnitude_z = (z.real**2+z.imag**2)**0.5
    while abs(magnitude_z) < 2 and color_ticker<=max_iter:
                
        color_ticker+=1
        z = z**2+c
        magnitude_z = (z.real**2+z.imag**2)**0.5
        if color_ticker >= max_iter:
            return True
            break
    return False

def connect_dots_inner(array_data,super_list):
    
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
    
def is_in_main_cardioid(cx,cy):
    # Main cardioid check
    p = (cx - 0.25)**2 + cy**2
    if p * (p + (cx - 0.25)) <= 0.25 * cy**2:
        return True

def mandelbrot_set(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,dict_catchers):
    if zoom==0:
        zoom+=1
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
            max_iter=24
            scale_x = 3.5 / zoom
            scale_y = 2.0 / zoom
            cx = ((x - viewX) / width) * scale_x - scale_x/2
            cy = ((y - viewY) / height) * scale_y - scale_y/2
            
                
            cy*=(height/width)
            c = complex(cx, cy)
            color_ticker=0
            z=complex(z_axis,w_axis)
            y_ticker+=1
            #print(x,y) #Sanity check
            total_ticker+=1
            magnitude_z = (z.real**2+z.imag**2)**0.5
            while abs(magnitude_z) < 2 and color_ticker<=max_iter:
                if is_in_main_cardioid(cx,cy):
                    inside=True
                    break
                color_ticker+=1
                z = z**2+c
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
                            if is_in_mandelbrot_set(x+x2,y+y2,z_axis,w_axis,zoom,width,height,viewX,viewY):
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
    clrprint('Coords: x:'+str(round(viewX,1))+'y:'+str(round(viewY,1))+'i, z-axis:'+str(round(z_axis,1))+', c-axis:'+str(round(w_axis,1))+' zoom lvl:'+str(round(zoom,1)), clr='red', end=' ')
def draw_to_terminal(frac_matrix_f,width,height,dict_catchers,frac_matrix_s):
    #Two buckets, in_catcher and out_catcher. When one starts being filled, the
    #other dumps to the terminal
    #
    #Set up
    os.system('cls' if os.name == 'nt' else 'clear')
    counter = 0
    print('\n       ',end='')
    

    
    #Loop for each pixel
    for i, e in enumerate(frac_matrix_f):
        row_end = (i + 1)% width == 0
        spill_over = frac_matrix_f[i]%len(ascii_density)
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
            print('\n       ',end='')  # <-- the ONLY place newline happens
    # flush remaining
    for dict_ent in dict_catchers:
        if dict_ent['catcher']:
            
            clrprint(''.join(dict_ent['catcher']), clr=dict_ent['color'], end='')
   
            dict_ent['catcher'] = []
        #print(e)


xpos = 0
ypos = 0
width = 32
height = 32
viewX = 0
viewY = 0
scale = 0
z_axis = 0
w_axis = 0
zoom = 1

ascii_density = list('░▒▓█')

dict_catchers = [{
        "id":1,
        "catcher":[],
        "flag":False,
        "color":'black',
        "char":'██',
        "thresh":3
            },{
        "id":2,
        "catcher":[],
        "flag":False,
        "color":'grey',
        "char":'▓▓',
        "thresh":7
            },{
        "id":3,
        "catcher":[],
        "flag":False,
        "color":'green',
        "char":'▓▓',
        "thresh":11
            },{
        "id":4,
        "catcher":[],
        "flag":False,
        "color":'purple',
        "char":'▒▒',
        "thresh":15
            },{
        "id":5,
        "catcher":[],
        "flag":False,
        "color":'red',
        "char":'▒▒',
        "thresh":20
            },{
        "id":6,
        "catcher":[],
        "flag":False,
        "color":'yellow',
        "char":'░░',
        "thresh":24
            }
        ]

#mandelbrot_set(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom)
#time.sleep(1)


clrprint('   ______   ______     ______     ______     ______   ______     __         ', clr='black')
clrprint('  /\\  ___\\ /\\  == \\   /\\  __ \\   /\\  ___\\   /\\__  _\\ /\\  __ \\   /\\ \\        ', clr='grey')
clrprint('  \\ \\  __\\ \\ \\  __<   \\ \\  __ \\  \\ \\ \\____  \\/_/\\ \\/ \\ \\  __ \\  \\ \\ \\____   ', clr='green')
clrprint('   \\ \\_\\    \\ \\_\\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\    \\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\  ', clr='purple')
clrprint('    \\/_/     \\/_/ /_/   \\/_/\\/_/   \\/_____/     \\/_/   \\/_/\\/_/   \\/_____/  ', clr='red')
clrprint('                                                                            ', clr='yellow')
clrprint('                                                           __     ______    ', clr='pink')
clrprint('                                                          /\\ \\   /\\  == \\   ', clr='black')
clrprint('                                                         _\\_\\ \\  \\ \\  __<   ', clr='grey')
clrprint('                                                        /\\_____\\  \\ \\_\\ \\_\\ ', clr='green')
clrprint('                                                        \\/_____/   \\/_/ /_/ ', clr='purple')
clrprint('                                                                            ', clr='red')
clrprint('     © Katherina L Jesek               2026                MIT License',clr='red')
print('')
print('')
time.sleep(0.5)
os.system('cls' if os.name == 'nt' else 'clear')
clrprint(' ______   ______     ______     ______     ______   ______     __         ', clr='grey')
clrprint('/\\  ___\\ /\\  == \\   /\\  __ \\   /\\  ___\\   /\\__  _\\ /\\  __ \\   /\\ \\        ', clr='green')
clrprint('\\ \\  __\\ \\ \\  __<   \\ \\  __ \\  \\ \\ \\____  \\/_/\\ \\/ \\ \\  __ \\  \\ \\ \\____   ', clr='purple')
clrprint(' \\ \\_\\    \\ \\_\\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\    \\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\  ', clr='red')
clrprint('  \\/_/     \\/_/ /_/   \\/_/\\/_/   \\/_____/     \\/_/   \\/_/\\/_/   \\/_____/  ', clr='yellow')
clrprint('                                                                          ', clr='pink')
clrprint('                                                         __     ______    ', clr='black')
clrprint('                                                        /\\ \\   /\\  == \\   ', clr='grey')
clrprint('                                                       _\\_\\ \\  \\ \\  __<   ', clr='green')
clrprint('                                                      /\\_____\\  \\ \\_\\ \\_\\ ', clr='purple')
clrprint('                                                      \\/_____/   \\/_/ /_/ ', clr='red')
clrprint('                                                                          ', clr='black')
clrprint('     © Katherina L Jesek               2026                MIT License',clr='red')
print('')
print('')
time.sleep(0.5)
os.system('cls' if os.name == 'nt' else 'clear')
clrprint(' ______   ______     ______     ______     ______   ______     __         ', clr='green')
clrprint('/\\  ___\\ /\\  == \\   /\\  __ \\   /\\  ___\\   /\\__  _\\ /\\  __ \\   /\\ \\        ', clr='purple')
clrprint('\\ \\  __\\ \\ \\  __<   \\ \\  __ \\  \\ \\ \\____  \\/_/\\ \\/ \\ \\  __ \\  \\ \\ \\____   ', clr='red')
clrprint(' \\ \\_\\    \\ \\_\\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\    \\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\  ', clr='yellow')
clrprint('  \\/_/     \\/_/ /_/   \\/_/\\/_/   \\/_____/     \\/_/   \\/_/\\/_/   \\/_____/  ', clr='pink')
clrprint('                                                                          ', clr='black')
clrprint('                                                         __     ______    ', clr='grey')
clrprint('                                                        /\\ \\   /\\  == \\   ', clr='green')
clrprint('                                                       _\\_\\ \\  \\ \\  __<   ', clr='purple')
clrprint('                                                      /\\_____\\  \\ \\_\\ \\_\\ ', clr='red')
clrprint('                                                      \\/_____/   \\/_/ /_/ ', clr='black')
clrprint('                                                                          ', clr='grey')
clrprint('      © Katherina L Jesek               2026                MIT License',clr='red')
clrprint('      type help and hit enter for info on commands!  ',clr='yellow')
print('')
time.sleep(0.5)
os.system('cls' if os.name == 'nt' else 'clear')
clrprint('   ______   ______     ______     ______     ______   ______     __         ', clr='black')
clrprint('  /\\  ___\\ /\\  == \\   /\\  __ \\   /\\  ___\\   /\\__  _\\ /\\  __ \\   /\\ \\        ', clr='grey')
clrprint('  \\ \\  __\\ \\ \\  __<   \\ \\  __ \\  \\ \\ \\____  \\/_/\\ \\/ \\ \\  __ \\  \\ \\ \\____   ', clr='green')
clrprint('   \\ \\_\\    \\ \\_\\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\    \\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\  ', clr='purple')
clrprint('    \\/_/     \\/_/ /_/   \\/_/\\/_/   \\/_____/     \\/_/   \\/_/\\/_/   \\/_____/  ', clr='red')
clrprint('                                                                            ', clr='yellow')
clrprint('                                                           __     ______    ', clr='pink')
clrprint('                                                          /\\ \\   /\\  == \\   ', clr='black')
clrprint('                                                         _\\_\\ \\  \\ \\  __<   ', clr='grey')
clrprint('                                                        /\\_____\\  \\ \\_\\ \\_\\ ', clr='green')
clrprint('                                                        \\/_____/   \\/_/ /_/ ', clr='purple')
clrprint('                                                                            ', clr='red')
clrprint('     © Katherina L Jesek               2026                MIT License',clr='red')
clrprint('      type help and hit enter for info on commands!  ',clr='yellow')
clrprint('      loading fractal . . .')
time.sleep(0.5)
os.system('cls' if os.name == 'nt' else 'clear')
clrprint(' ______   ______     ______     ______     ______   ______     __         ', clr='grey')
clrprint('/\\  ___\\ /\\  == \\   /\\  __ \\   /\\  ___\\   /\\__  _\\ /\\  __ \\   /\\ \\        ', clr='green')
clrprint('\\ \\  __\\ \\ \\  __<   \\ \\  __ \\  \\ \\ \\____  \\/_/\\ \\/ \\ \\  __ \\  \\ \\ \\____   ', clr='purple')
clrprint(' \\ \\_\\    \\ \\_\\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\    \\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\  ', clr='red')
clrprint('  \\/_/     \\/_/ /_/   \\/_/\\/_/   \\/_____/     \\/_/   \\/_/\\/_/   \\/_____/  ', clr='yellow')
clrprint('                                                                          ', clr='pink')
clrprint('                                                         __     ______    ', clr='black')
clrprint('                                                        /\\ \\   /\\  == \\   ', clr='grey')
clrprint('                                                       _\\_\\ \\  \\ \\  __<   ', clr='green')
clrprint('                                                      /\\_____\\  \\ \\_\\ \\_\\ ', clr='purple')
clrprint('                                                      \\/_____/   \\/_/ /_/ ', clr='red')
clrprint('                                                                          ', clr='black')
clrprint('     © Katherina L Jesek               2026                MIT License',clr='red')
clrprint('      type help and hit enter for info on commands!  ',clr='yellow')
clrprint('      loading fractal . . .')
time.sleep(0.5)
os.system('cls' if os.name == 'nt' else 'clear')
clrprint(' ______   ______     ______     ______     ______   ______     __         ', clr='green')
clrprint('/\\  ___\\ /\\  == \\   /\\  __ \\   /\\  ___\\   /\\__  _\\ /\\  __ \\   /\\ \\        ', clr='purple')
clrprint('\\ \\  __\\ \\ \\  __<   \\ \\  __ \\  \\ \\ \\____  \\/_/\\ \\/ \\ \\  __ \\  \\ \\ \\____   ', clr='red')
clrprint(' \\ \\_\\    \\ \\_\\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\    \\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\  ', clr='yellow')
clrprint('  \\/_/     \\/_/ /_/   \\/_/\\/_/   \\/_____/     \\/_/   \\/_/\\/_/   \\/_____/  ', clr='pink')
clrprint('                                                                          ', clr='black')
clrprint('                                                         __     ______    ', clr='grey')
clrprint('                                                        /\\ \\   /\\  == \\   ', clr='green')
clrprint('                                                       _\\_\\ \\  \\ \\  __<   ', clr='purple')
clrprint('                                                      /\\_____\\  \\ \\_\\ \\_\\ ', clr='red')
clrprint('                                                      \\/_____/   \\/_/ /_/ ', clr='black')
clrprint('                                                                          ', clr='grey')
clrprint('      © Katherina L Jesek               2026                MIT License',clr='red')
clrprint('      type help and hit enter for info on commands!  ',clr='yellow')
clrprint('      loading fractal . . .')


time.sleep(2)
os.system('cls' if os.name == 'nt' else 'clear')

while True:
    
    mandelbrot_set(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom,dict_catchers)
    
    time.sleep(0.1)
    
    while True:
        clrprint('command:',clr='white',end='')
        read_comm = input(' -')
        if read_comm == 'help':
            print('\n       Enter commands, then hit enter to run!                           ')
            print('       W +              -   +          -   +            -   +         ')
            print('     A<->D = x,y axes | X<->Z = zoom | V<->F = Z-axis | G<->B = W-axis')
            print('       - S    ')
            print('')
            print('     You can issue multiple 1-char commands per entry to be more efficient')
            print('           (ie. "ass" is a valid command for -1 on the')
            print('             x axis and -2 on the imaginary/y axis)')
            print('     Keyword commands: resize, help, quit')
            clrprint('\n       command:',clr='white',end='')
            read_comm = input(' -')
        if read_comm == 'resize':
            try:
                new_size = int(input('\n       New size: '))
                width = new_size
                height = new_size
                #clrprint('\n       command:',clr='white',end='')
                #read_comm = input(' -')
            except ValueError:
                print('<- Back')
                continue
            
        if read_comm == 'quit':
            break
        for read_key in list(read_comm):
            #zooming in and out
            if read_key == 'z':
                zoom+=0.1
                if zoom == 0:
                    zoom+=1
                continue
            elif read_key == 'x':
                zoom-=0.1
                if zoom == 0:
                    zoom-=1
                continue
                
            elif read_key == 'w':
                viewX+=0.2
                continue
            elif read_key == 's':
                viewX-=0.2
                continue
            elif read_key == 'a':
                viewY-=0.1
                continue
            elif read_key == 'd':
                viewY+=0.1
                continue
            elif read_key == 'v':
                z_axis-=0.1
                continue
            elif read_key == 'f':
                z_axis+=0.1
                continue
            elif read_key == 'g':
                w_axis+=0.1
                continue
            elif read_key == 'b':
                w_axis-=0.1
                continue
        break
           
        
    if read_comm == 'quit':
        print('Have a lovely day <3')
        time.pause(2)
        sys.exit(0)
        break
    




#mandelbrot_set(xpos,ypos,width,height,viewX,viewY,scale,z_axis,w_axis,zoom)
