from dotenv import load_dotenv
import os
import requests
import pygame
from backend.data.logo_colors import LOGO_COLORS

load_dotenv()
MTA_API_URL = "https://wheres-my-train-at.onrender.com"
STOP_ID_1, ROUTE_ID_1 = os.getenv("DISPLAY_STOP_ID_1"), os.getenv("DISPLAY_ROUTE_ID_1")
STOP_ID_2, ROUTE_ID_2 = os.getenv("DISPLAY_STOP_ID_2"), os.getenv("DISPLAY_ROUTE_ID_2")

LED_WIDTH = 64
LED_HEIGHT = 32
SCALE = 10
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FONT_SIZE = 8
SCROLL_DELAY = 60
SCROLL_PAUSE_DURATION = 60
SCROLL_SPEED = 4

pygame.init()
screen = pygame.display.set_mode((LED_WIDTH * SCALE, LED_HEIGHT * SCALE))
pygame.display.set_caption("MTA Display")

# Fonts
font = pygame.font.Font(None, FONT_SIZE * SCALE)

def fetch_train_data(stop_id, route_id):
    try:
        response = requests.get(f'{MTA_API_URL}/{stop_id}/{route_id}')
        if (response.status_code == 200):
            return response.json()
        return 
    except Exception as e:
        print(f'Error fetching data: {e}')
        return

train_data_1 = fetch_train_data(STOP_ID_1, ROUTE_ID_1)
train_data_2 = fetch_train_data(STOP_ID_2, ROUTE_ID_2)

def draw_train_line(train_data, y, scroll_state):
    if train_data:
        route = train_data["routeId"]
        minutes = train_data["minutesAway"]
        station_name = train_data["stopName"]
        color = LOGO_COLORS.get(route, BLACK)
    else:
        route = None
        minutes = None
        station_name = "No Data"
        color = None
    scroll_offset, frame_counter, scroll_pause_counter = scroll_state

    # Train Logo
    circle_center_x = 6
    circle_center_y = y
    circle_radius = 5
    
    screen_x = circle_center_x * SCALE
    screen_y = circle_center_y * SCALE
    screen_radius = circle_radius * SCALE
    
    if route is not None:
        pygame.draw.circle(screen, color, (screen_x, screen_y), screen_radius)
        
        route_surface = font.render(route, False, WHITE)
        route_rect = route_surface.get_rect(center=(screen_x, screen_y))
        screen.blit(route_surface, route_rect)

    start_x = (circle_center_x + circle_radius + 3)
    end_x = (LED_WIDTH - 20)
    screen_x = start_x * SCALE
    available_width = (end_x - start_x) * SCALE
    station_surface = font.render(station_name, True, WHITE)
    station_width_actual = station_surface.get_width()
    if station_width_actual > available_width:
        frame_counter += 1
        if frame_counter > SCROLL_DELAY:
            if abs(scroll_offset) > station_width_actual - available_width:
                scroll_pause_counter += 1
                if scroll_pause_counter >= SCROLL_PAUSE_DURATION:
                    scroll_offset = 0
                    frame_counter = 0
                    scroll_pause_counter = 0
            else:
                scroll_offset -= SCROLL_SPEED
        station_rect = station_surface.get_rect(left=screen_x + scroll_offset, centery=screen_y)
    else:
        station_rect = station_surface.get_rect(left=screen_x, centery=screen_y)
    clip_rect = pygame.Rect(screen_x, 0, available_width, LED_HEIGHT * SCALE)
    screen.set_clip(clip_rect)
    screen.blit(station_surface, station_rect)
    screen.set_clip(None) 
    
    # Minutes
    if minutes is not None:
        minutes_text = f"{int(minutes)} Min"
    else:
        minutes_text = "N/A"
    minutes_surface = font.render(minutes_text, False, WHITE)
    text_x = (LED_WIDTH - 18) * SCALE
    text_y = circle_center_y * SCALE
    minutes_rect = minutes_surface.get_rect(x=text_x, centery=text_y)
    screen.blit(minutes_surface, minutes_rect)
    return (scroll_offset, frame_counter, scroll_pause_counter)

# for refresh data
last_fetch_time = pygame.time.get_ticks()
fetch_interval = 30000 

running = True
clock = pygame.time.Clock()

scroll_state_1 = (0,0,0) # scroll_offset, frame_counter, scroll_pause_counter
scroll_state_2 = (0,0,0)

while running:
    current_time = pygame.time.get_ticks()

    # refresh data
    if current_time - last_fetch_time >= fetch_interval:
        print("Fetching new train data...")
        train_data_1 = fetch_train_data(STOP_ID_1, ROUTE_ID_1)
        train_data_2 = fetch_train_data(STOP_ID_2, ROUTE_ID_2)
        scroll_state_1 = (0,0,0)
        scroll_state_2 = (0,0,0)
        last_fetch_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(BLACK)
    scroll_state_1 = draw_train_line(train_data_1, 8, scroll_state_1)
    scroll_state_2 = draw_train_line(train_data_2, 24, scroll_state_2)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()