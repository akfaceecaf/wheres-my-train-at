from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from dotenv import load_dotenv
import time
import os
import sys
import requests
from data.logo_colors import LOGO_COLORS

load_dotenv()

MTA_API_URL = os.getenv("MTA_API_URL")
STOP_ID_1, ROUTE_ID_1 = os.getenv("DISPLAY_STOP_ID_1"), os.getenv("DISPLAY_ROUTE_ID_1")
STOP_ID_2, ROUTE_ID_2 = os.getenv("DISPLAY_STOP_ID_2"), os.getenv("DISPLAY_ROUTE_ID_2")

LED_WIDTH = 64
LED_HEIGHT = 32

options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.hardware_mapping = 'adafruit-hat'
options.gpio_slowdown = 4
options.brightness = 100
matrix = RGBMatrix(options=options)

font = graphics.Font()
font.LoadFont("/usr/local/share/fonts/led-matrix/5x8.bdf")

BLACK = graphics.Color(0, 0, 0)
LIGHT_GRAY = graphics.Color(200, 200, 200)
WHITE = graphics.Color(255, 255, 255)

def fetch_train_data(stop_id, route_id):
    try:
        response = requests.get(f'{MTA_API_URL}/mta/{stop_id}/{route_id}')
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f'Error fetching data: {e}')
        return None

SCROLL_START_DELAY = 60
SCROLL_END_PAUSE = 60
SCROLL_SPEED = 0.8

scroll_state_1 = {"delay_counter": 0, "pos": 0, "pause_counter": 0}
scroll_state_2= {"delay_counter": 0, "pos": 0, "pause_counter": 0}

def draw_train_line(canvas, train_data, center_y, scroll_state):
    if train_data and train_data.get("minutesAway") is not None:
        train = {
            "route": f'{train_data["routeId"]}',
            "stop_name": f'{train_data["stopName"]}',
            "minutes": f'{train_data["minutesAway"]}m',
        }
    else:
        train = {
            "route": '?',
            "stop_name": 'No Data',
            "minutes": 'na',
        }

    ROUTE_COLOR = graphics.Color(*LOGO_COLORS.get(train["route"],(255,255,255)))

    # route sign
    circle_radius = 4
    circle_center_x = 5
    circle_center_y = center_y
    graphics.DrawCircle(canvas, circle_center_x, circle_center_y, circle_radius, ROUTE_COLOR)

    # minutes away
    char_length = 5
    minutes_length = len(train["minutes"]) * char_length
    minutes_x = LED_WIDTH - minutes_length - 2
    minutes_y = center_y + 3
    graphics.DrawText(canvas, font, minutes_x, minutes_y, WHITE, train["minutes"])

    # station
    station_start_x = circle_center_x + circle_radius + 3
    station_end_x = LED_WIDTH - minutes_length - 3
    station_y = center_y + 3
    available_width = station_end_x - station_start_x
    text_width = len(train["stop_name"]) * char_length

    if text_width > available_width:
        scroll_state["delay_counter"] += 1
        if scroll_state["delay_counter"] > SCROLL_START_DELAY:
            max_scroll = text_width - available_width
            if scroll_state["pos"] < max_scroll:
                scroll_state["pos"] += SCROLL_SPEED
            else:
                scroll_state["pause_counter"] += 1
                if scroll_state["pause_counter"] > SCROLL_END_PAUSE:
                    scroll_state["delay_counter"] = 0
                    scroll_state["pos"] = 0
                    scroll_state["pause_counter"] = 0
        text_x = station_start_x - scroll_state["pos"]
    else:
        text_x = station_start_x
        scroll_state["pos"] = 0
    
    for i, char in enumerate(train['stop_name']):
        char_x = text_x + (i * char_length)
        if station_start_x <= char_x and char_x + char_length <= station_end_x:
            graphics.DrawText(canvas, font, char_x, station_y, WHITE, char)
    
train_data_1 = fetch_train_data(STOP_ID_1, ROUTE_ID_1)
train_data_2 = fetch_train_data(STOP_ID_2, ROUTE_ID_2)

offset_canvas = matrix.CreateFrameCanvas()
last_fetch_time = time.time()
fetch_interval = 30

try: 
    while True:
        current_time = time.time()
        if current_time - last_fetch_time >= fetch_interval:
            train_data_1 = fetch_train_data(STOP_ID_1, ROUTE_ID_1)
            train_data_2 = fetch_train_data(STOP_ID_2, ROUTE_ID_2)
            scroll_state_1 = {'pos': 0, 'delay_counter': 0, "pause_counter": 0}
            scroll_state_2 = {'pos': 0, 'delay_counter': 0, "pause_counter": 0}
            last_fetch_time = current_time
        offset_canvas.Clear()
        draw_train_line(offset_canvas, train_data_1, 8, scroll_state_1)
        draw_train_line(offset_canvas, train_data_2, 24, scroll_state_2)
        offset_canvas = matrix.SwapOnVSync(offset_canvas)
        time.sleep(0.03)
except KeyboardInterrupt:
    sys.exit(0)

