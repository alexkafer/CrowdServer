#!/usr/bin/python
"""This is the super fun main file to run the whole thing. Be nice."""

import platform
import sys
import time
import threading

import libraries

from libraries.PixelManager import PixelManager, Color
from serial.serialutil import SerialException
from libraries.EnttecUsbDmxPro import EnttecUsbDmxPro

from games.pong import PongGame

print "Welcome to the Crowd Interaction software. We put the cool in cool beans."
PIXELS = PixelManager()
DMX = EnttecUsbDmxPro()

DPORT = None
if len(sys.argv) < 2:
    if platform.system() == 'Linux':
        DPORT = '/dev/ttyUSB0'
    elif platform.system() == 'Darwin':
        DPORT = '/dev/tty.usbserial-EN215593'
        # Erwin: tty.usbserial-EN215593
        # Timmy: tty.usbserial-EN17533
else:
    DPORT = sys.argv[1]

if DPORT is None:
    DMX.list()
    sys.stderr.write("ERROR: No serial port for DMX detected!\n")
    sys.exit()

DMX.setPort(DPORT)

try:
    DMX.connect()
    PIXELS.link_dmx(DMX)
except SerialException:
    print "Unable to connect to USB to DMX converter. Is Timmy (Erwin) alive? Proceeding without DMX"

PIXELS.start_websocket()
PIXELS.start_webserver()

def test_command():
    PIXELS.set_current_mode("testing")
    try: 
        while True:
            color = Color.RED
            for x in range(5):
                for y in range(12):
                    PIXELS.set_color(x, y, color)
                    time.sleep(1)
                    PIXELS.render_update()

            color = Color.OFF
            for x in range(5):
                for y in range(12):
                    PIXELS.set_color(x, y, color)
                    time.sleep(1)
                    PIXELS.render_update()

            color = Color.GREEN
            for x in range(5):
                for y in range(12):
                    PIXELS.set_color(x, y, color)
                    time.sleep(1)
                    PIXELS.render_update()

    except KeyboardInterrupt:
        print('interrupted!')

def green():
    pixels = [[Color.GREEN for x in range(12)] for y in range(5)]
    PIXELS.set_frame(pixels)
    PIXELS.render_update()

def red():
    pixels = [[Color.RED for x in range(12)] for y in range(5)]
    PIXELS.set_frame(pixels)
    PIXELS.render_update()

def allOn():
    pixels = [[Color.BOTH for x in range(12)] for y in range(5)]
    PIXELS.set_frame(pixels)
    PIXELS.render_update()

def clear():
    pixels = [[Color.OFF for x in range(12)] for y in range(5)]
    PIXELS.set_frame(pixels)
    PIXELS.render_update()

def numbers():
    game = PongGame(PIXELS)
    for x in range(10):
        game.left_score = x
        game.show_score()
        PIXELS.render_update()
        time.sleep(3)

def clients():
    print PIXELS.ws.clients

def stop_command():
    if DMX is not None:
        DMX.disconnect

def multiplayer_test():
    PIXELS.set_game_size(2)
    while True:
        PIXELS.start_game_filling()
        time.sleep(5)
        # PIXELS.clear_players()

def pong_command():
    try:
        while True:
            game = PongGame(PIXELS)
            game.show_score()

            while not game.finished:
                PIXELS.start_game_filling()
                time.sleep(0.25)
                game.update()
                PIXELS.render_update()

            PIXELS.clear_players()
    except KeyboardInterrupt:
        print('interrupted!')



COMMANDS = {
    "stop" : stop_command,
    "test" : test_command,
    "pong" : pong_command,
    "green" : green,
    "red" : red,
    "all": allOn,
    "clear" : clear,
    "multiplayer": multiplayer_test
}

command = None
while command != "stop":
    PIXELS.set_current_mode("places")
    command = raw_input("Enter a command: ")
    to_run = COMMANDS.get(command, None)
    if to_run is not None:
        to_run()