import pygame, sys, os, threading, chess, chess.engine, time, random
from pygame.locals import *
# Initializing all the global variables and variables needed to run the game
pygame.init()
pygame.mixer.init()

global turn, halfmove_count, fullmove_count, castle, en_passant_tile, en_passant, play_or_pause, player_color, previous_castle, previously_in_check, game_over_sound_heard
gamemode = 'two_player' #can also be set as 'two_player'
game_over_sound_heard = False
previously_in_check = False
previous_castle = 'KQkq'
play_or_pause = 'pause'
player_color = 'white'
original_fen_position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
test_fen_position = 'r4br1/3b1kpp/1q1P4/1pp1RP1N/p7/6Q1/PPB3PP/2KR4 w - - 1 0'
fen_position = original_fen_position
turn = fen_position.split(' ')[1]
screen_size = screen_width, screen_height = 1440, 780
tile_size = screen_width/8, screen_height/8
screen = pygame.display.set_mode(screen_size)
inverted_surface = pygame.Surface((screen_width, screen_height))
pygame.display.set_caption('Chess')
black = (25, 25, 25)
red = (255, 0, 0)
gray = (145, 145, 145)
white = (255, 255, 255)
dark_blue = (139,163,172,255)
light_blue = (221,227,231,255)
light_brown = (218, 247, 166)
dark_brown = (171,126,76)
yellow = (194,217,140,255)
clock = pygame.time.Clock()
window_rect = pygame.Rect(0, 0, screen_width, screen_height)
last_valid_pos_1d = None
castle = 'KQkq'
en_passant = '-'
en_passant_tile = None
halfmove_count = 0
fullmove_count = 1
tile = [[0,0,0] for i in range(64)] #A 2D array of size 64 where in each element in this array is a list containing the binary value of the piece and its char representation
                                    #[0,0,0] denotes an empty piece 
                                    #[piece_binary, piece_char, is_sliding_piece]

tiles_white = {
    0: 'a8', 1: 'b8', 2: 'c8', 3: 'd8', 4: 'e8', 5: 'f8', 6: 'g8', 7: 'h8',
    8: 'a7', 9: 'b7', 10: 'c7', 11: 'd7', 12: 'e7', 13: 'f7', 14: 'g7', 15: 'h7',
    16: 'a6', 17: 'b6', 18: 'c6', 19: 'd6', 20: 'e6', 21: 'f6', 22: 'g6', 23: 'h6',
    24: 'a5', 25: 'b5', 26: 'c5', 27: 'd5', 28: 'e5', 29: 'f5', 30: 'g5', 31: 'h5',
    32: 'a4', 33: 'b4', 34: 'c4', 35: 'd4', 36: 'e4', 37: 'f4', 38: 'g4', 39: 'h4',
    40: 'a3', 41: 'b3', 42: 'c3', 43: 'd3', 44: 'e3', 45: 'f3', 46: 'g3', 47: 'h3',
    48: 'a2', 49: 'b2', 50: 'c2', 51: 'd2', 52: 'e2', 53: 'f2', 54: 'g2', 55: 'h2',
    56: 'a1', 57: 'b1', 58: 'c1', 59: 'd1', 60: 'e1', 61: 'f1', 62: 'g1', 63: 'h1'
}

tiles_inverted = {v: k for k, v in tiles_white.items()}

tiles_white_keys = list(tiles_white.keys())
tiles_white_values = list(tiles_white.values())

#Uses the os library in order to get the images of the pieces
cwd = os.getcwd()
path = 'CHESS PIECES'
full_path = os.path.join(cwd, path)
full_path = full_path.replace('\\', '/')

white_king, black_king = pygame.image.load(full_path+'/white_king.png'), pygame.image.load(full_path+'/black_king.png')
white_queen, black_queen = pygame.image.load(full_path+'/white_queen.png'), pygame.image.load(full_path+'/black_queen.png')
white_rook, black_rook = pygame.image.load(full_path+'/white_rook.png'), pygame.image.load(full_path+'/black_rook.png')
white_bishop, black_bishop = pygame.image.load(full_path+'/white_bishop.png'), pygame.image.load(full_path+'/black_bishop.png')
white_pawn, black_pawn = pygame.image.load(full_path+'/white_pawn.png'), pygame.image.load(full_path+'/black_pawn.png')
white_knight, black_knight = pygame.image.load(full_path+'/white_knight.png'), pygame.image.load(full_path+'/black_knight.png')

if player_color == 'black':
    white_king, black_king = pygame.transform.flip(white_king, False, True), pygame.transform.flip(black_king, False, True)
    white_queen, black_queen = pygame.transform.flip(white_queen, False, True), pygame.transform.flip(black_queen, False, True)
    white_rook, black_rook = pygame.transform.flip(white_rook, False, True), pygame.transform.flip(black_rook, False, True)
    white_bishop, black_bishop = pygame.transform.flip(white_bishop, False, True), pygame.transform.flip(black_bishop, False, True)
    white_pawn, black_pawn = pygame.transform.flip(white_pawn, False, True), pygame.transform.flip(black_pawn, False, True)
    white_knight, black_knight = pygame.transform.flip(white_knight, False, True), pygame.transform.flip(black_knight, False, True)


#Using the os library to get the audio files of pieces
sound_path = 'CHESS SOUNDS'
full_path = os.path.join(cwd, sound_path)
full_path = full_path.replace('\\', '/')

chess_sounds = [pygame.mixer.Sound(full_path+'/game_start.mp3'),pygame.mixer.Sound(full_path+'/move_piece.mp3'), pygame.mixer.Sound(full_path+'/piece_takes.mp3'), 
                pygame.mixer.Sound(full_path+'/check.mp3'), pygame.mixer.Sound(full_path+'/castling.mp3'), pygame.mixer.Sound(full_path+'/game_over_checkmate.mp3'), 
                pygame.mixer.Sound(full_path+'/game_over_stalemate.mp3'), pygame.mixer.Sound(full_path+'/game_over.mp3')]

stockfish_path = 'Engine'
full_path = os.path.join(cwd, stockfish_path)
full_path = full_path.replace('\\', '/')
engine = chess.engine.SimpleEngine.popen_uci(full_path+'/stockfish-windows-2022.exe')



#------------------------------------------------------------------------------------------------------------------------------------------#

"""
This was created with help of Sebastian Lague who used this notation to
use binary in order to create a binary form of whether or not a piece is white or black and which
type it is

00|000
Color|Type
01010 = White Queen
"""
class Piece:
    def __init__(self):
        self.none = 0
        self.King = 1
        self.Queen = 2
        self.Rook = 3
        self.Bishop = 4
        self.Pawn = 5
        self.Knight = 6

        self.White = 8
        self.Black = 16

"""
This function returns the image of a piece based on the parameters piece_color and piece_type which are binary values 
that will be encoded through some logic
"""
def return_piece_image(piece_color, piece_type):
    #White pieces
    if piece_color == '1':
        if piece_type == '001':
            return white_king
        elif piece_type == '010':
            return white_queen
        elif piece_type == '011':
            return white_rook
        elif piece_type == '100':
            return white_bishop
        elif piece_type == '101':
            return white_pawn
        elif piece_type == '110':
            return white_knight
    #Black pieces
    elif piece_color == '10':
        if piece_type == '001':
            return black_king
        elif piece_type == '010':
            return black_queen
        elif piece_type == '011':
            return black_rook
        elif piece_type == '100':
            return black_bishop
        elif piece_type == '101':
            return black_pawn
        elif piece_type == '110':
            return black_knight

"""This draws all the tiles on the board"""
def draw_tiles(screen, previous_tile, new_tile, moves):
    global board_surface, board_rect
    # Define some constants
    ROWS = 8
    COLS = 8
    SQUARE_SIZE = screen.get_height() / ROWS // 1.4
    
    # Create a surface for each square of the checkerboard
    board_width = SQUARE_SIZE * COLS
    board_height = SQUARE_SIZE * ROWS
    board_surface = pygame.Surface((board_width, board_height))
    square = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
    colors = [(light_blue), (dark_blue)]
    font = pygame.font.Font('ConsolaMono-Bold.ttf', 18)
    # Draw the checkerboard pattern by alternating colors for each square
    for row in range(ROWS):
        for col in range(COLS):
            if (previous_tile == None and new_tile == None):
                color = colors[(row + col) % 2]
                square.fill(color)
                rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                # text = font.render(str(row*8+col), True, (0,0,0))
                # if player_color == 'black':
                #         text = pygame.transform.flip(text, True, True)
                # text_rect = text.get_rect()
                # text_rect.center = rect.center
                
                board_surface.blit(square, rect)
                #board_surface.blit(text, text_rect)
                #screen.blit(square, rect)
            elif (previous_tile != None and new_tile != None) or (previous_tile != None and new_tile == None):
                if row*8+col in moves:
                    color = (239, 112, 109)
                    square.fill(color)
                    rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                    # text = font.render(str(row*8+col), True, (0,0,0))
                    # if player_color == 'black':
                    #     text = pygame.transform.flip(text, True, True)
                    # text_rect = text.get_rect()
                    # text_rect.center = rect.center
                    
                    board_surface.blit(square, rect)
                    #board_surface.blit(text, text_rect)
                elif row*8+col == previous_tile or row*8+col == new_tile:
                    color = yellow
                    square.fill(color)
                    rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                    # text = font.render(str(row*8+col), True, (0,0,0))
                    # if player_color == 'black':
                    #     text = pygame.transform.flip(text, True, True)
                    # text_rect = text.get_rect()
                    # text_rect.center = rect.center
                    
                    board_surface.blit(square, rect)
                    #board_surface.blit(text, text_rect)
                    #screen.blit(square, rect)
                else:
                    color = colors[(row + col) % 2]
                    square.fill(color)
                    rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                    # text = font.render(str(row*8+col), True, (0,0,0))
                    # if player_color == 'black':
                    #     text = pygame.transform.flip(text, True, True)
                    # text_rect = text.get_rect()
                    # text_rect.center = rect.center
                    
                    board_surface.blit(square, rect)
                    #board_surface.blit(text, text_rect)
                    #screen.blit(square, rect)
    # Get the rectangular area of the board surface
    board_rect = board_surface.get_rect()
    
    # Center the board surface on the screen
    board_rect.center = screen.get_rect().center
    
    # Blit the board surface onto the screen
    screen.blit(board_surface, board_rect)
draw_tiles(screen, None, None, None)

"""This function converts the piece's bitwise operater to standard int"""                
def convert_piece_binary(piece):
    piece_color = str(bin(piece))[2:4] if len(str(bin(piece))) == 7 else str(bin(piece))[2]
    piece_type = str(bin(piece))[4:7] if len(str(bin(piece))) == 7 else str(bin(piece))[3:6]
    return piece_color, piece_type

"""
This function draws the pieces on the board and based on the value of the current tile[], it will then
call the function return_piece_image, which will take the binary values of tile[i] and then also print it on 
the center

The count of the tiles looks like this:
0    1    2    3    4    5    6    7  next_rank

8    9    10   11   12   13   14   15 next_rank

16   17   18   19   20   21   22   23 next_rank

24   25   26   27   28   29   30   31 next_rank

32   33   34   35   36   37   38   39 next_rank

40   41   42   43   44   45   46   47 next_rank

48   49   50   51   52   53   54   55 next_rank

56   57   58   59   60   61   62   63 next_rank

"""
def draw_board():
    global board_surface, board_rect
    for rank in range(8):
        for file in range(8):
            if tile[rank*8+file][0] != 0:
                piece_color, piece_type = convert_piece_binary(tile[rank*8+file][0])
                tile_rect = pygame.Rect(file*board_rect.width/8, rank*board_rect.height/8, board_rect.width/8, board_rect.height/8)
                piece_image = pygame.transform.scale(return_piece_image(piece_color, piece_type), (int(board_rect.width/8), int(board_rect.height/8)))
                piece_rect = piece_image.get_rect(center=tile_rect.center)
                board_surface.blit(piece_image, piece_rect)
    screen.blit(board_surface, board_rect)

"""Changing the turn after a user has made a move"""
def change_turn():
    global turn
    turn = 'w' if turn == 'b' else 'b'
    return turn

"""Changing the castling rights after user castles or makes a move that nulls the castling rights"""
def update_castling(color=None, side=None):
    color = color
    side = side
    global castle, previous_castle, previously_in_check
    if color == None and side == None:
        if tile[0] == [0,0,0] or (tile[0] != [0,0,0] and tile[0][1] != 'r'):
            if 'q' in castle:
                castle = castle.replace('q', '')
        if tile[7] == [0,0,0] or (tile[7] != [0,0,0] and tile[7][1] != 'r'):
            if 'k' in castle:
                castle = castle.replace('k', '')
        if tile[56] == [0,0,0] or (tile[56] != [0,0,0] and tile[56][1] != 'R'):
            if 'Q' in castle:
                castle = castle.replace('Q', '')
        if tile[63] == [0,0,0] or (tile[63] != [0,0,0] and tile[63][1] != 'R'):
            if 'K' in castle:
                castle = castle.replace('K', '')
        if tile[60] == [0,0,0]:
            if 'K' in castle:
                castle = castle.replace('K','')
            if 'Q' in castle:
                castle = castle.replace('Q', '')
        if tile[4] == [0,0,0]:
            if 'k' in castle:
                castle = castle.replace('k', '')
            if 'q' in castle:
                castle = castle.replace('q', '')

    if king_in_check() != None and king_in_check()[0] == 'white':
        previously_in_check = True
        previous_castle = castle
        if 'K' in castle:
            castle = castle.replace('K','')
        if 'Q' in castle:
            castle = castle.replace('Q', '')
    elif king_in_check() != None and king_in_check()[0] == 'black':
        previously_in_check = True
        previous_castle = castle
        if 'k' in castle:
            castle = castle.replace('k', '')
        if 'q' in castle:
            castle = castle.replace('q', '')
    elif king_in_check() == None and previously_in_check == True:
        castle = previous_castle
        previously_in_check = False
        #Making sure the new castle we set is still okay
        if tile[0] == [0,0,0] or (tile[0] != [0,0,0] and tile[0][1] != 'r'):
            if 'q' in castle:
                castle = castle.replace('q', '')
        if tile[7] == [0,0,0] or (tile[7] != [0,0,0] and tile[7][1] != 'r'):
            if 'k' in castle:
                castle = castle.replace('k', '')
        if tile[56] == [0,0,0] or (tile[56] != [0,0,0] and tile[56][1] != 'R'):
            if 'Q' in castle:
                castle = castle.replace('Q', '')
        if tile[63] == [0,0,0] or (tile[63] != [0,0,0] and tile[63][1] != 'R'):
            if 'K' in castle:
                castle = castle.replace('K', '')
        if tile[60] == [0,0,0]:
            if 'K' in castle:
                castle = castle.replace('K','')
            if 'Q' in castle:
                castle = castle.replace('Q', '')
        if tile[4] == [0,0,0]:
            if 'k' in castle:
                castle = castle.replace('k', '')
            if 'q' in castle:
                castle = castle.replace('q', '')

    if castle == '':
        castle = '-'

def change_fen(new_fen):
    global fen_position
    fen_position = new_fen

"""Updating the fen notation after a user has made a move"""
def update_fen():
    global fen_position, turn, castle, en_passant, halfmove_count, fullmove_count
    board_str = ''.join(str(piece[1]) for piece in tile)
    rows = [board_str[i:i+8] for i in range(0, 64, 8)]
    # Replace consecutive empty squares with numbers
    for i in range(8):
        row = rows[i]
        new_row = ''
        count = 0
        for j in range(8):
            if row[j] == '0':
                count += 1
            else:
                if count > 0:
                    new_row += str(count)
                    count = 0
                new_row += row[j]
        if count > 0:
            new_row += str(count)
        rows[i] = new_row

    # Convert rows to FEN notation
    fen_rows = []
    for row in rows:
        if row == '':
            fen_rows.append('8')
        else:
            fen_rows.append(row)


    fen_position = '/'.join(fen_rows)
    fen_position+=' ' + turn + ' ' + castle + ' ' + en_passant + ' ' + str(halfmove_count) + ' ' + str(fullmove_count)
    return fen_position
    
"""
Using the standard FEN notation, a color of a piece is denoted by if its uppercase or not
so, b would be a black bishop while B would be a white bishop.
"""
def load_from_FEN():
    global fen_position
    piece = Piece()
    drawable_fen_notation = fen_position.split(' ')[0]
    rank, file = 0, 0
    fen_piece_notation = {
        'r' : piece.Rook,
        'b' : piece.Bishop,
        'n' : piece.Knight,
        'q' : piece.Queen,
        'k' : piece.King,
        'p' : piece.Pawn
    }
    for char in drawable_fen_notation:
        if char == '/':
            rank+=1
            file = 0
        else:
            if char.isnumeric() == True:
                num_skip_tiles = int(char)
                file+=num_skip_tiles
            else:
                piece_color = piece.White if char.isupper() else piece.Black
                piece_type = fen_piece_notation[char.lower()]
                tile[rank*8+file][0] = piece_color | piece_type
                tile[rank*8+file][1] = char
                char_lower = tile[rank*8+file][1].lower()
                if char_lower == 'r' or char_lower == 'b' or char_lower == 'q': #This is to check whether or not a piece is a sliding piece
                    tile[rank*8+file][2] = True
                file+=1
    draw_board()

"""Updating the en passant square"""
def update_en_passant(en_passant_square):
    global en_passant
    en_passant = en_passant_square

"""Updating the halfmove counter and the parameter move_type is a string that contains ('pawn_move', 'capture', 'regular move')"""
def update_halfmove(move_type):
    global halfmove_count
    if move_type == 'pawn_move' or move_type == 'capture':
        halfmove_count = 0
    elif move_type == 'regular_move':
        halfmove_count+=1

"""Updating the fullmove counter"""
def update_fullmove():
    global fullmove_count
    fullmove_count+=1

def get_mouse_position_on_board():
    global board_rect, player_color
    # Offset mouse position based on board surface rect
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if player_color == 'black':
        mouse_y = screen_height - mouse_y
        mouse_x = screen_width - mouse_x
    board_x, board_y = board_rect.topleft
    mouse_x-=board_x
    mouse_y-=board_y

    # Calculate tile position based on mouse position
    tile_size = board_surface.get_width() // 8
    file = mouse_x // tile_size
    rank = mouse_y // tile_size
    return (rank, file)

def get_square_under_mouse():
    global board_rect
    x, y = get_mouse_position_on_board()

    rank=x
    file=y
    
    return rank * 8 + file

"""This will return the last value of the mouse position when dropped"""
def drag(selected_piece):
    global board_rect, player_color
    if selected_piece:
        # Offset mouse position based on board surface rect
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # if player_color == 'black':
        #     mouse_y = screen_height - mouse_y
        tile_under_mouse = get_square_under_mouse()
        selected_piece_color, selected_piece_type = convert_piece_binary(selected_piece[0])
        selected_piece_image = pygame.transform.scale(return_piece_image(selected_piece_color, selected_piece_type), (int(board_rect.width/8) + 25, int(board_rect.height/8)+25))
        if player_color == 'black':
            selected_piece_image = pygame.transform.flip(selected_piece_image, True, True)
        #selected_piece_image = pygame.transform.scale(return_piece_image(selected_piece_color, selected_piece_type), (screen_width/8, screen_height/8))
        screen.blit(selected_piece_image, selected_piece_image.get_rect(center=(mouse_x,mouse_y)))
        return tile_under_mouse, selected_piece

"""
This is using Sebastian Lague's technique of using a big function that will determine the moves of a certain tile
then depending on the piece, it will then append certain moveable tiles to moves[]

Starting at 0, this is the num of the distances between other indexes around the 0th piece
 -9 |-8 |-7
 -----------
 -1 | 0 | 1
 -----------
  7 | 8 | 9

"""
def generate_moves(tile_num, color):
    global turn
    pinned_pieces = generate_pinned_pieces()
    moves = []
    real_moves = []
    if ((color.islower() and turn == 'b') or (color.isupper() and turn == 'w')) and king_in_check() == None and (tile_num not in pinned_pieces):
        if tile[tile_num][2] == True: #Checks if the piece is a sliding piece or not
            moves = generate_sliding_moves(tile_num, color)
            return moves
        elif tile[tile_num][1].lower() == 'n':
            moves = generate_knight_moves(tile_num, color)
            return moves
        elif tile[tile_num][1].lower() == 'k':
            moves = generate_king_moves(tile_num, color)
            return moves
        elif tile[tile_num][1].lower() == 'p':
            moves = generate_pawn_moves(tile_num, color)
            return moves
    elif ((color.islower() and turn == 'b') or (color.isupper() and turn == 'w')) and king_in_check() == None and (tile_num in pinned_pieces):
        print('this one!')
        moves = generate_pinned_piece_moves(tile_num, color)
        return moves
    elif ((color.islower() and turn == 'b') or (color.isupper() and turn == 'w')) and king_in_check() != None and (tile_num not in pinned_pieces):
        white_king_tile, black_king_tile = get_kings_square() # Getting the square of the king
        king_in_attack, attacker_tile = king_in_check() # Retrieving the color of the king under attack
        attacker_tile_color = 'black' if tile[attacker_tile][1].islower() else 'white' #Retrieving the color of the attacking tile

        if tile[attacker_tile][2] == True: #Generating attacking tile move if attacker is sliding piece
            attacking_tiles = generate_sliding_moves(attacker_tile, attacker_tile_color)
        else: # If the piece isn't a sliding piece, meaning that the check cannot be blocked, the only attacking move is the king's tile
            king_under_attack_tile = white_king_tile if king_in_attack == 'white' else black_king_tile
            attacking_tiles = [king_under_attack_tile]
        
        """Generating the possible moves now based on the piece the user wants to use"""
        if tile[tile_num][2] == True: #Checks if the piece is a sliding piece or not
            moves = generate_sliding_moves(tile_num, color)
        elif tile[tile_num][1].lower() == 'n':
            moves = generate_knight_moves(tile_num, color)
        elif tile[tile_num][1].lower() == 'k':
            moves = generate_king_moves(tile_num, color)
            real_moves = []
            for move in moves:
                if move == attacker_tile or move not in attacking_tiles:
                    if move != white_king_tile and move != black_king_tile:
                        if move not in real_moves:
                            real_moves.append(move)
            return real_moves
        elif tile[tile_num][1].lower() == 'p':
            moves = generate_pawn_moves(tile_num, color)

        real_moves = []
        for move in moves:
            if (move == attacker_tile or move in attacking_tiles) and (move != white_king_tile and move != black_king_tile):
                # Temporarily letting the pieces move into their pseudo-legal moves and see if it puts their king in check, if it does, don't apppend it
                curr_color = 'black' if tile[tile_num][1].islower() else 'white'
                previous_tile_value = tile[tile_num]
                tile[tile_num] = [0,0,0]
                previous_move_value = tile[move]
                tile[move] = previous_tile_value

                # Now we see if this move puts its king in check
                pseudo_check = king_in_check()
                if pseudo_check == None and move not in real_moves:
                    real_moves.append(move)
                # elif pseudo_check != None and pseudo_check[0] != curr_color and move not in real_moves:
                #     real_moves.append(move)
                
                tile[tile_num] = previous_tile_value
                tile[move] = previous_move_value
        return real_moves
    return moves

"""This function returns the tile number of both the white king and the black king"""
def get_kings_square():
    white_king_tile = None
    black_king_tile = None
    for i in range(64):
        if tile[i] != [0,0,0] and tile[i][1] == 'k':
            if black_king_tile != None:
                black_king_tile = i
                break
            else:
                black_king_tile = i
        elif tile[i] != [0,0,0] and tile[i][1] == 'K':
            if black_king_tile != None:
                white_king_tile = i
                break
            else:
                white_king_tile = i
    return (white_king_tile, black_king_tile)

"""This function essentially returns the amount of squares to the edge and this is used mainly for generating the sliding moves for the sliding pieces"""
def count_squares_to_edge(index):
    # Convert the one-dimensional index to row and column coordinates
    row = index // 8
    col = index % 8

    # Calculate the number of squares to the edge of the board in each direction
    squares_to_edge={
        'up' : row,
        'down' : 7 - row,
        'left' : col,
        'right' : 7 - col,
        'up_left' : min(row, col),
        'up_right' : min(row, 7 - col),
        'down_left' : min(7 - row, col),
        'down_right' : min(7 - row, 7 - col)
    }
    return squares_to_edge

"""This function generates the possible tiles that a sliding piece can move
Sliding pieces are Queen, Rook, Bishop"""
def generate_sliding_moves(tile_num, color):

    next_tile_color = 0
    piece_color = 'black' if color.islower() else 'white'

    """
    possible_tiles is a 2d array of size 8 that contains the possible tiles that a certain piece can move to in each of the 8 directions
    each index goes like this:
    0: possible top left directions
    1: possible top right directions
    2: possible bottom right directions
    3: possible bottom left directions
    4: possible up directions
    5: possible left directions
    6: possible down directions
    7: possible right directions
    """
    possible_tiles = [] 

    #This dictionary contains the amount of squares to the edge based on the position of the board

    squares_to_edge_of_board = count_squares_to_edge(tile_num)

    possible_moves = {
        -9 : squares_to_edge_of_board['up_left'],
        -7 : squares_to_edge_of_board['up_right'],
         9 : squares_to_edge_of_board['down_right'],
         7 : squares_to_edge_of_board['down_left'],
        -8 : squares_to_edge_of_board['up'],
        -1 : squares_to_edge_of_board['left'],
         8 : squares_to_edge_of_board['down'],
         1 : squares_to_edge_of_board['right']
    }
    
    for move in possible_moves:
        possible_tiles_in_direction = []
        next_tile = (tile_num+move)
        max_count = possible_moves[move]

        for i in range(max_count):
            if (next_tile < 64 and next_tile >= 0) and tile[next_tile] != [0,0,0]:
                next_tile_color = 'black' if tile[next_tile][1].islower() else 'white'
                if next_tile_color != piece_color:
                    possible_tiles_in_direction.append(next_tile)
                    break
                elif next_tile_color == piece_color:
                    break
            elif (next_tile < 64 and next_tile >= 0) and tile[next_tile] == [0,0,0]:
                possible_tiles_in_direction.append(next_tile)
                next_tile+=move
               
        possible_tiles.append(possible_tiles_in_direction)

    """
    The next lines of code will make it so that:
      - rook can only move up, down, left, right
      - bishop can only move diagonally
      - queen can move in all directions
    """
    if tile[tile_num][1].lower() == 'r':
        possible_tiles = possible_tiles[4:]
        possible_tiles = [move for row in possible_tiles for move in row]
        return possible_tiles
    elif tile[tile_num][1].lower() == 'b':
        possible_tiles = possible_tiles[0:4]
        possible_tiles = [move for row in possible_tiles for move in row]
        return possible_tiles
    elif tile[tile_num][1].lower() == 'q':
        possible_tiles = [move for row in possible_tiles for move in row]
        return possible_tiles     

"""
This function will generate all the sliding pieces that can attack the king.
Sliding pieces are the only pieces that can pin a certain piece so we will use this function
in order to help generate whether or not a piece is also pinned or not
This function should return the tile that the attacking piece is on and also the possible tiles that it can move to, only if its 
"""
def generate_attacking_pieces():
    global turn
    all_attacking_tiles = []
    attacker_tiles = []
    white_king_square, black_king_square = get_kings_square()
    #This logic only detects sliding pieces ie. rooks, bishops, queens as these are the only pieces that can pin a piece and can have their line of sight blocked by another piece

    if turn == 'w': #Checking if any black pieces are attacking the white king
        for i in range(64):
            if tile[i] != [0,0,0] and tile[i][2] == True and tile[i][1].islower() == True: #Making sure that the tile we are looking at isn't empty and that it is a sliding piece

                """We are now going to use a slightly modified implementation of the generate_sliding_piece() function"""

                current_piece_color = 'black' #this is since we are only checking black pieces in this function
                next_tile_color = 0 #this is going to be used so that we can compare the current piece color to the other tiles that it can move to
                current_attacking_tiles = [] #this is to detect all the tiles that the piece can possibly move to
                squares_to_edge_of_board = count_squares_to_edge(i) #This dictionary contains the amount of squares to the edge based on the position of the board

                if tile[i][1] == 'q':
                    possible_moves = { 
                    -9 : squares_to_edge_of_board['up_left'],
                    -7 : squares_to_edge_of_board['up_right'],
                    9 : squares_to_edge_of_board['down_right'],
                    7 : squares_to_edge_of_board['down_left'],
                    -8 : squares_to_edge_of_board['up'],
                    -1 : squares_to_edge_of_board['left'],
                    8 : squares_to_edge_of_board['down'],
                    1 : squares_to_edge_of_board['right']
                    }
                elif tile[i][1] == 'r':
                    possible_moves = { 
                    -8 : squares_to_edge_of_board['up'],
                    -1 : squares_to_edge_of_board['left'],
                    8 : squares_to_edge_of_board['down'],
                    1 : squares_to_edge_of_board['right']
                    }
                elif tile[i][1] == 'b':
                    possible_moves = { 
                    -9 : squares_to_edge_of_board['up_left'],
                    -7 : squares_to_edge_of_board['up_right'],
                    9 : squares_to_edge_of_board['down_right'],
                    7 : squares_to_edge_of_board['down_left'],
                    }

                """Now we iterate through all the possible directions that this tile can move to and if it satisfies the conditions, we append each valid tile to current_attacking_tiles"""
                for move in possible_moves:
                    possible_tiles_in_direction = []
                    next_tile = (i+move)
                    max_count = possible_moves[move]

                    for j in range(max_count):
                        if (next_tile < 64 and next_tile >= 0) and tile[next_tile] != [0,0,0] and tile[next_tile][1] == 'K':
                            next_tile_color = 'black' if tile[next_tile][1].islower() else 'white'
                            if next_tile_color != current_piece_color:
                                possible_tiles_in_direction.append(next_tile)
                                break
                            elif next_tile_color == current_piece_color:
                                break
                        elif (next_tile < 64 and next_tile >= 0) and tile[next_tile] != [0,0,0] and tile[next_tile][1] != 'K':
                            next_tile_color = 'black' if tile[next_tile][1].islower() else 'white'
                            if next_tile_color != current_piece_color:
                                possible_tiles_in_direction.append(next_tile)
                                next_tile+=move
                            elif next_tile_color == current_piece_color:
                                break
                        elif (next_tile < 64 and next_tile >= 0) and tile[next_tile] == [0,0,0]:
                            possible_tiles_in_direction.append(next_tile)
                            next_tile+=move
                    
                    if white_king_square in possible_tiles_in_direction: #If the white king's square was found in the current iteration of possible moves
                        if i not in attacker_tiles:
                            attacker_tiles.append(i)
                        current_attacking_tiles.append(possible_tiles_in_direction)
                    else: #If the white king's square wasn't found in the current iteration of possible moves
                        current_attacking_tiles.append([])
                    
                all_attacking_tiles.append(current_attacking_tiles)
    elif turn == 'b': #Checking if any white pieces are attacking the black king
        for i in range(64):
            if tile[i] != [0,0,0] and tile[i][2] == True and tile[i][1].isupper() == True: #Making sure that the tile we are looking at isn't empty and that it is a sliding piece

                """We are now going to use a slightly modified implementation of the generate_sliding_piece() function"""

                current_piece_color = 'white' #this is since we are only checking white pieces in this function
                next_tile_color = 0 #this is going to be used so that we can compare the current piece color to the other tiles that it can move to
                current_attacking_tiles = [] #this is to detect all the tiles that the piece can possibly move to
                squares_to_edge_of_board = count_squares_to_edge(i) #This dictionary contains the amount of squares to the edge based on the position of the board

                if tile[i][1] == 'Q':
                    possible_moves = { 
                    -9 : squares_to_edge_of_board['up_left'],
                    -7 : squares_to_edge_of_board['up_right'],
                    9 : squares_to_edge_of_board['down_right'],
                    7 : squares_to_edge_of_board['down_left'],
                    -8 : squares_to_edge_of_board['up'],
                    -1 : squares_to_edge_of_board['left'],
                    8 : squares_to_edge_of_board['down'],
                    1 : squares_to_edge_of_board['right']
                    }
                elif tile[i][1] == 'R':
                    possible_moves = { 
                    -8 : squares_to_edge_of_board['up'],
                    -1 : squares_to_edge_of_board['left'],
                    8 : squares_to_edge_of_board['down'],
                    1 : squares_to_edge_of_board['right']
                    }
                elif tile[i][1] == 'B':
                    possible_moves = { 
                    -9 : squares_to_edge_of_board['up_left'],
                    -7 : squares_to_edge_of_board['up_right'],
                    9 : squares_to_edge_of_board['down_right'],
                    7 : squares_to_edge_of_board['down_left'],
                    }


                """Now we iterate through all the possible directions that this tile can move to and if it satisfies the conditions, we append each valid tile to current_attacking_tiles"""
                for move in possible_moves:
                    possible_tiles_in_direction = []
                    next_tile = (i+move)
                    max_count = possible_moves[move]

                    for j in range(max_count):
                        if (next_tile < 64 and next_tile >= 0) and tile[next_tile] != [0,0,0] and tile[next_tile][1] == 'k':
                            next_tile_color = 'black' if tile[next_tile][1].islower() else 'white'
                            if next_tile_color != current_piece_color:
                                possible_tiles_in_direction.append(next_tile)
                                break
                            elif next_tile_color == current_piece_color:
                                break
                        elif (next_tile < 64 and next_tile >= 0) and tile[next_tile] != [0,0,0] and tile[next_tile][1] != 'k':
                            next_tile_color = 'black' if tile[next_tile][1].islower() else 'white'
                            if next_tile_color != current_piece_color:
                                possible_tiles_in_direction.append(next_tile)
                                next_tile+=move
                            elif next_tile_color == current_piece_color:
                                break
                        elif (next_tile < 64 and next_tile >= 0) and tile[next_tile] == [0,0,0]:
                            possible_tiles_in_direction.append(next_tile)
                            next_tile+=move
                    
                    if black_king_square in possible_tiles_in_direction: #If the black king's square was found in the current iteration of possible moves
                        if i not in attacker_tiles:
                            attacker_tiles.append(i)
                        current_attacking_tiles.append(possible_tiles_in_direction)
                    else: #If the black king's square wasn't found in the current iteration of possible moves
                        current_attacking_tiles.append([])

                all_attacking_tiles.append(current_attacking_tiles)

    all_attacking_tiles = [move for row in all_attacking_tiles for move in row]
    #all_attacking_tiles = [move for row in all_attacking_tiles for move in row]
    return all_attacking_tiles, attacker_tiles

"""This function generates the pawns moves"""
def generate_pawn_moves(tile_num, color):
    global en_passant_tile, en_passant_tile_color, player_color, en_passant
    piece_color = 'black' if color.islower() else 'white'
    next_tile_color = 0
    possible_tiles = []
    starting_move_black_offsets = [8, 16, 7, 9] #Bottom left, bottom, bottom right, two spaces forward
    starting_move_white_offsets = [-8, -16, -7, -9] #Top right, top, top left, two spaces forward
    regular_black_offsets = [8, 7, 9]
    regular_white_offsets = [-8, -7, -9]
    
    pawn_file = tile_num%8
    if pawn_file == 0 and piece_color == 'white':
        regular_white_offsets.remove(-9)
    elif pawn_file == 7 and piece_color == 'black':
        regular_black_offsets.remove(9)

    #Black pawn (if not moved yet)
    if tile_num >= 8 and tile_num <= 15 and piece_color == 'black':
        for offset in starting_move_black_offsets: #Removing tiles in front of the pawn if it has a piece or removing a tile if the diagonal isn't empty but has a same piece color
            if tile[tile_num+offset] != [0,0,0]:
                next_tile_color = 'black' if tile[tile_num+offset][1].islower() else 'white'
                if offset == 7 and next_tile_color != piece_color:
                    possible_tiles.append(tile_num+offset)
                elif offset == 9 and next_tile_color != piece_color:
                    possible_tiles.append(tile_num+offset)
            elif tile[tile_num+offset] == [0,0,0]:
                if offset == 8:
                    possible_tiles.append(tile_num+offset)
                elif offset == 16 and tile[tile_num+8] == [0,0,0]:
                    possible_tiles.append(tile_num+offset)
    #White pawn (if not moved yet)
    elif tile_num >= 48 and tile_num <= 55 and piece_color == 'white':
        for offset in starting_move_white_offsets: #Removing tiles in front of the pawn if it has a piece or removing a tile if the diagonal isn't empty but has a same piece color
            if tile[tile_num+offset] != [0,0,0]:
                next_tile_color = 'black' if tile[tile_num+offset][1].islower() else 'white'
                if offset == -7 and next_tile_color != piece_color:
                    possible_tiles.append(tile_num+offset)
                elif offset == -9 and next_tile_color != piece_color:
                    possible_tiles.append(tile_num+offset)
            elif tile[tile_num+offset] == [0,0,0]:
                if offset == -8:
                    possible_tiles.append(tile_num+offset)
                elif offset == -16 and tile[tile_num-8] == [0,0,0]:
                    possible_tiles.append(tile_num+offset)
    elif piece_color == 'black':
        for offset in regular_black_offsets:
            if (tile_num+offset <= 63 and tile_num+offset >= 0) and tile[tile_num+offset] != [0,0,0]:
                next_tile_color = 'black' if tile[tile_num+offset][1].islower() else 'white'
                if offset == 7 and next_tile_color != piece_color:
                    possible_tiles.append(tile_num+offset)
                elif offset == 9 and next_tile_color != piece_color:
                    possible_tiles.append(tile_num+offset)
            elif (tile_num+offset <= 63 and tile_num+offset >= 0) and tile[tile_num+offset] == [0,0,0]:
                if offset == 8:
                    possible_tiles.append(tile_num+offset)
    elif piece_color == 'white':
        for offset in regular_white_offsets: #Removing tiles in front of the pawn if it has a piece or removing a tile if the diagonal isn't empty but has a same piece color
            if (tile_num+offset <= 63 and tile_num+offset >= 0) and tile[tile_num+offset] != [0,0,0]:
                next_tile_color = 'black' if tile[tile_num+offset][1].islower() else 'white'
                if offset == -7 and next_tile_color != piece_color:
                    possible_tiles.append(tile_num+offset)
                elif offset == -9 and next_tile_color != piece_color:
                    possible_tiles.append(tile_num+offset)
            elif (tile_num+offset <= 63 and tile_num+offset >= 0) and tile[tile_num+offset] == [0,0,0]:
                if offset == -8:
                    possible_tiles.append(tile_num+offset)
                elif offset == -16 and tile[tile_num-8] == [0,0,0]:
                    possible_tiles.append(tile_num+offset)

    if en_passant != '-':
        # if player_color == 'white' :
        #     position = tiles_white_values.index(en_passant)
        #     en_passant_tile = tiles_white_keys[position]
        #     en_passant_tile_color = 'black' if tile[en_passant_tile][1].islower() else 'white'
        # elif player_color == 'black':
        #     position = tiles_black_values.index(en_passant)
        #     en_passant_tile = tiles_black_keys[position]
        #     en_passant_tile_color = 'black' if tile[en_passant_tile][1].islower() else 'white'
        position = tiles_white_values.index(en_passant)
        en_passant_tile = tiles_white_keys[position]
        en_passant_tile_color = 'black' if tile[en_passant_tile][1].islower() else 'white'
        
            
        if tile_num+1 == en_passant_tile:
            if piece_color == 'white' and piece_color != en_passant_tile_color:
                possible_tiles.append((tile_num-8)+1)
            elif piece_color == 'black' and piece_color != en_passant_tile_color:
                possible_tiles.append((tile_num+8)+1)
        elif tile_num-1 == en_passant_tile:
            if piece_color == 'white' and piece_color != en_passant_tile_color:
                possible_tiles.append((tile_num-8)-1)
            elif piece_color == 'black' and piece_color != en_passant_tile_color:
                possible_tiles.append((tile_num+8)-1)
    return possible_tiles

"""This function generates knight moves"""
def generate_knight_moves(tile_num, color):
    piece_color = 'black' if color.islower() else 'white'
    knight_move_offsets = [-10, -15, -17, -6, 10, 15, 17, 6]
    knight_file = tile_num % 8
    if knight_file == 7 and color.isupper(): #Removing certain offsets for the white knight in file 7
        knight_move_offsets.remove(-6)
        knight_move_offsets.remove(-15)
    elif knight_file == 7 and color.islower(): #Removing certain offsets for black knight in file 7
        knight_move_offsets.remove(-6)
        knight_move_offsets.remove(-15)
        knight_move_offsets.remove(10)
        knight_move_offsets.remove(17)
    elif knight_file == 0 and color.isupper(): #Removing certain offsetes for white knight in file 0
        knight_move_offsets.remove(6)
        knight_move_offsets.remove(-10)
        knight_move_offsets.remove(-17)
    elif knight_file == 0 and color.islower():
        knight_move_offsets.remove(6)
        knight_move_offsets.remove(15)

    if knight_file == 1:
        knight_move_offsets.remove(6)
        knight_move_offsets.remove(-10)
    elif knight_file == 6:
        knight_move_offsets.remove(-6)
        knight_move_offsets.remove(10)

    pseudo_possible_tiles = []
    possible_tiles = []
    for offset in knight_move_offsets:
        if tile_num+offset <= 63 and tile_num+offset >= 0: #Removing any moves that are outside the bounds of the board and
            pseudo_possible_tiles.append(tile_num+offset)  #appending it to the new pseudo_possible_tiles list
    
    for possible_tile in pseudo_possible_tiles:
        if tile[possible_tile] == [0,0,0]:
            possible_tiles.append(possible_tile)
        elif tile[possible_tile] != [0,0,0]:
            possible_tile_color = 'black' if tile[possible_tile][1].islower() else 'white'
            if piece_color != possible_tile_color:
                possible_tiles.append(possible_tile)
    return possible_tiles

"""This function generates the kings moves and also makes it so that it cannot move itself into check"""
def generate_king_moves(tile_num, color):
    global currently_in_check, castle
    king_color = 'black' if color.islower() else 'white'
    both_king_tiles = get_kings_square()
    other_king_color = 'black' if king_color == 'white' else 'white'
    other_king_tile = both_king_tiles[1] if tile_num == both_king_tiles[0] else both_king_tiles[0]

    currently_in_check = king_in_check() #should return none, else it should return the color of the king in check and the tile of the attacker
    pseudo_check = None
    pseudo_moves = []
    other_king_pseudo_moves = []
    real_moves = []
    king_offsets = [-9, -8, -7, -1, 1, 7, 8, 9] #These are the tile positions that the king is available to move to potentially
    other_king_offsets = [-9, -8, -7, -1, 1, 7, 8, 9]
    #First we will be removing any tiles that the king cannot move to because of their own colored piece in the way or the move is out of the bounds of the board
    king_file = tile_num % 8
    if king_file == 7:
        king_offsets.remove(-7)
        king_offsets.remove(1)
        king_offsets.remove(9)
    elif king_file == 0:
        king_offsets.remove(7)
        king_offsets.remove(-1)
        king_offsets.remove(-9)

    other_king_file = other_king_tile % 8
    if other_king_file == 7:
        other_king_offsets.remove(-7)
        other_king_offsets.remove(1)
        other_king_offsets.remove(9)
    elif other_king_file == 0:
        other_king_offsets.remove(7)
        other_king_offsets.remove(-1)
        other_king_offsets.remove(-9)


    #Getting the current king offsets
    for offset in king_offsets:
        if tile_num+offset >= 0 and tile_num+offset <= 63:
            if tile[tile_num+offset] == [0,0,0]:
                pseudo_moves.append(tile_num+offset)
            elif tile[tile_num+offset] != [0,0,0]:
                tile_color = 'black' if tile[tile_num+offset][1].islower() else 'white'
                if tile_color != king_color:
                    pseudo_moves.append(tile_num+offset)

    #Getting the other_king offsets
    for offset in other_king_offsets:
        if other_king_tile+offset >= 0 and other_king_tile+offset <= 63:
            if tile[other_king_tile+offset] == [0,0,0]:
                other_king_pseudo_moves.append(other_king_tile+offset)
            elif tile[other_king_tile+offset] != [0,0,0]:
                tile_color = 'black' if tile[other_king_tile+offset][1].islower() else 'white'
                if tile_color != king_color:
                    other_king_pseudo_moves.append(other_king_tile+offset)


    white_king_square, black_king_square = get_kings_square()

    if white_king_square == 60 and king_color == 'white':
        #White king castling moves
        if 'Q' in castle and tile[59] == [0,0,0] and tile[57] == [0,0,0] and tile[58] == [0,0,0]:
            pseudo_moves.append(58)
        if 'K' in castle and tile[61] == [0,0,0] and tile[62] == [0,0,0]:
            pseudo_moves.append(62)
    elif black_king_square == 4 and king_color == 'black':
        #Black king castling moves
        if 'q' in castle and tile[3] == [0,0,0] and tile[1] == [0,0,0] and tile[2] == [0,0,0]:
            pseudo_moves.append(2)
        if 'k' in castle and tile[5] == [0,0,0] and tile[6] == [0,0,0]:
            pseudo_moves.append(6)

    #This will now start to put the king in each of the possible moves, if it is then put in check after making that move, it cannot move there
    for move in pseudo_moves:
        if move not in other_king_pseudo_moves:
            original_king_position = tile[tile_num]
            previous_tile = tile[move] #keep track of the tile that we deleted
            tile[move] = tile[tile_num] #putting the king in this position
            tile[tile_num] = [0,0,0] #removing the king from that position for a slight second
            pseudo_check = king_in_check()
            if pseudo_check == None:
                if move not in real_moves:
                    real_moves.append(move)
                    tile[move] = previous_tile
                    tile[tile_num] = original_king_position
            else:
                tile[move] = previous_tile
                tile[tile_num] = original_king_position
    
    return real_moves

"""This function helps figure out whether or not the king is currently in check or not"""
def king_in_check():
    global turn
    white_king_tile, black_king_tile = get_kings_square()

    #Checking if any piece has a chance to attack the kings, if they do, then we return the color of the king that is being attacked and the tile of the attacker
    #Returns None if no attacker is found
    for j in range(64):
        #Need to check if sliding_piece is attacking
        if tile[j] != [0,0,0] and tile[j][1].lower() != 'k' and (tile[j][1].lower() == 'q' or tile[j][1].lower() == 'b' or tile[j][1].lower() == 'r'):
            curr_tile_moves = generate_sliding_moves(j, tile[j][1])
            if white_king_tile in curr_tile_moves:
                return ('white', j)
            elif black_king_tile in curr_tile_moves:
                return ('black', j)
        #Checking if knight is attacking
        elif tile[j] != [0,0,0] and tile[j][1].lower() != 'k' and tile[j][1].lower() == 'n':
            curr_tile_moves = generate_knight_moves(j, tile[j][1])
            if white_king_tile in curr_tile_moves:
                return ('white', j)
            elif black_king_tile in curr_tile_moves:
                return ('black', j)
        #Checking if pawn is attacking
        elif tile[j] != [0,0,0] and tile[j][1].lower() != 'k' and tile[j][1].lower() == 'p':
            curr_tile_moves = generate_pawn_moves(j, tile[j][1])
            if white_king_tile in curr_tile_moves:
                return ('white', j)
            elif black_king_tile in curr_tile_moves:
                return ('black', j)       
    return None

"""
This function will detect pinned pieces and will help so that pinned pieces can't be moved
It will use the help of generate_attacking_pieces() in order to figure out whether or not a piece is actually pinned
The generate_attacking_pieces() function actually returns a list of tiles that an sliding-attacking piece can move to, 
if a certain piece is within that vicinity, then it is a pinned piece, it cannot move as it will put its own king in check
"""
def generate_pinned_pieces():
    attacking_tiles = generate_attacking_pieces()[0]
    pinned_pieces = []

    #Checking if the piece is in any of the possible tiles that would be attacked
    for move in attacking_tiles:
        for i in range(64):
            if tile[i] != [0,0,0] and tile[i][1].lower() != 'k' and i in move and i not in pinned_pieces:
                pinned_pieces.append(i)
                
                
    
    real_pinned_pieces = pinned_pieces.copy()
    #Validating pinned pieces by moving them away and seeing if a check is made possible, if so, then the piece is for sure pinned
    for pinned_piece in pinned_pieces:
        pinned_piece_color = 'black' if tile[pinned_piece][1].islower() else 'white'
        if tile[pinned_piece][1].lower() == 'p':
            pinned_piece_moves = generate_pawn_moves(pinned_piece, pinned_piece_color)
        elif tile[pinned_piece][1].lower() == 'q' or tile[pinned_piece][1].lower() == 'r' or tile[pinned_piece][1].lower() == 'b':
            pinned_piece_moves = generate_sliding_moves(pinned_piece, pinned_piece_color) 
        elif tile[pinned_piece][1].lower() == 'n':
            pinned_piece_moves = generate_knight_moves(pinned_piece, pinned_piece_color)
        #Detecting whether any of their moves leads to a check
        for move in pinned_piece_moves:
            #Temporarily make that move
            previous_pinned_piece_value = tile[pinned_piece]
            previous_move_value = tile[move]
            tile[move] = tile[pinned_piece]
            tile[pinned_piece] = [0,0,0] 

            #Checking if that move put the king in check
            if king_in_check() == None:
                if pinned_piece in real_pinned_pieces:
                    real_pinned_pieces.remove(pinned_piece)
                #Putting pieces back in their correct spot
                tile[pinned_piece] = previous_pinned_piece_value
                tile[move] = previous_move_value
                break

            tile[pinned_piece] = previous_pinned_piece_value
            tile[move] = previous_move_value

                
    return real_pinned_pieces

"""Generating the moves that pinned pieces can make"""
def generate_pinned_piece_moves(tile_num, color):
    attacker_tiles = generate_attacking_pieces()[1] # Returns the tiles of the any attackers of pinned pieces
    pinned_color = 'black' if color.islower() else 'white'
    legal_moves = []

    if tile[tile_num][1].lower() == 'p':
        curr_moves = generate_pawn_moves(tile_num, color)
    elif tile[tile_num][1].lower() == 'n':
        curr_moves = generate_knight_moves(tile_num, color)
    elif tile[tile_num][2] == True:
        curr_moves = generate_sliding_moves(tile_num, color)
    semi_legal_moves = []
    #Only filtering moves that can lead to eating an attacking piece
    for move in curr_moves:
        if move in attacker_tiles and move not in semi_legal_moves:
            semi_legal_moves.append(move)

    #Temporarily let the pinned piece eat any of the attacker tiles and then if the king is not put in check, then we can eat, if not, it cannot move there
    for semiLegalMove in semi_legal_moves:
        prev_pinned_piece_position = tile[tile_num]
        tile[tile_num] = [0,0,0]
        prev_attacker_piece_position = tile[semiLegalMove]
        tile[semiLegalMove] = prev_pinned_piece_position
        pseudo_check = king_in_check()

        if pseudo_check == None or (pseudo_check != None and pseudo_check != pinned_color):
            legal_moves.append(semiLegalMove)
        
        tile[tile_num] = prev_pinned_piece_position
        tile[semiLegalMove] = prev_attacker_piece_position

    return legal_moves

"""This function plays sound"""
def play_sound(sound):
    sound.play()

"""This function helps play sound using the threading library so that playing sound doesn't actually affect the other code"""
def play_sound_threaded(index):
    sound = chess_sounds[index]
    sound_thread = threading.Thread(target=play_sound, args=(sound,))
    sound_thread.start()

"""This function will help make a promoted piece"""
def promote_pawn(tile_num):
    global board_rect
    not_clicked = True
    if tile[tile_num] != [0,0,0]:
        color = 'black' if tile[tile_num][1].islower() else 'white'
        while not_clicked:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:        
                    # Check if the mouse is clicked inside the rectangle
                    if color == 'black':
                        if black_queen_rect.collidepoint(event.pos):
                            # Remove the rectangle by not drawing it on the next frame
                            background_rect = pygame.Rect(0,0,0,0)
                            return [(Piece().Black|Piece().Queen), 'q', True]
                        elif black_rook_rect.collidepoint(event.pos):
                            # Remove the rectangle by not drawing it on the next frame
                            background_rect = pygame.Rect(0,0,0,0)
                            return [(Piece().Black|Piece().Rook), 'r', True]
                        elif black_bishop_rect.collidepoint(event.pos):
                            # Remove the rectangle by not drawing it on the next frame
                            background_rect = pygame.Rect(0,0,0,0)
                            return [(Piece().Black|Piece().Bishop), 'b', True]
                        elif black_knight_rect.collidepoint(event.pos):
                            # Remove the rectangle by not drawing it on the next frame
                            background_rect = pygame.Rect(0,0,0,0)
                            return [(Piece().Black|Piece().Knight), 'n', 0]
                        
                    elif color == 'white':
                        if white_queen_rect.collidepoint(event.pos):
                            # Remove the rectangle by not drawing it on the next frame
                            background_rect = pygame.Rect(0,0,0,0)
                            return [(Piece().White|Piece().Queen), 'Q', True]
                        elif white_rook_rect.collidepoint(event.pos):
                            # Remove the rectangle by not drawing it on the next frame
                            background_rect = pygame.Rect(0,0,0,0)
                            return [(Piece().White|Piece().Rook), 'R', True]
                        elif white_bishop_rect.collidepoint(event.pos):
                            # Remove the rectangle by not drawing it on the next frame
                            background_rect = pygame.Rect(0,0,0,0)
                            return [(Piece().White|Piece().Bishop), 'B', True]
                        elif white_knight_rect.collidepoint(event.pos):
                            # Remove the rectangle by not drawing it on the next frame
                            background_rect = pygame.Rect(0,0,0,0)
                            return [(Piece().White|Piece().Knight), 'N', 0]
                        
            if color == 'black':
                black_queen_image = pygame.transform.scale(black_queen, (int(board_rect.width/8)+25, int(board_rect.height/8)+25))
                black_rook_image = pygame.transform.scale(black_rook, (int(board_rect.width/8)+25, int(board_rect.height/8)+25))
                black_bishop_image = pygame.transform.scale(black_bishop, (int(board_rect.width/8)+25, int(board_rect.height/8)+25))
                black_knight_image = pygame.transform.scale(black_knight, (int(board_rect.width/8)+25, int(board_rect.height/8)+25))

                if player_color == 'black':
                    black_queen_image = pygame.transform.flip(black_queen_image, False, True)
                    black_rook_image = pygame.transform.flip(black_rook_image, False, True)
                    black_bishop_image = pygame.transform.flip(black_bishop_image, False, True)
                    black_knight_image = pygame.transform.flip(black_knight_image, False, True)

                black_queen_rect = black_queen_image.get_rect()
                black_queen_rect.center = (screen_width/2-150, screen_height/2-50)

                black_bishop_rect = black_bishop_image.get_rect()
                black_bishop_rect.center = (screen_width/2-50, screen_height/2-50)

                black_rook_rect = black_rook_image.get_rect()
                black_rook_rect.center = (screen_width/2+50, screen_height/2-50)

                black_knight_rect = black_knight_image.get_rect()
                black_knight_rect.center = (screen_width/2+150, screen_height/2-50)

                background_rect = pygame.Rect(screen_width/2-200, screen_height/2-100, 400, 100)
                pygame.draw.rect(screen, dark_brown, background_rect)
                
                
                screen.blit(black_queen_image, black_queen_rect)
                screen.blit(black_rook_image, black_rook_rect)
                screen.blit(black_bishop_image, black_bishop_rect)
                screen.blit(black_knight_image, black_knight_rect)

                pygame.display.update()

            elif color == 'white':
                white_queen_image = pygame.transform.scale(white_queen, (int(board_rect.width/8)+25, int(board_rect.height/8)+25))
                white_rook_image = pygame.transform.scale(white_rook, (int(board_rect.width/8)+25, int(board_rect.height/8)+25))
                white_bishop_image = pygame.transform.scale(white_bishop, (int(board_rect.width/8)+25, int(board_rect.height/8)+25))
                white_knight_image = pygame.transform.scale(white_knight, (int(board_rect.width/8)+25, int(board_rect.height/8)+25))
            

                if player_color == 'black':
                    white_queen_image = pygame.transform.flip(white_queen_image, False, True)
                    white_rook_image = pygame.transform.flip(white_rook_image, False, True)
                    white_bishop_image = pygame.transform.flip(white_bishop_image, False, True)
                    white_knight_image = pygame.transform.flip(white_knight_image, False, True)


                white_queen_rect = white_queen_image.get_rect()
                white_queen_rect.center = (screen_width/2-150, screen_height/2-50)

                white_bishop_rect = white_bishop_image.get_rect()
                white_bishop_rect.center = (screen_width/2-50, screen_height/2-50)

                white_rook_rect = white_rook_image.get_rect()
                white_rook_rect.center = (screen_width/2+50, screen_height/2-50)

                white_knight_rect = white_knight_image.get_rect()
                white_knight_rect.center = (screen_width/2+150, screen_height/2-50)

                background_rect = pygame.Rect(screen_width/2-200, screen_height/2-100, 400, 100)
                pygame.draw.rect(screen, dark_brown, background_rect)

                screen.blit(white_queen_image, white_queen_rect)
                screen.blit(white_rook_image, white_rook_rect)
                screen.blit(white_bishop_image, white_bishop_rect)
                screen.blit(white_knight_image, white_knight_rect)

                pygame.display.update()

def create_player_color_button():
    global player_color_button_shade, player_color, player_text, player_text_rect
    player_color_button_shade = pygame.Rect(screen_width/11, screen_height/8, 140, 55)
    player_color_button = pygame.Rect(screen_width/11, screen_height/8, 130, 45)
    pygame.draw.rect(screen, (0, 0, 0), player_color_button_shade)
    pygame.draw.rect(screen, gray, player_color_button)
    font = pygame.font.Font('ConsolaMono-Bold.ttf', 16)
    if player_color == 'white':
        player_text = font.render('Play As Black', True, (0,0,0))
    elif player_color == 'black':
        player_text = font.render('Play As White', True, (0,0,0))
    
    player_text_rect = player_text.get_rect()
    player_text_rect.center=player_color_button.center
    screen.blit(player_text, player_text_rect)

def update_player_color_button():
    global player_text, player_text_rect
    player_color_button_shade = pygame.Rect(screen_width/11, screen_height/8, 130, 45)
    player_color_button = pygame.Rect(screen_width/11, screen_height/8, 120, 35)
    pygame.draw.rect(screen, (0, 0, 0), player_color_button_shade)
    pygame.draw.rect(screen, gray, player_color_button)

    player_text_rect.center=player_color_button.center
    screen.blit(player_text, player_text_rect)

def create_play_pause_buttons():
    global play_or_pause, play_button, play_or_pause_text_rect, play_or_pause_text, play_button_shade
    play_button_shade = pygame.Rect(screen_width/11, screen_height/4, 140, 55)
    play_button = pygame.Rect(screen_width/11, screen_height/4, 130, 45)   
    pygame.draw.rect(screen, (0,0,0), play_button_shade)
    pygame.draw.rect(screen, gray, play_button)
    font = pygame.font.Font('ConsolaMono-Bold.ttf', 16)
    if play_or_pause == 'pause':
        play_or_pause_text = font.render('Play', True, (0,0,0))
    elif play_or_pause == 'play':
        play_or_pause_text = font.render('Pause', True, (0,0,0))


    play_or_pause_text_rect = play_or_pause_text.get_rect()
    play_or_pause_text_rect.center=play_button.center
    screen.blit(play_or_pause_text, play_or_pause_text_rect)

def update_play_pause_button():
    global play_or_pause_text, play_or_pause_text_rect, play_or_pause
    play_button_shade = pygame.Rect(screen_width/11, screen_height/4, 130, 45)
    play_button = pygame.Rect(screen_width/11, screen_height/4, 120, 35)
    pygame.draw.rect(screen, (0,0,0), play_button_shade)
    pygame.draw.rect(screen, gray, play_button)
    play_or_pause_text_rect.center=play_button.center
    screen.blit(play_or_pause_text, play_or_pause_text_rect)

def create_reset_button():
    global reset_button_text, reset_button_text_rect, reset_button_shade
    reset_button_shade = pygame.Rect(screen_width/11, screen_height / 2.65, 140, 55)
    reset_button = pygame.Rect(screen_width/11, screen_height/2.65, 130, 45)
    pygame.draw.rect(screen, (0,0,0), reset_button_shade)
    pygame.draw.rect(screen, gray, reset_button)
    font = pygame.font.Font('ConsolaMono-Bold.ttf', 16)
    reset_button_text = font.render('Reset', True, (0,0,0))
    reset_button_text_rect = reset_button_text.get_rect()
    reset_button_text_rect.center=reset_button.center
    screen.blit(reset_button_text, reset_button_text_rect)

def update_reset_button():
    global reset_button_text, reset_button_text_rect
    reset_button_shade = pygame.Rect(screen_width/11, screen_height/2.65, 130, 45)
    reset_button = pygame.Rect(screen_width/11, screen_height/2.65, 120, 35)
    pygame.draw.rect(screen, (0,0,0), reset_button_shade)
    pygame.draw.rect(screen, gray, reset_button)
    reset_button_text_rect.center=reset_button.center
    screen.blit(reset_button_text, reset_button_text_rect)

def create_play_again_button(winner):
    global play_again_button_text, play_again_button_text_rect, play_again_button_shade

    play_again_button_shade = pygame.Rect(screen_width/2 - 288.888889/2, screen_height / 2 - 50, 298.888889, 110)
    play_again_button = pygame.Rect(screen_width/2 - 288.888889/2, screen_height/2 - 50, 288.888889, 100)
    pygame.draw.rect(screen, (0,0,0), play_again_button_shade)
    pygame.draw.rect(screen, gray, play_again_button)
    font = pygame.font.Font('ConsolaMono-Bold.ttf', 28)
    play_again_button_text = font.render('Play Again', True, (0,0,0))
    play_again_button_text_rect = play_again_button_text.get_rect()
    play_again_button_text_rect.center=play_again_button.center
    screen.blit(play_again_button_text, play_again_button_text_rect)

    other_font = pygame.font.Font('ConsolaMono-Bold.ttf', 32)
    winner_text = other_font.render(winner, True, (10, 10, 10))
    winner_text_rect = winner_text.get_rect()
    winner_text_rect.center = screen_width/2, screen_height/3
    screen.blit(winner_text, winner_text_rect)

def update_play_again_button(winner):
    global play_again_button_text, play_again_button_text_rect, play_again_button_shade

    play_again_button_shade = pygame.Rect(screen_width/2 - 288.888889/2, screen_height / 2 - 50, 288.888889, 100)
    play_again_button = pygame.Rect(screen_width/2 - 288.888889/2, screen_height/2 - 50, 278.888889, 90)
    pygame.draw.rect(screen, (0,0,0), play_again_button_shade)
    pygame.draw.rect(screen, gray, play_again_button)
    font = pygame.font.Font('ConsolaMono-Bold.ttf', 28)
    play_again_button_text = font.render('Play Again', True, (0,0,0))
    play_again_button_text_rect = play_again_button_text.get_rect()
    play_again_button_text_rect.center = play_again_button.center
    screen.blit(play_again_button_text, play_again_button_text_rect)

    other_font = pygame.font.Font('ConsolaMono-Bold.ttf', 32)
    winner_text = other_font.render(winner, True, (10, 10, 10))
    winner_text_rect = winner_text.get_rect()
    winner_text_rect.center = screen_width/2, screen_height/3
    screen.blit(winner_text, winner_text_rect)

def create_play_against_computer_button():
    global computer_button_text, computer_button_text_rect, computer_button_shade, gamemode, computer_button
    computer_button_shade = pygame.Rect(screen_width/11, screen_height / 2, 230, 55)
    computer_button = pygame.Rect(screen_width/11, screen_height/2, 220, 45)
    pygame.draw.rect(screen, (0,0,0), computer_button_shade)
    pygame.draw.rect(screen, gray, computer_button)
    font = pygame.font.Font('ConsolaMono-Bold.ttf', 16)
    if gamemode == 'single_player':
        computer_button_text = font.render('Play Against a Friend', True, (0,0,0))
    elif gamemode == 'two_player':
        computer_button_text = font.render('Play Against a Computer', True, (0,0,0))
    computer_button_text_rect = computer_button_text.get_rect()
    computer_button_text_rect.center=computer_button.center
    screen.blit(computer_button_text, computer_button_text_rect)

def update_play_against_computer_button():
    global computer_button_text, computer_button_text_rect, computer_button_shade, gamemode, computer_button
    computer_button_shade = pygame.Rect(screen_width/11, screen_height / 2, 220, 45)
    computer_button = pygame.Rect(screen_width/11, screen_height/2, 210, 35)
    pygame.draw.rect(screen, (0,0,0), computer_button_shade)
    pygame.draw.rect(screen, gray, computer_button)
    computer_button_text_rect.center=computer_button.center
    screen.blit(computer_button_text, computer_button_text_rect)


def seconds_to_minutes(time):
    seconds = time // 1000
    minutes = seconds//60
    seconds = seconds%60
    return "{:02d}:{:02d}".format(minutes, seconds)   

def create_timers(time1, time2):
    # global white_time_time, black_time_time
    starting_time_1_converted = seconds_to_minutes(time1)
    starting_time_2_converted = seconds_to_minutes(time2)
    font = pygame.font.Font('ConsolaMono-Bold.ttf', 28)
    white_time = font.render(starting_time_1_converted, True, (255, 255, 255))
    white_time_rect = white_time.get_rect()

    black_time = font.render(starting_time_2_converted, True, (255, 255, 255))
    black_time_rect = black_time.get_rect()
    if player_color == 'white':
        white_time_rect.center = (screen_width/2, screen_height-60)
        black_time_rect.center = (screen_width/2, screen_height/12)
    elif player_color == 'black':
        white_time_rect.center = (screen_width/2, screen_height/12)
        black_time_rect.center = (screen_width/2, screen_height-60)

    screen.blit(white_time, white_time_rect)
    screen.blit(black_time, black_time_rect)

def create_username_tag():
    font = pygame.font.Font('ConsolaMono-Bold.ttf', 20)
    kelbwah = font.render('@kelbwah', True, (255, 255, 255))
    kelbwah_rect = kelbwah.get_rect()
    kelbwah_rect.center = (screen_width - 100, screen_height-35)
    screen.blit(kelbwah, kelbwah_rect)

def set_turn(new_turn):
    global turn
    turn = new_turn

def reset_halfmove():
    global halfmove_count
    halfmove_count = 0

def reset_fullmove():
    global fullmove_count
    fullmove_count = 1

def reset_tile():
    global tile
    tile = [[19, 'r', True], [22, 'n', 0], [20, 'b', True], [18, 'q', True], [17, 'k', 0], [20, 'b', True], [22, 'n', 0], [19, 'r', True], [21, 'p', 0], [21, 'p', 0], [21, 'p', 0], [21, 'p', 0], [21, 'p', 0], [21, 'p', 0], [21, 'p', 0], 
            [21, 'p', 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], 
            [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [13, 'P', 0], [13, 'P', 0], [13, 'P', 0], [13, 'P', 0], [13, 'P', 0], [13, 'P', 0], 
            [13, 'P', 0], [13, 'P', 0], [11, 'R', True], [14, 'N', 0], [12, 'B', True], [10, 'Q', True], [9, 'K', 0], [12, 'B', True], [14, 'N', 0], [11, 'R', True]]

"""This function will check if a piece is in checkmate"""
def determine_game_over():
    global game_over_sound_heard
    if halfmove_count == 50:
        if game_over_sound_heard == False:
            play_sound_threaded(6)
            game_over_sound_heard = True
        return 'Draw'
    elif white_player_time <= 0:
        if game_over_sound_heard == False:
            play_sound_threaded(7)
            game_over_sound_heard = True
        return 'Black Wins by Time!'
    elif black_player_time <= 0:
        if game_over_sound_heard == False:
            play_sound_threaded(7)
            game_over_sound_heard = True
        return 'White Wins by Time!'
    elif dragging == False:
        #Checking if there are only kings left in the game and returning draw
        still_pieces = False
        for piece in tile:
            if piece != [0,0,0] and piece[1].lower() != 'k':
                still_pieces = True
        if still_pieces == False:
            if game_over_sound_heard == False:
                play_sound_threaded(6)
                game_over_sound_heard = True
            return 'Draw'
        
        #Analyzing checkmate
        if king_in_check() != None and king_in_check()[0] == 'white': #Checking if white is in checkmate
            still_possible_moves = False
            for i in range(64):
                if tile[i] != [0,0,0] and tile[i][1].isupper():
                    piece_move = generate_moves(i, tile[i][1])
                    if piece_move != []:
                        still_possible_moves = True
                        break
            if still_possible_moves == False:
                if game_over_sound_heard == False:
                    play_sound_threaded(5)
                    game_over_sound_heard = True
                return 'Black Wins by Checkmate'
        elif king_in_check() != None and king_in_check()[0] == 'black': #Checking if white is in checkmate
            still_possible_moves = False
            for i in range(64):
                if tile[i] != [0,0,0] and tile[i][1].islower():
                    piece_move = generate_moves(i, tile[i][1])
                    if piece_move != []:
                        still_possible_moves = True
                        break
            if still_possible_moves == False:
                if game_over_sound_heard == False:
                    play_sound_threaded(5)
                    game_over_sound_heard = True
                return 'White Wins by Checkmate'
        
        #Analyzing stalemate positions
        if king_in_check() == None:
            still_possible_moves = False

            for i in range(64):
                if tile[i] != [0,0,0] and ((tile[i][1].islower() and turn == 'b') or (tile[i][1].isupper() and turn == 'w')):
                    piece_move = generate_moves(i, tile[i][1])
                    if piece_move != []:
                        still_possible_moves = True
                        break
            if still_possible_moves == False:
                if game_over_sound_heard == False:
                    play_sound_threaded(6)
                    game_over_sound_heard = True
                return 'Draw by Stalemate'
            
    return None

def get_computer_move(fen_position):
    global white_player_time, black_player_time, random_time
    board = chess.Board(fen_position)
    random_time = random.randint(1,3)
    result = engine.play(board, chess.engine.Limit(time=random_time))
    best_move = str(result.move)
    best_move_1 = best_move[:2]
    best_move_2 = best_move[2:]
    best_move_1_tile = tiles_inverted[best_move_1]
    best_move_2_tile = tiles_inverted[best_move_2]


    return best_move_1_tile, best_move_2_tile


def computer_move():
    global play_or_pause, valid_move, first_move
    if (play_or_pause == 'play' and valid_move == True and first_move == False) or (play_or_pause == 'play' and valid_move == False and first_move == True):
        valid_move = False
        if turn != player_color[0] and gamemode == 'single_player':
            best_move_1, best_move_2 = get_computer_move(fen_position)
            print(best_move_1, best_move_2)
            if tile[best_move_1][1].lower() == 'p':

                tile[best_move_2] = tile[best_move_1]
                tile[best_move_1] = [0,0,0]
                play_sound_threaded(1)
                if turn == 'black':
                    update_halfmove('pawn_move')
                    update_fullmove()
                elif turn == 'white':
                    update_halfmove('pawn_move')
            elif tile[best_move_2] != [0,0,0]:
                tile[best_move_2] = tile[best_move_1]
                tile[best_move_1] = [0,0,0]
                play_sound_threaded(2)
                if turn == 'black':
                    update_halfmove('capture')
                    update_fullmove()
                elif turn == 'white':
                    update_halfmove('capture')
            else:
                tile[best_move_2] = tile[best_move_1]
                tile[best_move_1] = [0,0,0]
                play_sound_threaded(1)
                if turn == 'black':
                    update_halfmove('regular_move')
                    update_fullmove()
                elif turn == 'white':
                    update_halfmove('regular_move')
            
            change_turn()
            update_castling()
            update_fen()


# Create a threading.Event object to signal when the computer move is ready
move_ready = threading.Event()


# Define a function that wraps the computer_move() function and sets the move_ready event
def computer_move_wrapper():
    computer_move()
    move_ready.set()

    


#-----------------------------------------------------------------------------------------------------------------------------------------------------------

"""This is the main game engine that loads the pieces and handles the game logic"""
def main():
    global board_rect, player_color_button_shade, player_color, white_king, black_king, white_bishop, black_bishop, white_pawn, black_pawn, white_knight, black_knight, white_queen, black_queen, white_rook, black_rook
    global play_button, play_button_shade, play_or_pause, reset_button_shade, player_color, tile, turn, white_player_time, black_player_time, dragging, game_over_sound_heard, gamemode, valid_move, first_move, random_time
    selected_piece = None
    dropped_tile = None
    dragging = False
    piece_under_mouse = None
    tile_num = None
    original_tile = None
    moves = []
    pressed_button_1 = False
    pressed_button_2 = False
    pressed_button_3 = False
    previous_move_tile = None
    new_move_tile = None
    play_again_button_pressed = False
    play_against_computer_button_pressed = False
    white_player_time = 5000 #5 minutes
    black_player_time = 5000 #5 mintues
    valid_move = False
    first_move = True
    TIMER_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(TIMER_EVENT, 1000)
    computer_thread = None
    random_time = 1 #Just for the edge case that random time isn't defined due to threading
    while True:
        #Making sure that the mouse's position doesn't get recorded outside the window
        if get_square_under_mouse() < 64:
            piece_under_mouse, tile_num = tile[get_square_under_mouse()], get_square_under_mouse()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #Closes the screen if user exits the window
                print(fen_position)
                engine.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN: #Checking whether the user pressed down
                if determine_game_over() == None and pygame.mouse.get_pos()[0] >= player_color_button_shade.left and pygame.mouse.get_pos()[0] <= player_color_button_shade.right and pygame.mouse.get_pos()[1] >= player_color_button_shade.top and pygame.mouse.get_pos()[1] <= player_color_button_shade.bottom:
                    pressed_button_1 = True
                    update_player_color_button()
                if determine_game_over() == None and pygame.mouse.get_pos()[0] >= play_button_shade.left and pygame.mouse.get_pos()[0] <= play_button_shade.right and pygame.mouse.get_pos()[1] >= play_button_shade.top and pygame.mouse.get_pos()[1] <= play_button_shade.bottom:
                    pressed_button_2 = True
                    update_play_pause_button()
                if determine_game_over() == None and pygame.mouse.get_pos()[0] >= reset_button_shade.left and pygame.mouse.get_pos()[0] <= reset_button_shade.right and pygame.mouse.get_pos()[1] >= reset_button_shade.top and pygame.mouse.get_pos()[1] <= reset_button_shade.bottom:
                    pressed_button_3 = True
                    update_reset_button()
                if determine_game_over() != None and pygame.mouse.get_pos()[0] >= play_again_button_shade.left and pygame.mouse.get_pos()[0] <= play_again_button_shade.right and pygame.mouse.get_pos()[1] >= play_again_button_shade.top and pygame.mouse.get_pos()[1] <= play_again_button_shade.bottom:
                    play_again_button_pressed = True
                    update_play_again_button(determine_game_over())
                if determine_game_over() == None and play_or_pause == 'pause' and pygame.mouse.get_pos()[0] >= computer_button_shade.left and pygame.mouse.get_pos()[0] <= computer_button_shade.right and pygame.mouse.get_pos()[1] >= computer_button_shade.top and pygame.mouse.get_pos()[1] <= computer_button_shade.bottom:
                    play_against_computer_button_pressed = True
                if determine_game_over() == None and piece_under_mouse != [0,0,0] and (pygame.mouse.get_pos()[0] >= board_rect.left and pygame.mouse.get_pos()[0] <= board_rect.right and pygame.mouse.get_pos()[1] >= board_rect.top and pygame.mouse.get_pos()[1] <= board_rect.bottom) and play_or_pause == 'play': #If the mouse actually clicked a piece, it will then record that piece and set the dragging state to true
                    selected_piece = piece_under_mouse, tile_num
                    dragging = True
                    original_tile = tile_num
                    previous_move_tile = tile_num
                    moves = generate_moves(selected_piece[1], selected_piece[0][1]) #Starts to generate moves for the clicked piece
                    tile[tile_num] = [0,0,0] #This sets the current tile that the mouse clicked on to 0, so that it deletes it from the board
                    update_fen() #This updates the FEN string so that when the piece gets clicked on, it is also deleted from the fen string and the screen itself
            elif event.type == pygame.MOUSEBUTTONUP: #Checking whether the user let go of the mouse button
                if determine_game_over() == None and pygame.mouse.get_pos()[0] >= player_color_button_shade.left and pygame.mouse.get_pos()[0] <= player_color_button_shade.right and pygame.mouse.get_pos()[1] >= player_color_button_shade.top and pygame.mouse.get_pos()[1] <= player_color_button_shade.bottom:
                    pressed_button_1 = False
                    """DO SOMETHING HERE!"""
                    player_color = 'black' if player_color == 'white' else 'white'
                    if player_color == 'black' or player_color == 'white':
                        white_king, black_king = pygame.transform.flip(white_king, True, True), pygame.transform.flip(black_king, True, True)
                        white_queen, black_queen = pygame.transform.flip(white_queen, True, True), pygame.transform.flip(black_queen, True, True)
                        white_rook, black_rook = pygame.transform.flip(white_rook, True, True), pygame.transform.flip(black_rook, True, True)
                        white_bishop, black_bishop = pygame.transform.flip(white_bishop, True, True), pygame.transform.flip(black_bishop, True, True)
                        white_pawn, black_pawn = pygame.transform.flip(white_pawn, True, True), pygame.transform.flip(black_pawn, True, True)
                        white_knight, black_knight = pygame.transform.flip(white_knight, True, True), pygame.transform.flip(black_knight, True, True)                         
                if determine_game_over() == None and pygame.mouse.get_pos()[0] >= play_button_shade.left and pygame.mouse.get_pos()[0] <= play_button_shade.right and pygame.mouse.get_pos()[1] >= play_button_shade.top and pygame.mouse.get_pos()[1] <= play_button_shade.bottom:
                    play_or_pause = 'pause' if play_or_pause == 'play' else 'play'
                    if play_or_pause == 'play':
                        play_sound_threaded(0)
                    pressed_button_2 = False
                if determine_game_over() == None and pygame.mouse.get_pos()[0] >= reset_button_shade.left and pygame.mouse.get_pos()[0] <= reset_button_shade.right and pygame.mouse.get_pos()[1] >= reset_button_shade.top and pygame.mouse.get_pos()[1] <= reset_button_shade.bottom:
                    reset_tile()
                    update_en_passant('-')
                    set_turn('w')
                    change_fen(original_fen_position)
                    reset_fullmove()
                    reset_halfmove()
                    white_player_time = 300000
                    black_player_time = 300000
                    
                    play_or_pause = 'pause'
                    pressed_button_3 = False
                    previous_move_tile = None
                    new_move_tile = None
                    first_move = True
                    valid_move = False
                    if computer_thread:
                        # Stop the computer move thread
                        computer_thread.join()
                        # Recreate and start the thread for the computer move
                        computer_thread = threading.Thread(target=computer_move_wrapper)
                        computer_thread.start()
                if determine_game_over() == None and play_or_pause == 'pause' and pygame.mouse.get_pos()[0] >= computer_button_shade.left and pygame.mouse.get_pos()[0] <= computer_button_shade.right and pygame.mouse.get_pos()[1] >= computer_button_shade.top and pygame.mouse.get_pos()[1] <= computer_button_shade.bottom:
                    play_against_computer_button_pressed = False
                    gamemode = 'two_player' if gamemode == 'single_player' else 'single_player'
                    update_play_against_computer_button()

                if determine_game_over() != None and pygame.mouse.get_pos()[0] >= play_again_button_shade.left and pygame.mouse.get_pos()[0] <= play_again_button_shade.right and pygame.mouse.get_pos()[1] >= play_again_button_shade.top and pygame.mouse.get_pos()[1] <= play_again_button_shade.bottom:
                    reset_tile()
                    update_en_passant('-')
                    set_turn('w')
                    change_fen(original_fen_position)
                    reset_fullmove()
                    reset_halfmove()
                    white_player_time = 300000
                    black_player_time = 300000
                    play_or_pause = 'pause'
                    pressed_button_3 = False
                    previous_move_tile = None
                    new_move_tile = None
                    game_over_sound_heard = False
                    first_move = True
                    valid_move = False
                    
                    # Stop the computer move thread
                    computer_thread.join()

                    # Recreate and start the thread for the computer move
                    computer_thread = threading.Thread(target=computer_move_wrapper)
                    computer_thread.start()


                #Before this event even starts, the function drag() is called and actually gives back the position in which the user decided to place the piece
                if determine_game_over() == None and dropped_tile != None and selected_piece != None and dragging and dropped_tile[0] in moves and play_or_pause == 'play': 
                    valid_move = True
                    if first_move == True:
                        first_move = False
                    if tile[dropped_tile[0]] == [0,0,0]: # playing move sound
                        play_sound_threaded(1)
                    elif tile[dropped_tile[0]] != [0,0,0]: # playing takes sound
                        play_sound_threaded(2)
                    if dropped_tile[1][1] == 'K' and (dropped_tile[0] == 58 or dropped_tile[0] == 62):
                        if dropped_tile[0] == 58 and 'Q' in castle: # Castling queen side for white
                            # Changing the king's position
                            previous_tile = original_tile
                            new_tile = dropped_tile[0]
                            new_move_tile = new_tile
                            tile[previous_tile] = [0,0,0]
                            tile[new_tile] = dropped_tile[1]

                            # Changing the rook's position
                            previous_rook_tile = tile[56]
                            new_rook_tile_num = 59
                            tile[56] = [0,0,0]
                            tile[new_rook_tile_num] = previous_rook_tile
                            play_sound_threaded(4)
                            update_en_passant('-')
                            update_halfmove('regular_move')
                        elif dropped_tile[0] == 62 and 'K' in castle: # Castling king side for white
                            # Changing the king's position
                            previous_tile = tile_num
                            new_tile = dropped_tile[0]
                            new_move_tile = new_tile
                            tile[previous_tile] = [0,0,0]
                            tile[new_tile] = dropped_tile[1]

                            # Changing the rook's position
                            previous_rook_tile = tile[63]
                            new_rook_tile_num = 61
                            tile[63] = [0,0,0]
                            tile[new_rook_tile_num] = previous_rook_tile
                            play_sound_threaded(4)
                            update_en_passant('-')
                            update_halfmove('regular_move')
                        else:
                            update_en_passant('-')
                            previous_tile = original_tile
                            
                            new_tile = dropped_tile[0]
                            new_move_tile = new_tile
                            #Then sets the previous position as None and the new position as the dropped piece
                            tile[previous_tile] = [0,0,0]
                            tile[new_tile] = dropped_tile[1] #The simpler version is tile[new_tile] = selected_piece                   
                    elif dropped_tile[1][1] == 'k' and (dropped_tile[0] == 2 or dropped_tile[0] == 6):
                        if dropped_tile[0] == 2 and 'q' in castle: # Castling queen side for black
                            # Changing the king's position
                            previous_tile = original_tile
                            new_tile = dropped_tile[0]
                            new_move_tile = new_tile
                            tile[previous_tile] = [0,0,0]
                            tile[new_tile] = dropped_tile[1]
                            
                            # Changing the rook's position
                            previous_rook_tile = tile[0]
                            new_rook_tile_num = 3
                            tile[0] = [0,0,0]
                            tile[new_rook_tile_num] = previous_rook_tile
                            play_sound_threaded(4)
                            update_fullmove()
                            update_halfmove('regular_move')
                        elif dropped_tile[0] == 6 and 'k' in castle: # Castling king side for black
                            # Changing the king's position
                            previous_tile = tile_num
                            new_tile = dropped_tile[0]
                            new_move_tile = new_tile
                            tile[previous_tile] = [0,0,0]
                            tile[new_tile] = dropped_tile[1]

                            # Changing the rook's position
                            previous_rook_tile = tile[7]
                            new_rook_tile_num = 5
                            tile[7] = [0,0,0]
                            tile[new_rook_tile_num] = previous_rook_tile
                            play_sound_threaded(4)
                            update_fullmove()
                            update_halfmove('regular_move')
                        else:
                            update_en_passant('-')
                            previous_tile = original_tile
                            
                            new_tile = dropped_tile[0]
                            new_move_tile = new_tile
                            #Then sets the previous position as None and the new position as the dropped piece
                            tile[previous_tile] = [0,0,0]
                            tile[new_tile] = dropped_tile[1] #The simpler version is tile[new_tile] = selected_piece             
                    elif dropped_tile[1][1].lower() == 'p' and (dropped_tile[0]//8 == 0 or dropped_tile[0]//8 == 7):
                        color = 'black' if dropped_tile[1][1].islower() else 'white'
                        update_en_passant('-')
                        previous_tile = original_tile

                        new_tile = dropped_tile[0]

                        if color == 'black':
                            update_fullmove()
                            if tile[new_tile] != [0,0,0]:
                                update_halfmove('pawn_move')
                        elif color == 'white':
                            if tile[new_tile] != [0,0,0]:
                                update_halfmove('pawn_move')

                        new_move_tile = new_tile
                        #Then sets the previous position as None and the new position as the dropped piece
                        tile[previous_tile] = [0,0,0]
                        tile[new_tile] = dropped_tile[1]
                        tile_values = promote_pawn(dropped_tile[0])
                        tile[new_tile] = tile_values                   
                    elif (dropped_tile[1][1] == 'P' and dropped_tile[0]//8 == 4 and original_tile//8 == 6) or (dropped_tile[1][1] == 'p' and dropped_tile[0]//8 == 3 and original_tile//8 == 1):
                        color = 'black' if dropped_tile[1][1].islower() else 'white'
                        if color == 'black':
                            update_fullmove()
                            update_halfmove('pawn_move')
                            play_sound_threaded(1)
                        elif color == 'white':
                            update_halfmove('pawn_move')
                            play_sound_threaded(1)

                        current_en_passant = tiles_white[dropped_tile[0]]
                        update_en_passant(current_en_passant)
                        previous_tile = original_tile
                        new_tile = dropped_tile[0]
                        new_move_tile = new_tile
                        #Then sets the previous position as None and the new position as the dropped piece
                        tile[previous_tile] = [0,0,0]
                        tile[new_tile] = dropped_tile[1]                    
                    elif (dropped_tile[1][1].lower() == 'p' and en_passant != '-' and (dropped_tile[0] == (en_passant_tile - 8) or dropped_tile[0] == (en_passant_tile + 8))): # Generating en passant move
                        if en_passant_tile_color == 'black' and dropped_tile[0] == (en_passant_tile - 8) or en_passant_tile_color == 'white' and dropped_tile[0] == (en_passant_tile + 8):
                            previous_tile = original_tile
                            new_tile = dropped_tile[0]
                            new_move_tile = new_tile
                            #Then sets the previous position as None and the new position as the dropped piece
                            tile[previous_tile] = [0,0,0]
                            tile[new_tile] = dropped_tile[1]
                            print(en_passant_tile)
                            tile[en_passant_tile] = [0,0,0]
                            update_en_passant('-')
                            if color == 'black':
                                update_fullmove()
                                update_halfmove('pawn_move')
                            elif color == 'white':
                                update_halfmove('pawn_move')
                        else:
                            #Keeping track of old and new positions of dropped piece
                            update_en_passant('-')
                            previous_tile = original_tile
                            
                            new_tile = dropped_tile[0]
                            new_move_tile = new_tile
                            #Then sets the previous position as None and the new position as the dropped piece
                            tile[previous_tile] = [0,0,0]
                            tile[new_tile] = dropped_tile[1] #The simpler version is tile[new_tile] = selected_piece                
                    else:
                        #Keeping track of old and new positions of dropped piece
                        update_en_passant('-')
                        previous_tile = original_tile
                        new_tile = dropped_tile[0]
                        color = 'black' if dropped_tile[1][1].islower() else 'white'
                        if tile[dropped_tile[0]] == [0,0,0] and dropped_tile[1][1].lower() != 'p':
                            if color == 'black':
                                update_fullmove()
                                update_halfmove('regular_move')
                            elif color == 'white':
                                update_halfmove('regular_move')
                        elif tile[dropped_tile[0]] != [0,0,0]:
                            if color == 'black':
                                update_fullmove()
                                update_halfmove('capture')
                            elif color == 'white':
                                update_halfmove('capture')
                        elif dropped_tile[1][1].lower() == 'p':
                            if color == 'black':
                                update_fullmove()
                                update_halfmove('pawn_move')
                            elif color == 'white':
                                update_halfmove('pawn_move')

                        new_move_tile = new_tile
                        #Then sets the previous position as None and the new position as the dropped piece
                        tile[previous_tile] = [0,0,0]
                        tile[new_tile] = dropped_tile[1] #The simpler version is tile[new_tile] = selected_piece
                    
                    if king_in_check() != None:
                        play_sound_threaded(3)

                    change_turn() #Updates the turn
                    update_castling()
                    update_fen() #Updates the FEN string to blit the correct images

                elif determine_game_over() == None and dropped_tile != None and selected_piece != None and dragging and dropped_tile[0] not in moves and play_or_pause == 'play':
                    print('move not allowed')
                    tile[original_tile] = selected_piece[0]
                    update_fen()
                
                pressed_button_1 = False
                pressed_button_2 = False
                pressed_button_3 = False
                play_again_button_pressed = False
                play_against_computer_button_pressed = False
                #This then resets the whole dragging state and sets the dragging, selected_piece, and dropped_tile to False/None
                dragging = False
                selected_piece = None
                dropped_tile = None 
                moves = []
                tile_num = None
                original_tile = None

            elif event.type == TIMER_EVENT:
                if turn == 'w' and play_or_pause == 'play':
                    white_player_time-=1000
                elif turn == 'b' and play_or_pause == 'play':
                    black_player_time-=1000
                else:
                    white_player_time = white_player_time
                    black_player_time = black_player_time

        screen.fill(black)
        create_username_tag()
        create_timers(white_player_time, black_player_time)

        #Adding in the player_color button
        if pressed_button_1==True:
            update_player_color_button()
        elif pressed_button_1 == False:
            create_player_color_button()

        #Adding in a play and pause button
        if pressed_button_2 == True:
            update_play_pause_button()
        elif pressed_button_2 == False:
            create_play_pause_buttons()
        if pressed_button_3 == True:
            update_reset_button()
        elif pressed_button_3 == False:
            create_reset_button()
        if play_against_computer_button_pressed == True:
            update_play_against_computer_button()
        elif play_against_computer_button_pressed == False:
            create_play_against_computer_button()
        draw_tiles(screen, previous_move_tile, new_move_tile, moves)
        load_from_FEN()
        if determine_game_over() != None:
            if player_color == 'white':
                blurred_surface = pygame.transform.gaussian_blur(board_surface, 10, True)
                screen.blit(blurred_surface, (screen_width/2-board_surface.get_width()/2,screen_height/2-board_surface.get_height()/2))
            elif player_color == 'black':
                blurred_surface = pygame.transform.gaussian_blur(board_surface, 10, True)
                blurred_surface = pygame.transform.flip(blurred_surface, True, True)
                screen.blit(blurred_surface, (screen_width/2-board_surface.get_width()/2,screen_height/2-board_surface.get_height()/2))
            if white_player_time != 300000 and black_player_time != 300000 and play_or_pause == 'play':
                play_or_pause = 'pause'
            if play_again_button_pressed == False:
                create_play_again_button(determine_game_over())
            elif play_again_button_pressed == True:
                update_play_again_button(determine_game_over())

        if determine_game_over() == None:
            if player_color == 'black':
                inverted_surface = pygame.transform.flip(board_surface, True, True)
                # Blit the inverted surface onto the screen surface
                screen.blit(inverted_surface, board_rect.topleft)

        #It will only call the drag function if dragging = True and that a piece was selected
        if dragging and selected_piece:
            dropped_tile = drag(selected_piece[0])

        pygame.display.flip() #Update the screen


        clock.tick(60)
        if turn != player_color[0]:
            computer_thread = threading.Thread(target=computer_move_wrapper)
            computer_thread.start()
            move_ready.wait(timeout=random_time)
            move_ready.clear()

if __name__ == '__main__':
    draw_tiles(screen, None, None, None)
    main()
