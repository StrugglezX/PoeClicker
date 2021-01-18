

from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller
import pynput
from PIL import ImageGrab
from time import sleep
import threading

exiting = False
put_loot_away = False
pick_up_item = False
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
        try:
            print('{}'.format(key.char))
            if key.char == '/':
                put_loot_away = True
            elif key.char == '`':
                exiting = True
            elif key.char == '\\':
                pick_up_item = not pick_up_item
        except:
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
    image = ImageGrab.grab()
    
    keyboard.press(Key.ctrl_l.value)
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
            print(pixel)
            if pixel[0] < 15 and pixel[1] < 15 and pixel[2] < 15:
                continue
            move_mouse(current_x, current_y)
            sleep(0.33)
            ctrl_left_mouse_click()
            
    keyboard.release(Key.ctrl_l.value)

while True:
    if item_coordinate and pick_up_item:
        move_mouse(item_coordinate[0], item_coordinate[1])
        left_mouse_click()
        item_coordinate = None
    if put_loot_away:
        PutLootAway()
        put_loot_away = False
    sleep(0.5)