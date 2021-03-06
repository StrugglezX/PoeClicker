

from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller
import pynput
from PIL import ImageGrab
from time import sleep
import threading
import time

exiting = False
put_loot_away = False
pick_up_item = False
do_flasks = False
item_coordinate = None
mouse = MouseController()
keyboard = Controller()


def move_mouse(x, y):
    def set_mouse_position(x, y):
        mouse.position = (int(x), int(y))
    def smooth_move_mouse(from_x, from_y, to_x, to_y, speed=0.2):
        steps = 40
        sleep_per_step = speed // steps
        x_delta = (to_x - from_x) / steps
        y_delta = (to_y - from_y) / steps
        for step in range(steps):
            new_x = x_delta * (step + 1) + from_x
            new_y = y_delta * (step + 1) + from_y
            set_mouse_position(new_x, new_y)
            sleep(sleep_per_step)
    return smooth_move_mouse(
        mouse.position[0],
        mouse.position[1],
        x,
        y
    )

def left_mouse_click():
    mouse.click(Button.left)
    
def ctrl_left_mouse_click():
    mouse.click(Button.left)
    
def hook_keyboard():
    from pynput.keyboard import Key
    from pynput.keyboard import Listener


    def on_press(key):
        pass

    def on_release(key):
        global exiting
        global put_loot_away
        global pick_up_item
        global do_flasks
        try:
            if key.char == '/':
                put_loot_away = True
            elif key.char == '`':
                print('should exit')
                exiting = True
            elif key.char == 'm':
                print('should exit')
                exiting = True
            elif key.char == '+':
                print('should exit')
                exiting = True
            elif key.char == '.':
                do_flasks = not do_flasks
            elif key.char == '\\':
                pick_up_item = not pick_up_item
        except Exception as e:
            print('exception occured {}', e)
            return

    # Collect events until released
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()        

def ItemThread():
    while True:
        sleep(0.5)
        image = ImageGrab.grab()
        total_width, total_height = image.size
        start_x = int(total_width * 0.2)
        end_x = int(total_width * 0.8)
        start_y = int(total_height * 0.1)
        end_y = int(total_height * 0.9)
        current_width = start_x
        current_height = start_y
        width_increment = 4
        height_increment = 4
        
        red_tolerance = 5
        green_tolerance = 5
        blue_tolerance = 5
        
        expected_pixels = []
        expected_pixels.append( (38, 133, 180) )
        found_coordinate = None
        
        while current_width < end_x and not found_coordinate:
        
            while current_height < end_y and not found_coordinate:
                coordinate = (current_width, current_height)
                pixel = image.getpixel(coordinate)
                for expected_pixel in expected_pixels:
                    if not found_coordinate:
                        red_diff = abs(pixel[0] - expected_pixel[0])
                        green_diff = abs(pixel[1] - expected_pixel[1])
                        blue_diff = abs(pixel[2] - expected_pixel[2])
                        
                        if red_diff < red_tolerance and green_diff < green_tolerance and blue_diff < blue_tolerance:
                            found_coordinate = coordinate
                
                current_height = current_height + height_increment
            current_width = current_width + width_increment
            current_height = start_y
        item_coordinate = found_coordinate
        
keyboard_thread = threading.Thread(target=hook_keyboard)
keyboard_thread.setDaemon(True)
keyboard_thread.start()
item_thread = threading.Thread(target=ItemThread)
item_thread.setDaemon(True)
item_thread.start()

def PutLootAway():
    start_x = 3323#todo
    start_y = 1073#todo
    square_size = 70
    current_x = start_x
    current_y = start_y
    rows = 5
    columns = 11
    global exiting
    exiting = False
    image = ImageGrab.grab()
    
    sleep(0.5)
    
    for row in range(0,rows):
        if exiting:
            break
        current_y = start_y - (row * square_size)
        for column in range(0,columns):
            if exiting:
                break
            current_x = start_x - (column * square_size)
            coordinate = (current_x, current_y)
            pixel = image.getpixel(coordinate)
            if pixel[0] < 15 and pixel[1] < 15 and pixel[2] < 15:
                continue
            move_mouse(current_x, current_y)
            sleep(0.1)
            keyboard.press(Key.ctrl_l.value)
            sleep(0.1)
            ctrl_left_mouse_click()
            sleep(0.1)
            keyboard.release(Key.ctrl_l.value)
            

last_flask_time_s = 0
def DoFlasks():
    if not do_flasks:
        return
    global last_flask_time_s
    current_time_s = epoch_time = int(time.time())
    time_since_last = current_time_s - last_flask_time_s
    time_between_presses = 2
    print('too soon {}?'.format(time_since_last) )
    if time_since_last < time_between_presses:
        print('too soon !~!!!'.format(time_since_last) )
        return
    last_flask_time_s = current_time_s

    image = ImageGrab.grab()
    
    mana_coordinate = (3275, 1350)
    mana_pixel = image.getpixel(mana_coordinate)
    # if not blue, need mana
    print('mna {}'.format(mana_pixel))
    if mana_pixel[0] != 12 or mana_pixel[1] != 69 or mana_pixel[2] != 144:
        keyboard.press('5')
        keyboard.release('5')
        sleep(0.2)
    else:
        keyboard.press('3')
        keyboard.release('3')
        
    life_coordinate = (160, 1225)
    life_pixel = image.getpixel(life_coordinate)
    print('life_pixel {}'.format(life_pixel))
    need_life = False
    # if not blue, need mana
    if life_pixel[0] != 168 or life_pixel[1] != 46 or life_pixel[2] != 53:
        need_life = True
        keyboard.press('1')
        keyboard.release('1')
        
    '''
    haste_coordinate = (2895, 1395)
    haste_pixel = image.getpixel(haste_coordinate)
    expected_haste = (145, 163, 52)
    if haste_pixel == expected_haste:
        keyboard.press('w')
        keyboard.release('w')
        sleep(0.1)
        
    immortal_coordinate = (2895, 1395)
    immortal_pixel = image.getpixel(immortal_coordinate)
    expected_immortal = (88, 111, 64)
    if expected_immortal == immortal_pixel:
        keyboard.press('r')
        keyboard.release('r')
        sleep(0.1)
    '''
    return
        
    
    
    
while True:
    if item_coordinate and pick_up_item:
        move_mouse(item_coordinate[0], item_coordinate[1])
        left_mouse_click()
        item_coordinate = None
    if put_loot_away:
        PutLootAway()
        put_loot_away = False
    DoFlasks()
    sleep(0.5)