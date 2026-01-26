from dotenv import load_dotenv
import os
import requests
import pygame
from data.logo_colors import LOGO_COLORS

load_dotenv()
STOP_ID_1, ROUTE_ID_1 = os.getenv("DISPLAY_STOP_ID_1"), os.getenv("DISPLAY_ROUTE_ID_1")
STOP_ID_2, ROUTE_ID_2 = os.getenv("DISPLAY_STOP_ID_2"), os.getenv("DISPLAY_ROUTE_ID_2")


LED_WIDTH = 64
LED_HEIGHT = 32
SCALE = 10
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FONT_SIZE = 8

pygame.init()
screen = pygame.display.set_mode((LED_WIDTH * SCALE, LED_HEIGHT * SCALE))
pygame.display.set_caption("MTA Display")

# Fonts
font = pygame.font.Font(None, FONT_SIZE * SCALE)

def fetch_train_data(stop_id, route_id):
    try:
        response = requests.get(f'http://localhost:3001/mta/{stop_id}/{route_id}')
        if (response.status_code == 200):
            return response.json()
        return 
    except Exception as e:
        print(f'Error fetching data: {e}')
        return

train_data_1 = fetch_train_data(STOP_ID_1, ROUTE_ID_1)
train_data_2 = fetch_train_data(STOP_ID_2, ROUTE_ID_2)

# for refresh data
last_fetch_time = pygame.time.get_ticks()
fetch_interval = 30000 

running = True
clock = pygame.time.Clock()

scroll_offset = 0
scroll_speed = 4
scroll_delay = 60  
frame_counter = 0
scroll_pause_counter = 0
scroll_pause_duration = 60 

scroll_offset_2 = 0
scroll_speed_2 = 4
scroll_delay_2 = 60  
frame_counter_2 = 0
scroll_pause_counter_2 = 0
scroll_pause_duration_2 = 60 

while running:
    current_time = pygame.time.get_ticks()
    # refresh data
    if current_time - last_fetch_time >= fetch_interval:
        print("Fetching new train data...")
        train_data_1 = fetch_train_data(STOP_ID_1, ROUTE_ID_1)
        train_data_2 = fetch_train_data(STOP_ID_2, ROUTE_ID_2)
        scroll_offset = 0
        frame_counter = 0
        scroll_pause_counter = 0
        scroll_offset_2 = 0
        frame_counter_2 = 0
        scroll_pause_counter_2 = 0
        last_fetch_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(BLACK)
    route = train_data_1["routeId"]
    minutes = int(train_data_1["minutesAway"])
    station_name = train_data_1["stopName"]
    color = LOGO_COLORS[route]
    
    # Train Logo
    circle_center_x = 6
    circle_center_y = 8
    circle_radius = 5
    
    screen_x = circle_center_x * SCALE
    screen_y = circle_center_y * SCALE
    screen_radius = circle_radius * SCALE
    
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
        if frame_counter > scroll_delay:
            if abs(scroll_offset) > station_width_actual - available_width:
                scroll_pause_counter += 1
                if scroll_pause_counter >= scroll_pause_duration:
                    scroll_offset = 0
                    frame_counter = 0
                    scroll_pause_counter = 0
            else:
                scroll_offset -= scroll_speed
        station_rect = station_surface.get_rect(left=screen_x + scroll_offset, centery=screen_y)
    else:
        station_rect = station_surface.get_rect(left=screen_x, centery=screen_y)
    clip_rect = pygame.Rect(screen_x, 0, available_width, LED_HEIGHT * SCALE)
    screen.set_clip(clip_rect)
    screen.blit(station_surface, station_rect)
    screen.set_clip(None) 
    
    # Minutes
    minutes_text = f"{minutes} Min"
    minutes_surface = font.render(minutes_text, False, WHITE)
    text_x = (LED_WIDTH - 18) * SCALE
    text_y = circle_center_y * SCALE
    minutes_rect = minutes_surface.get_rect(x=text_x, centery=text_y)
    screen.blit(minutes_surface, minutes_rect)

    route_2 = train_data_2["routeId"]
    minutes_2 = int(train_data_2["minutesAway"])
    station_name_2 = train_data_2["stopName"]
    color_2 = LOGO_COLORS[route_2]
    
    # Train Logo
    circle_center_x_2 = 6
    circle_center_y_2 = 24
    circle_radius_2 = 5
    
    screen_x_2 = circle_center_x_2 * SCALE
    screen_y_2 = circle_center_y_2 * SCALE
    screen_radius_2 = circle_radius_2 * SCALE
    
    pygame.draw.circle(screen, color_2, (screen_x_2, screen_y_2), screen_radius_2)
    
    route_surface_2 = font.render(route_2, False, WHITE)
    route_rect_2 = route_surface_2.get_rect(center=(screen_x_2, screen_y_2))
    screen.blit(route_surface_2, route_rect_2)

    start_x_2 = (circle_center_x_2 + circle_radius_2 + 3)
    end_x_2 = (LED_WIDTH - 20)
    screen_x_2 = start_x_2 * SCALE
    available_width_2 = (end_x - start_x) * SCALE
    station_surface_2 = font.render(station_name_2, True, WHITE)
    station_width_actual_2 = station_surface_2.get_width()
    if station_width_actual_2 > available_width_2:
        frame_counter_2 += 1
        if frame_counter_2 > scroll_delay_2:
            if abs(scroll_offset_2) > station_width_actual_2 - available_width_2:
                scroll_pause_counter_2 += 1
                if scroll_pause_counter_2 >= scroll_pause_duration_2:
                    scroll_offset_2 = 0
                    frame_counter_2 = 0
                    scroll_pause_counter_2 = 0
            else:
                scroll_offset_2 -= scroll_speed_2
        station_rect_2 = station_surface_2.get_rect(left=screen_x_2 + scroll_offset_2, centery=screen_y_2)
    else:
        station_rect_2 = station_surface_2.get_rect(left=screen_x_2, centery=screen_y_2)
    clip_rect_2 = pygame.Rect(screen_x_2, 0, available_width_2, LED_HEIGHT * SCALE)
    screen.set_clip(clip_rect_2)
    screen.blit(station_surface_2, station_rect_2)
    screen.set_clip(None) 
    
    # Minutes
    minutes_text_2 = f"{minutes_2} Min"
    minutes_surface_2 = font.render(minutes_text_2, False, WHITE)
    text_x_2 = (LED_WIDTH - 18) * SCALE
    text_y_2 = circle_center_y_2 * SCALE
    minutes_rect_2 = minutes_surface_2.get_rect(x=text_x_2, centery=text_y_2)
    screen.blit(minutes_surface_2, minutes_rect_2)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()