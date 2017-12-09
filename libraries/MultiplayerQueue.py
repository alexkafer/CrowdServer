from collections import deque

class MultiplayerQueue():
    def __init__(self, pixel):
        self.line = deque()
        self.in_game = []
        self.pixelManager = pixel
        
    def add_player(self, player):
        if player not in self.line:
            self.line.append(player)
            print "Added player: ", player['id']
            self.pixelManager.update_positions()
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

    def start_player(self, number):
        """ Returns the ID of the new player"""
        try:
            player = self.line.popleft() 
            print "Starting ", player['id']

            self.pixelManager.send_update(player['id'],  "mode_change", {"mode": self.pixelManager.current_mode})

            self.in_game[number] = player
            self.pixelManager.update_positions()
            return player
        except IndexError:
            return None

    def fill_players(self):
        for idx, val in enumerate(self.in_game):
            if val is None:
                print "Filling a player ", idx
                self.start_player(idx)

    def remove_player(self, clientID):
        print "Kicking player", clientID

        self.pixelManager.send_update(clientID,  "mode_change", {"mode": "line"})

        try:
            client = int(clientID)
        except ValueError:
            return False

        # for player in self.line:
        #     try:
        #         if player['id'] == client:
        #             print "Removing player in line"
        #             self.line.remove(player)
        #             return True
        #     except:
        #         return False
        for idx, val in enumerate(self.in_game):
            try:
                if val['id'] == client:
                    print "Kicking current player ", idx
                    self.add_player(self.in_game[idx])
                    self.in_game[idx] = None
                    return True
            except:
                return False
        return False

    def remove_current_player(self, number):
        try:
            self.pixelManager.send_update(self.in_game[number-1]['id'],  "mode_change", {"mode": "line"})
            self.in_game[number-1] = None
            self.pixelManager.update_positions()
        except Exception as e:
            print "Removing player error", e

    def clear_players(self):
        for index, player in enumerate(self.in_game):
            if player is not None:
                self.pixelManager.send_update(player['id'],  "mode_change", {"mode": "line"})
                self.add_player(player)
                self.in_game[index] = None
                self.pixelManager.update_positions()