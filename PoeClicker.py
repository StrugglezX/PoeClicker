

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
            

class TimedSkill:
    def __init__(self, keychar, interval, debug=False):
        self._keychar = keychar
        self._interval = interval
        self._last_pressed_time = 0
        self._debug = debug
        
    def PressIfElapsed(self, current_time):
        elapsed_time = current_time - self._last_pressed_time
        if self._debug:
            print('elapsed_time {} = current_time {} - self._last_pressed_time {}'.format(elapsed_time, current_time, self._last_pressed_time))
        if elapsed_time > self._interval:
            self._last_pressed_time = current_time
            keyboard.press( self._keychar )
            keyboard.release( self._keychar )
            sleep(0.1)
            
class PixelSkill:
    def __init__(self, keychar, coordinate, expected_pixel_color, delta=5, debug=False):
        self._keychar = keychar
        self._coordinate = coordinate
        self._expected_pixel_color = expected_pixel_color
        self._delta = delta
        self._debug = debug
        
    def PressIfReady(self, image):
        actual_pixel = image.getpixel(self._coordinate)
        r_diff = abs(self._expected_pixel_color[0] - actual_pixel[0])
        g_diff = abs(self._expected_pixel_color[1] - actual_pixel[1])
        b_diff = abs(self._expected_pixel_color[2] - actual_pixel[2])
        
        if self._debug:
            print('\n')
            print('_keychar {}'.format(self._keychar))
            print('_delta {}'.format(self._delta))
            print('actual_pixel {}'.format(actual_pixel))
            print('_expected_pixel_color {}'.format(self._expected_pixel_color))
            
        if r_diff < self._delta and g_diff < self._delta and b_diff < self._delta:
            keyboard.press( self._keychar )
            keyboard.release( self._keychar )
            sleep(0.1)
               
class TimedMissingPixelSkill:
    def __init__(self, keychar, interval, coordinate, expected_pixel_color, delta=5, debug=False):
        self._keychar = keychar
        self._interval = interval
        self._last_pressed_time = 0
        self._coordinate = coordinate
        self._expected_pixel_color = expected_pixel_color
        self._delta = delta
        self._debug = debug
        
    def PressIfReady(self, current_time, image):
        elapsed_time = current_time - self._last_pressed_time
        actual_pixel = image.getpixel(self._coordinate)
        r_diff = abs(self._expected_pixel_color[0] - actual_pixel[0])
        g_diff = abs(self._expected_pixel_color[1] - actual_pixel[1])
        b_diff = abs(self._expected_pixel_color[2] - actual_pixel[2])
        
        if self._debug:
            print('\n')
            print('_keychar {}'.format(self._keychar))
            print('_delta {}'.format(self._delta))
            print('actual_pixel {}'.format(actual_pixel))
            print('_expected_pixel_color {}'.format(self._expected_pixel_color))
            print('elapsed_time {} = current_time {} - self._last_pressed_time {}'.format(elapsed_time, current_time, self._last_pressed_time))
            
        if elapsed_time > self._interval and (r_diff > self._delta or g_diff > self._delta or b_diff > self._delta ):
            self._last_pressed_time = current_time
            keyboard.press( self._keychar )
            keyboard.release( self._keychar )
            sleep(0.1)
            
            
onslaught_skill = TimedSkill('2', 5.0)
movement_skill = TimedSkill('3', 5.0)
hybrid_skill = TimedSkill('4', 3.5)
mana_skill = TimedSkill('5', 5.0)

haste_coordinate = (2895, 1395)
expected_haste = (145, 163, 52)
haste_skill = PixelSkill('w', haste_coordinate, expected_haste)

phase_skill = TimedSkill('e', 3.0)
immortal_skill = TimedSkill('r', 3.0)

life_coordinate = (160, 1225)
expected_life = (168, 46, 53)
life_skill = TimedMissingPixelSkill('1', 4.0, life_coordinate, expected_life)
            
last_flask_time_s = 0
def DoFlasks():
    if not do_flasks:
        return
    global last_flask_time_s
    current_time_s = epoch_time = int(time.time())

    image = ImageGrab.grab()
    
    onslaught_skill.PressIfElapsed(current_time_s)
    movement_skill.PressIfElapsed(current_time_s)
    hybrid_skill.PressIfElapsed(current_time_s)
    mana_skill.PressIfElapsed(current_time_s)
    phase_skill.PressIfElapsed(current_time_s)
    immortal_skill.PressIfElapsed(current_time_s)
    
    haste_skill.PressIfReady(image)
    
    life_skill.PressIfReady(current_time_s, image)
        
    
while True:
    if item_coordinate and pick_up_item:
        move_mouse(item_coordinate[0], item_coordinate[1])
        left_mouse_click()
        item_coordinate = None
    if put_loot_away:
        PutLootAway()
        put_loot_away = False
    DoFlasks()
    sleep(0.1)