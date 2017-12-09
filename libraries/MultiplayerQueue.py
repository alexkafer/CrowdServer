from collections import deque

class MultiplayerQueue():
    def __init__(self, update_callback):
        self.line = deque()
        self.in_game = []
        self.update_callback = update_callback
        
    def add_player(self, player):
        if player not in self.line:
            self.line.append(player)
            print "Added player: ", player['id']
        else:
            print "Player", player['id'],  "already on list"


    def map_line_players(self, fn):
        for player in self.line:
            fn(player)

    def map_game_players(self, fn):
        for player in self.in_game:
            fn(player)

    def set_game_size(self, size):
        self.in_game = [None]*size
        print "set size", size

    def start_player(self, number, notifyCb, game):
        """ Returns the ID of the new player"""
        try:
            player = self.line.popleft() 
            print "Starting ", player['id']
            notifyCb(player['id'], "mode_change", {"mode": game})

            self.in_game[number] = player
            self.update_callback()
            return player
        except IndexError:
            return None

    def fill_players(self, notifyCb, game):
        for idx, val in enumerate(self.in_game):
            if val is None:
                print "Filling a player ", idx
                self.start_player(idx, notifyCb, game)

    def remove_player(self, clientID, notifyCb=None):
        print "Kicking player", clientID
        self.update_callback()
        if notifyCb is not None:
            notifyCb(clientID, "mode_change", {"mode": "line"})
        try:
            client = int(clientID)
        except ValueError:
            return False

        for player in self.line:
            try:
                if player['id'] == client:
                    print "Removing player in line"
                    self.line.remove(player)
                    return True
            except:
                return False
        for idx, val in enumerate(self.in_game):
            try:
                if val['id'] == client:
                    print "Kicking current player ", idx
                    self.in_game[idx] = None
                    return True
            except:
                return False
        return False

    def clear_players(self):
        for player in self.in_game:
            player = None