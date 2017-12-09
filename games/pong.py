from libraries.PixelManager import PixelManager, Color
import random

NET_LIGHT_WIDTH = 12 # Number of columns
NET_LIGHT_HEIGHT = 5 # Number of rows

#row[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
row0 = [
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1], # pixel00
    [1, 0, 1, 1, 0, 1, 1, 1, 1, 1], # pixel01
    [1, 1, 1, 1, 0, 1, 1, 1, 1, 1], # pixel02
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1]] # pixel03

#row, col [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
row1 =[
    [1, 0, 0, 0, 1, 1, 1, 0, 1, 1], #pixel10
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #pixel11
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0], #pixel12
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 1]] #pixel13

#row, col [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
row2 = [
    [1, 0, 1, 0, 1, 1, 1, 0, 1, 1], #pixel20 = 
    [0, 0, 1, 1, 1, 1, 1, 0, 1, 1], #pixel21 = 
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1], #pixel22 = 
    [1, 0, 1, 1, 1, 1, 1, 0, 1, 1]] #pixel23 = 

#row, col [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
row3 =[
    [1, 0, 1, 0, 0, 0, 1, 0, 1, 0], # pixel30 = 
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0], # pixel31 = 
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0], # pixel32 = 
    [1, 0, 0, 1, 1, 1, 1, 0, 1, 1]] # pixel33 = 

#row, col [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
row4 =[
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 0], #pixel40 = 
    [1, 0, 1, 1, 0, 1, 1, 1, 1, 0], #pixel41 = 
    [1, 1, 1, 1, 0, 1, 1, 0, 1, 0], #pixel42 = 
    [1, 0, 1, 1, 1, 1, 1, 0, 1, 1]] #pixel43 = 

numbers = [row0, row1, row2, row3, row4]

class PongGame:
    def __init__(self, pixel_manager):
        self.pixel_manager = pixel_manager
        self.pixel_manager.set_current_mode("pong")
        self.ball_location_row = 1
        self.ball_location_col = NET_LIGHT_WIDTH/2 - 1
        self.velocity_horizontal = 1
        self.velocity_verticle = 0
        self.left_pos = 2
        self.right_pos = 0
        self.left_score = 0
        self.right_score = 0

        self.title_card_remaining = 5

        self.pixel_manager.custom_receiver = self.controls_update

        self.finished = False

        self.pixel_manager.set_game_size(2)
    
    def controls_update(self, client, update):
        if self.pixel_manager.multiplayer.in_game[0] == client:
            print 'found player one!' 
            if update['button'] == 0:
                self.left_pos += 1
                if self.left_pos > 3:
                    self.left_pos = 3
            if update['button'] == 1:
                self.left_pos -= 1
                if self.left_pos < 0:
                    self.left_pos = 0

        if self.pixel_manager.multiplayer.in_game[1] == client:
            print 'found player two!' 
            if update['button'] == 0:
                self.right_pos += 1
                if self.right_pos > 3:
                    self.right_pos = 3
            if update['button'] == 1:
                self.right_pos -= 1
                if self.right_pos < 0:
                    self.right_pos = 0

    def update(self):
        if self.title_card_remaining > 0:
            self.title_card_remaining -= 1
            if self.title_card_remaining == 1:
                self.pixel_manager.clear()
            return

        self.ball_location_col += self.velocity_horizontal
        self.ball_location_row += self.velocity_verticle

        if self.ball_location_row < 0: # If I hit the top
            self.ball_location_row = 1 # Act like I bounced
            self.velocity_verticle = 1 # And change my direction

        if self.ball_location_row >= NET_LIGHT_HEIGHT: # If I hit the top
            self.ball_location_row = NET_LIGHT_HEIGHT-2 # Act like I bounced
            self.velocity_verticle = -1 # And change my direction
        
        if self.ball_location_col == 0 and (self.ball_location_row == self.left_pos or self.ball_location_row == self.left_pos + 1):
            # Left Blocked! Bouce!
            self.ball_location_col = 1
            self.velocity_horizontal = 1 # And change my direction
            self.velocity_verticle = random.randint(-1, 1)
    
        if self.ball_location_col == 11 and (self.ball_location_row == self.right_pos or self.ball_location_row == self.right_pos + 1):
            # Left Blocked! Bouce!
            self.ball_location_col = 10
            self.velocity_horizontal = -1 # And change my direction
            self.velocity_verticle = random.randint(-1, 1)

        if self.ball_location_col < 0:
            # Right scored
            self.score_right()
        elif self.ball_location_col > NET_LIGHT_WIDTH:
            # Left scored
            self.score_left()
        else:
            self.draw_frame()
        
    def draw_frame(self):
        # First draw the lowest priority. AKA cleaning:
        self.pixel_manager.clear()

        # Draw the ball and clear where it was
        self.pixel_manager.set_color(self.ball_location_row, self.ball_location_col, Color.RED)
                                  
        # Draw the correct slider    
        self.pixel_manager.set_color(self.left_pos, 0, Color.GREEN)
        self.pixel_manager.set_color(self.left_pos+1, 0, Color.GREEN)

        # Draw the correct slider
        self.pixel_manager.set_color(self.right_pos, 11, Color.GREEN)
        self.pixel_manager.set_color(self.right_pos+1, 11, Color.GREEN)
        

    def score_left(self):
        print "Left Scores! ", self.left_score, " + 1!"
        self.left_score += 1

        if self.left_score > 9:
            # left win
            self.show_left_win()
        else:
            self.show_score()

        self.pixel_manager.multiplayer.remove_current_player(2)

    def score_right(self):
        print "Right Scores! ", self.right_score, " + 1!"
        self.right_score += 1

        if self.right_score > 9:
            # left win
            self.show_right_win()
        else:
            self.show_score()

        self.pixel_manager.multiplayer.remove_current_player(1)

    def show_right_win(self):
        print "Right Wins! "
        pixels = [[Color.OFF for x in range(NET_LIGHT_WIDTH)] for y in range(NET_LIGHT_HEIGHT)]
        # right win

        #   |0 |1 |2 |3 |4 |5 |6 |7 |8 |9 |10|11|
        # 0 |# |  |  |  |  |  |  | #|  |  |  | #|
        # 1 |# |  |  |  |  |  |  | #|  |  |  | #|
        # 2 |# |  |  |  |  |  |  | #|  |  |  | #|
        # 3 |# |  |  |  |  |  |  | #|  | #|  | #|
        # 4 |# |# |# |# |  |  |  |  | #|  | #|  |

        # L
        pixels[0][0] = Color.RED
        pixels[1][0] = Color.RED
        pixels[2][0] = Color.RED
        pixels[3][0] = Color.RED
        pixels[4][0] = Color.RED
        pixels[4][1] = Color.RED
        pixels[4][2] = Color.RED
        pixels[4][3] = Color.RED


        # W
        pixels[0][7] = Color.GREEN
        pixels[0][11] = Color.GREEN
        pixels[1][7] = Color.GREEN
        pixels[1][11] = Color.GREEN
        pixels[2][7] = Color.GREEN
        pixels[2][11] = Color.GREEN
        pixels[3][7] = Color.GREEN
        pixels[3][9] = Color.GREEN
        pixels[3][11] = Color.GREEN
        pixels[4][8] = Color.GREEN
        pixels[4][10] = Color.GREEN

        self.pixel_manager.set_frame(pixels)

        self.finished = True

    def show_left_win(self):
        print "Left Wins! "
        # left win
        pixels = [[Color.OFF for x in range(NET_LIGHT_WIDTH)] for y in range(NET_LIGHT_HEIGHT)]

        #   |0 |1 |2 |3 |4 |5 |6 |7 |8 |9 |10|11|
        # 0 | #|  |  |  | #|  |  |  |# |  |  |  |
        # 1 | #|  |  |  | #|  |  |  |# |  |  |  |
        # 2 | #|  |  |  | #|  |  |  |# |  |  |  |
        # 3 | #|  | #|  | #|  |  |  |# |  |  |  |
        # 4 |  | #|  | #|  |  |  |  |# |# |# |# |

        # L
        pixels[0][8] = Color.RED
        pixels[1][8] = Color.RED
        pixels[2][8] = Color.RED
        pixels[3][8] = Color.RED
        pixels[4][8] = Color.RED
        pixels[4][9] = Color.RED
        pixels[4][10] = Color.RED
        pixels[4][11] = Color.RED


        # W
        pixels[0][0] = Color.GREEN
        pixels[0][4] = Color.GREEN
        pixels[1][0] = Color.GREEN
        pixels[1][4] = Color.GREEN
        pixels[2][0] = Color.GREEN
        pixels[2][4] = Color.GREEN
        pixels[3][0] = Color.GREEN
        pixels[3][2] = Color.GREEN
        pixels[3][4] = Color.GREEN
        pixels[4][1] = Color.GREEN
        pixels[4][3] = Color.GREEN

        self.pixel_manager.set_frame(pixels)
        self.title_card_remaining = 5
        self.finished = True

    def show_score(self):
        print "Showing score! ", self.left_score, " ", self.right_score
        pixels = [[Color.OFF for x in range(NET_LIGHT_WIDTH)] for y in range(NET_LIGHT_HEIGHT)]

        # Middle bar
        pixels[2][5] = Color.GREEN if self.left_score == self.right_score else Color.RED
        pixels[2][6] = Color.GREEN if self.left_score == self.right_score else Color.RED

        leftcolor = Color.GREEN if self.left_score >= self.right_score else Color.RED
        rightcolor = Color.GREEN if self.right_score >= self.left_score else Color.RED

        # Left Number
        for row in range(5):
            for col in range(4):
                if numbers[row][col][self.left_score] == 1:
                    pixels[row][col] = leftcolor

        for row in range(5):
            for col in range(4):
                if numbers[row][col][self.right_score] == 1:
                    pixels[row][col+8] = rightcolor

        self.pixel_manager.set_frame(pixels)

        # Reset the data

        self.title_card_remaining = 5

        self.ball_location_row = 1
        self.ball_location_col = NET_LIGHT_WIDTH/2 - 1
        self.velocity_horizontal = 1
        self.velocity_verticle = 0
        self.left_pos = 2
        self.right_pos = 1
