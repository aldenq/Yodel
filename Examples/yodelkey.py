import yodel
import time


import pygame
import sys
import pygame.locals

pygame.init()
BLACK = (0, 0, 0)
WIDTH = 100
HEIGHT = 100
windowSurface = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)

windowSurface.fill(BLACK)


# 11111111111111111111111111
# print(dir(keyboard))
yodel.setName("sender")
yodel.addGroup("group_of_robots")
yodel.setPower(3200)
yodel.setRepeats(10)
yodel.startRadio("wlx00c0caa5efb2")
yodel.setChannel(3)


key_standard = [
    yodel.field("key_code", int, 255),
    yodel.field("key_info", yodel.flags)
]

key_format = yodel.format(key_standard)
key_data = yodel.section(key_format)

font = pygame.font.Font(pygame.font.get_default_font(), 36)
key_data.key_info = yodel.flags(["isUppercase", "isPressed", "clearAll"])
caps_lock = False

keys_pressed = [] * 255


prev_code = 0
prev_state = 0
st = time.time()


while True:
    # print("a")
    # print(time.time()-st)
    for event in pygame.event.get():

        if event.type == pygame.KEYDOWN:
            # print(event.scancode)
            key_code = event.scancode
            state = True

        if event.type == pygame.KEYUP:
            # print(event.scancode)
            key_code = event.scancode
            state = False

        if event.type == pygame.locals.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            text_surface = font.render(
                str(event.scancode), True, (255, 255, 255))
            windowSurface.fill(BLACK)
            windowSurface.blit(text_surface, dest=(30, 35))
            pygame.display.update()
            # print(event)
            #event = keys.get()
            # print(event.scancode)

            if key_code == 225 and state == True:
                caps_lock = not caps_lock
            key_data.key_code = key_code
            key_data.key_info["isUppercase"] = caps_lock
            key_data.key_info["isPressed"] = state

            if key_code != prev_code or state != prev_state:
                yodel.send(
                    bytes(key_data),
                    name="listener",
                    group="group_of_robots")
            #print(caps_lock,key_code ,state)
            # key_data.print()

            prev_code = key_code
            prev_state = state
