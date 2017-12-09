""" Pixel Manager with Data Storage, Websocket, and HTTP Get Interface """
from enum import Enum
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json
from ConfigParser import RawConfigParser, NoSectionError, NoOptionError
import threading

from libraries.MultiplayerQueue import MultiplayerQueue
from websocket_server import WebsocketServer

NET_LIGHT_WIDTH = 12 # Number of columns
NET_LIGHT_HEIGHT = 5 # Number of rows

class Color(Enum):
    """ Three options of the Net Lights. Off, Red, and Green """
    OFF = 0
    RED = 1
    GREEN = 2
    BOTH = 3

class ColorEncoder(json.JSONEncoder):
    """ Allow color to be encoded with the JSONEncoder """
    def default(self, o): # pylint: disable=E0202
        if isinstance(o, Color):
            return o.value
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)

class PixelManager(HTTPServer):
    """ Pixel Manager with Data Storage, Websocket, and HTTP Get Interface """
    def __init__(self, websocket_port=8000, webserver_port=80):
        """ Initializes the pixels to the correct size and pre-sets everything to OFF """
        self.pixels = [[Color.OFF for x in range(NET_LIGHT_WIDTH)] for y in range(NET_LIGHT_HEIGHT)]
        self.dmx = None

        config = RawConfigParser()
        config.read('DMX.cfg')

        self.dmxmap = []
        for row in range(NET_LIGHT_HEIGHT):
            for col in range(NET_LIGHT_WIDTH):
                def read_color_config(name, row, col):
                    """ Small helper function to pull DMX channels for a name, row, and col """
                    try:
                        color = config.getint(name, str(col) + ',' + str(row))
                    except NoSectionError:
                        print name, " Netlights entries not found"
                        color = None
                    except NoOptionError:
                        print "DMX Channel for netlight ", name, row, col, " not found in config"
                        color = None

                    return color

                # Remove the first Color.OFF
                self.dmxmap.append([read_color_config(name, row, col) for name, color in Color.__members__.items()[1:]]) 

        self.ws = WebsocketServer(websocket_port, "0.0.0.0")
        self.ws.set_fn_new_client(self.new_client)
        self.ws.set_fn_client_left(self.client_left)
        self.ws.set_fn_message_received(self.receive_update)

        self.custom_receiver = None

        self.websocket_thread = threading.Thread(target=self.ws.run_forever)
        self.websocket_thread.daemon = True

        self.webserver_thread = threading.Thread(target=self.serve_forever)
        self.webserver_thread.daemon = True

        server_address = ('', webserver_port)
        HTTPServer.__init__(self, server_address, PixelServer)

        self.current_mode = "places"
        self.multiplayer = MultiplayerQueue(self)    
        
    def new_client(self, client, server):
            """ Called for every client connecting (after handshake) """
            print "New client connected and was given id %d" % client['id']
            
            payload = {
                'type': "pixel_update",
                'pixels': self.pixels
            }
            
            # Pre-populate pixel data
            client['handler'].send_message(json.dumps(payload, cls=ColorEncoder))

    # Called for every client disconnecting
    def client_left(self, client, server):
        """ Called for every client disconnecting """
        print "Client disconnected", client
        self.multiplayer.remove_player(client['id'])

    def update_positions(self):
        print "updating positions"
        position = 1
        for player in self.multiplayer.line:
            print "Found player", player
            try:
                print "Player", player['id'], "is", position
                player['handler'].send_message(json.dumps({"type": "player_position", "position": position}, cls=ColorEncoder))
                position += 1
            except Exception as e: 
                print "Cannot update position", e

    def receive_update(self, client, server, message):
        """ Receives web socket update and updates the pixel manager """
        print "Client(%d) said: %s" % (client['id'], message)
        updateMessage = json.loads(message)

        try:
            updateType = updateMessage['type']
        except KeyError:
            print "Update without type!"
            updateType = None

        updates = {
            "pixel_touch": self.pixel_touch,
            "button_press": self.custom_receiver,
            "play_intent": self.add_player_to_line
        }

        try:
            fun = updates[updateType]
            if callable(fun):
                fun(client, updateMessage)
        except KeyError:
            print "Received update called", updateType, "and I'm not sure what that is."

    def send_update(self, clientID, update_type, payload = {}):
        if self.ws:
            if not payload.has_key("type"):
                payload['type'] = update_type
            
            if clientID == -1:
                self.ws.send_message_to_all(json.dumps(payload, cls=ColorEncoder))
            else:
                for client in self.ws.clients:
                    if client['id'] == clientID:
                        client['handler'].send_message(json.dumps(payload, cls=ColorEncoder))
                        break
        
    def pixel_touch(self, client, update):
        if self.current_mode == "places":
            print self.current_mode, update
            row = int(update['row'])
            col = int(update['col'])
            color = Color(int(update['color']))
            self.set_color(row, col, color)
            self.render_update()

    # Game related things
    def set_game_size(self, size):
        self.multiplayer.set_game_size(size)

    def start_game_filling(self):
        self.multiplayer.fill_players()

    def add_player_to_line(self, client, update):
        self.multiplayer.add_player(client)

    def clear_players(self):
        self.multiplayer.clear_players()

    def set_current_mode(self, name):
        self.current_mode = name
        if name != "places":
            name = "line"
            self.multiplayer.clear_players()
        
        self.send_update(-1, "mode_change", {'mode': name})

    def clear(self):
        """ Sets an individual pixel to a given color """
        self.pixels = [[Color.OFF for x in range(NET_LIGHT_WIDTH)] for y in range(NET_LIGHT_HEIGHT)]

    def set_color(self, row, column, color):
        """ Sets an individual pixel to a given color """
        # Make sure we need to update the pixel
        if row < 0 or row >= NET_LIGHT_HEIGHT: # Out of range 
            return
        if column < 0 or column >= NET_LIGHT_WIDTH: # Out of range 
            return
        if self.pixels[row][column] == color: # Not changing
            return

        self.pixels[row][column] = color
        

    def render_update(self):
        if self.dmx is not None:
            self.dmx.sendDMX(self.convert_to_dmx_array())

        self.send_update(-1, "pixel_update", {'pixels': self.pixels})

    def set_frame(self, new_pixels):
        """ Sets an individual pixel to a given color """
        for row in range(NET_LIGHT_HEIGHT):
            for col in range(NET_LIGHT_WIDTH):
                 self.set_color(row, col, new_pixels[row][col])

    def get_pixels(self):
        """ Sets an individual pixel to a given color """
        return self.pixels

    def convert_to_dmx_array(self):
        """ Converts the matrix to a single 1D array. """
        output = [255] * 512
        flattened = (self.pixels[4] + self.pixels[3] + self.pixels[2] + self.pixels[1] + self.pixels[0])
        index = 0
        for pixel in flattened:
            print index, pixel, self.dmxmap[index]
            if pixel == Color.RED:
                output[self.dmxmap[index][0]-1] = 255
                output[self.dmxmap[index][1]-1] = 0
            elif pixel == Color.GREEN:
                output[self.dmxmap[index][0]-1] = 0
                output[self.dmxmap[index][1]-1] = 255
            elif pixel == Color.BOTH:
                output[self.dmxmap[index][1]-1] = 255
                output[self.dmxmap[index][0]-1] = 255
            else:
                output[self.dmxmap[index][0]-1] = 0
                output[self.dmxmap[index][1]-1] = 0
 
            index += 1
             
        return output
        # Initializes all lights to full brightness, the first None being an offset
        # The offset is removed at end since DMX is 1 based (not 0)

    def link_dmx(self, dmx):
        """ Links the DMX instance to the Pixel Manager  """
        self.dmx = dmx

    def start_websocket(self):
        """ Starts the web socket """
        print 'Starting web socket...'
        self.websocket_thread.start()

    def start_webserver(self):
        """ Starts the web server """
        print 'Starting httpd...'
        self.webserver_thread.start()

def extractID(client):
    try:
        return client['id']
    except:
        None

class PixelServer(BaseHTTPRequestHandler):
    """ A HTTP server that responds back with a JSON array of the current pixels """
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self): # pylint: disable=C0103
        """ responds to a GET and produces the JSON array """
        self._set_headers()

        print"Path!", self.path

        payload = None

        if self.path == "/players":
            payload = {
                "players": map(extractID, list(self.server.multiplayer.line)),
                "in_game": map(extractID, self.server.multiplayer.in_game)
            }

    
        if self.path == "/" or self.path == "":
            mode = self.server.current_mode
            if mode != "places":
                mode = "line"
            payload = {
                "pixels": self.server.get_pixels(),
                "mode": mode
            }

        if payload is None:
            payload = {}
        self.wfile.write(json.dumps(payload, cls=ColorEncoder))

    def do_POST(self): # pylint: disable=C0103
        """ responds to a GET and produces the JSON array """
        payload = {
             "message": "Success"
        }
        self._set_headers()
        try:
            split = self.path.split("/")
            if split[1] == "kick":
                idToKick = split[2]
                self.server.multiplayer.remove_player(idToKick, self.server.send_update)
        except Exception as e:
            print "Invalid POST: ", self.path, e
            payload = {
                "message": "Failed"
            }

        self.wfile.write(json.dumps(payload))

    def do_HEAD(self): # pylint: disable=C0103
        """ Sets the Access-Control-Allow-Origin to anyone  """
        self._set_headers()
