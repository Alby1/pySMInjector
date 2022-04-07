
import socket
import traceback
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import struct
import mouse
import time
import pygame
from decimal import Context
import json


# TODO:
# buttons support:
# | JSON for settings
# | Button class with name, channel, value (boolean?)
# | handle value change
# | send value to syringe

# prettify GUI: 
# - show axis value as a bar (better for standard or inverted) or slider/ scrollbar (better for centered) (how?)
# \ show axis name instead of index (what is shown for unnamed axis, index? should it show both every time?)
# * show buttons (all of them but change pressed ones with different color or just pressed ones? do I show the button name, index, both or index only for unnamed ones?)
# - set max axis range (real_max and virtual_max, just like type?)
# - "You have no controllers connected" screen

# polish up code:
# | put "everything" in a function and call it in a try catch in a while running loop whereas running is the same variable in the inside while loop, so that the program does not quit on error but keeps rebooting (is it a good idea?)
# | some kind of self diagnostics to try fixing itself
# - documentation
# | create .bat code to automate pyinstaller (run pyinstaller > move .exe file from dist to main folder > delete build and dist folders and .spec file ?> zip .exe and settings files)
# | add_setting()

# ease user use:
# * create GitHub page for easy distribution
# - add syringe path as setting and automatically open it at the start


def startup():
    global UDP_IP
    global UDP_PORT
    global SOCK
    UDP_IP = get_setting("IP")
    UDP_IP = get_setting("IP")
    UDP_PORT = 25752
    print(f'\nSending packets to {UDP_IP}:{UDP_PORT}')
    SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    MESSAGE = [3]
    SOCK.sendto(bytes(MESSAGE), (UDP_IP, UDP_PORT))



"""maxX = 0
maxY = 0
while True:
    mP = mouse.get_position()
    print(mP)
    x = mP[0]
    y  = mP[1]
    maxX = max(maxX, x)
    maxY = max(maxY, y)


    sock.sendto(struct.pack(">BId", 1, 6, 1 - x / (maxX / 2)), (UDP_IP, UDP_PORT))
    sock.sendto(struct.pack(">BId", 1, 5, 1 - y / (maxY / 2)), (UDP_IP, UDP_PORT))
    time.sleep(0.1)"""



def read_axis_json(settings_array_name):
    with open('axis_settings.json', 'r') as file:
        read = file.read()
        if len(read) < 1:
            return []

        js = json.loads(read)
        #print(js[settings_array])
        return js[settings_array_name]
        

def write_axis_json(settings_array_names, settings_array_values):
    with open('axis_settings.json', 'w') as file:
        out_str = '{ '
        for i in range(len(settings_array_names)):
            out_str += f'{"," if i != 0 else ""} "{settings_array_names[i]}": {json.dumps(settings_array_values[i])}'
        
        out_str += ' }'
        file.write(out_str)



def read_buttons_json(settings_array_name):
    with open('buttons_settings.json', 'r') as file:
        read = file.read()
        if len(read) < 1:
            return []

        js = json.loads(read)
        #print(js[settings_array])
        return js[settings_array_name]


def write_buttons_json(settings_array_names, settings_array_values):
    with open('buttons_settings.json', 'w') as file:
        out_str = '{ '
        for i in range(len(settings_array_names)):
            out_str += f'{"," if i != 0 else ""} "{settings_array_names[i]}": {json.dumps(settings_array_values[i])}'
        
        out_str += ' }'
        file.write(out_str)


def get_setting(toFind : str):
    with open('settings.txt', 'r') as file:
        read = file.read()

        if len(read) < 1:
            return ''

        setting = read[read.find(f'{toFind}:') + len(toFind) + 1 : len(read)]
        
        setting = setting[0 : (setting.find(';')) ]

        return setting


def add_setting(setting: str, value: str):
    with open('settings.txt', 'a') as file:
        file.write(f'\n{setting}:{value};')


def set_setting(setting: str, value: str):
    read = ''
    with open('settings.txt', 'r') as file:
        read = file.read()

    if read.find(f'{setting}:') < 0 or len(read) < 0:
        add_setting(setting, value)
        return
    
    output = read[0 : read.find(f'{setting}:') + len(setting) + 1] + value
        
    output += read[read.find(f'{setting}:') + len(setting) + len(get_setting(setting)) + 1 : len(read)]
    

    with open('settings.txt', 'w') as file:
        file.write(output)



def pygame_main():
    global axis
    pygame.event.set_grab(True)
    pygame.display.set_caption('Scrap Mechanic Injector')
    surface = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    global running
    running = True
 
    font = pygame.font.Font(None, 20)
    linesize = font.get_linesize()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for joy in joysticks:
        joy.init()
 
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
 
        surface.fill((0,0,0))
        position = [10, 10]
 
        scrolled_axis = 0
        scrolled_buttons = 0

        for joy in joysticks:
            image = font.render(joy.get_name(), 1, (0,200,0))
            surface.blit(image, position)
            position[1] += linesize
 
            """image = font.render('button count: {0}'.format(joy.get_numbuttons()), 1, (0,200,0))
            surface.blit(image, position)
            position[1] += linesize
 
            for i in range(joy.get_numbuttons()):
                if joy.get_button(i):
                    image = font.render('{0}: push'.format(i), 1, (0,200,0))
                    surface.blit(image, position)
                    position[1] += linesize"""
            
            for i in range(joy.get_numaxes()):
                j = scrolled_axis
                if(axis[j].raw_value != joy.get_axis(i)):
                    axis[j].update_value(joy.get_axis(i))
                    if(axis[j].channel >= 0):
                        packet = axis[j].create_send_packet()
                        axis[j].send(packet)
                image = font.render(f'{axis[j].name if axis[j].name != "" else i}: {axis[j].value}', 1, (0,200,0))
                surface.blit(image, position)
                position[1] += linesize
                scrolled_axis += 1

            for i in range(joy.get_numbuttons()):
                j = scrolled_buttons
                if(buttons[j].value != joy.get_button(i)):
                    buttons[j].update_value(joy.get_button(i))
                    if(buttons[j].channel >= 0):
                        packet = buttons[j].create_send_packet()
                        buttons[j].send(packet)
                image = font.render(f'{buttons[j].name if buttons[j].name != "" else i}: {buttons[j].value}', 1, (0,200,0))
                surface.blit(image, position)
                position[1] += linesize
                scrolled_buttons += 1


        global fixups_index
        fixups_index = 0
        pygame.display.flip()
        clock.tick(20)
 
    pygame.quit()
 



class Axis:
    plt_axis = 0
    plt_slider = 0
    plt_bar_axis = 0
    id = 0
    channel = 0
    raw_value = 0
    value = 0
    slider_minimum = 0
    slider_maximum = 0
    name = ''
    virtual_type = ''
    real_type = ''

    def update(self, val):
        self.value = val
        print(f'{self.id}: {val}')
        packet = self.create_send_packet()
        self.send(packet)
        self.plt_bar_axis.clear()
        self.plt_bar_axis.bar(x= self.name, height=val, color= (0,0,0))
    
    def create_send_packet(self):
        return struct.pack(">BId", 1, self.channel, self.value)

    def send(self, packet):
        SOCK.sendto(packet, (UDP_IP, UDP_PORT))

    def update_value(self, new_value):
        self.raw_value = new_value
        
        c = Context(prec = 5)
        new_value = c.create_decimal(new_value)

        if(self.real_type == 'centered'):
            if(self.virtual_type == 'standard'):
                new_value = (new_value + 1) / 2
            elif(self.virtual_type == 'inverted'):
                new_value = ((new_value + 1) / 2)
                new_value = 1 - new_value
        elif(self.real_type == 'standard'):
            if(self.virtual_type == 'centered'):
                new_value = (new_value * 2) - 1
            elif(self.virtual_type == 'inverted'):
                new_value = 1 - new_value + 1
        else:
            if(self.virtual_type == 'standard'):
                new_value = (new_value + 1) / 2
            elif(self.virtual_type == 'centered'):
                new_value = 1 - new_value

        self.value = new_value
        #print(f'{self.value} raw value: {self.raw_value}')


    def update_status(self, type = '', ):
        if(type != ''):
            self.virtual_type = type
            self.type_selector()
        

    def type_selector(self):
        if self.virtual_type == 'standard':
            self.slider_minimum = 0
            self.slider_maximum = 1
        elif self.virtual_type == 'inverted':
            self.slider_minimum = -1
            self.slider_maximum = 0
        elif self.virtual_type == 'centered':
            self.slider_minimum = -1
            self.slider_maximum = 1

    def __init__(self, id, channel, virtual_type = 'standard', name = 'null', real_type = 'centered'):
        self.id = id
        self.channel = channel
        self.virtual_type = virtual_type
        self.real_type = real_type

        if name == 'null':
            name = f'Axis {id}:'
        self.name = name

        self.type_selector()
    
        self.plt_axis = plt.axes([0.25, 0.1*id, 0.65, 0.03])

        self.plt_slider = Slider(self.plt_axis, name, self.slider_minimum, self.slider_maximum, 0.0)
        self.plt_slider.on_changed(self.update)
        global fig
        self.plt_bar_axis = fig.add_subplot(adjustable= 'box', aspect=0.3)

    def __str__(self):
        return f'Axis n.{self.id} {self.value}'


class Button:
    name = ''
    channel = -1
    value = False
    
    def __init__(self, name: str = '', channel: int = -1, value: int = 0):
        self.name = name
        self.channel = channel
        self.value = value

    def update_value(self, newValue: bool):
        self.value = newValue

    def create_send_packet(self):
        return struct.pack(">BId", 1, self.channel, int(self.value))

    def send(self, packet):
        SOCK.sendto(packet, (UDP_IP, UDP_PORT))



def main():
    global fig
    fig = plt.figure()
    plt.subplots_adjust(bottom=0.4)


    """ accelerator = Axis(1, 5, name='Acceleratore')
    brake = Axis(2, 6, name='Freno')
    steering = Axis(3, 7, 'centered', 'Sterzo') 
    plt.show() """

    global axis
    axis = []

    global buttons
    buttons = []

    axis_channels = read_axis_json('channels')
    axis_labels = read_axis_json('labels')
    virtual_types = read_axis_json('virtual_types')
    real_types = read_axis_json('real_types')

    buttons_channels = read_buttons_json('channels')
    buttons_labels = read_buttons_json('labels')



    pygame.init()

    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

    num_axis = 0
    num_buttons = 0

    for joy in joysticks:
        for i in range(joy.get_numaxes()):
            num_axis += 1
        for i in range(joy.get_numbuttons()):
            num_buttons += 1

    for i in range(num_axis):
        try: axis_channels[i]
        except: axis_channels.append(-1)

        try: axis_labels[i]
        except: axis_labels.append('')

        try: virtual_types[i]
        except: virtual_types.append('standard')

        try: real_types[i]
        except: real_types.append('centered')

    write_axis_json(["channels", "labels", "virtual_types", "real_types"], [axis_channels, axis_labels, virtual_types, real_types])

    for i in range(num_buttons):
        try: buttons_channels[i]
        except: buttons_channels.append(-1)
        
        try: buttons_labels[i]
        except: buttons_labels.append("")

    write_buttons_json(["channels", "labels"], [buttons_channels, buttons_labels])

    for i in range(num_axis):
        axis.append(Axis(i, channel=axis_channels[i], name=axis_labels[i], virtual_type=virtual_types[i], real_type=real_types[i]))

    for i in range(num_buttons):
        buttons.append(Button(buttons_labels[i], buttons_channels[i]))

    pygame_main()



global running
running = True

fixup_output_positive = 'Fixup succesful, restarting'
fixup_output_negative = 'Fixup unsucceful, trying next one'

def fixup_axis_settings_file():
    try: 
        open('axis_settings.json', 'r')
        print(fixup_output_positive)
    except:
        open('axis_settings.json', 'w+')
        print(fixup_output_negative)

def fixup_buttons_settings_file():
    try: 
        open('buttons_settings.json', 'r')
        print(fixup_output_positive)
    except:
        open('buttons_settings.json', 'w+')
        print(fixup_output_negative)

def fixup_settings_file():
    try:
        open('settings.txt', 'r')
        print(fixup_output_positive)
    except:
        open('settings.txt', 'w+')
        print(fixup_output_negative)

def fixup_no_default_ip():
    set_setting('IP', '127.0.0.1')
    print(fixup_output_positive)


global fixups_index
fixups_index = 0

fixups = {
    1 : fixup_axis_settings_file,
    2 : fixup_buttons_settings_file,
    3 : fixup_settings_file,
    4 : fixup_no_default_ip
}

while running:
    try:
        startup()
        main()
    except KeyboardInterrupt:
        running = False
    except Exception as e:
        fixups_index += 1
        print(f'Error occurred, trying automatic fixup n.{fixups_index}')

        print(traceback.format_exc())

        try:
            fixups[fixups_index]()
        except:
            running = False
            #print(e)
            print('Automatic error fixup unavailable. Quitting program...')
            




""" from subprocess import Popen
p = Popen(['watch', 'ls']) # something long running
# ... do other stuff while subprocess is running
p.terminate() """


