from pieces import *


class GameData:
    """
    Main data class for game.
    """

    def __init__(self, game):
        """
        Initialization of various data attributes. Notably there are 2 types of move banks.
        "black/white attacking" is a move bank that includes attacking cells where ally pieces exist
        as a means to evaluate protected cells. This is used in checking if a king can safely take a piece
        without accidentally self-checking via another piece.
        "verified black/white moves" is the actual list of cells that any piece can move on a turn. This is
        used to see if any moves are available for a player and, if none are, is the way checkmate is determined.
        :param game: 
        """
        self.selected_piece = None
        self.occupied_cells = []
        self.highlighted_cells = []
        self.black_attacking = []
        self.white_attacking = []
        self.verified_black_moves = []
        self.verified_white_moves = []
        self.passant = None
        self.passant_pawn = None
        self.black_king = None  # special pointers to black and white kings
        self.white_king = None
        self.turn_order = True
        self.turn = 'White'
        self.winner = None
        self.game = game

    @property
    def black_attacking(self):
        """
        Returns black attacking data.
        :return:
        """
        return self._black_attacking

    @black_attacking.setter
    def black_attacking(self, cell):
        """
        Adds cell as being attacked by at least 1 black piece.
        :param cell: tuple
        :return:
        """
        self._black_attacking = cell

    @property
    def white_attacking(self):
        """
        Returns white attacking data.
        :return:
        """
        return self._white_attacking

    @white_attacking.setter
    def white_attacking(self, cell):
        """
        Adds cell as being attacked by at least 1 white piece.
        :param cell: tuple
        :return:
        """
        self._white_attacking = cell

    @property
    def selected_piece(self):
        """
        Returns the currently selected piece.
        :return:
        """
        return self._selected_piece

    @selected_piece.setter
    def selected_piece(self, piece):
        """
        Sets the currently selected piece.
        :return:
        """
        self._selected_piece = piece

    @property
    def occupied_cells(self):
        """
        Returns known occupied cells.
        :return:
        """
        return self._occupied_cells

    @occupied_cells.setter
    def occupied_cells(self, cell):
        """
        Adds cell coord to occupied cell list.
        :param cell: tuple
        :return:
        """
        self._occupied_cells = cell

    @property
    def highlighted_cells(self):
        """
        Returns currently highlighted cells.
        :return:
        """
        return self._highlighted_cells

    @highlighted_cells.setter
    def highlighted_cells(self, move_list):
        """
        Sets highlight for where a piece can move.
        :param move_list:
        :return:
        """
        self._highlighted_cells = move_list

    @property
    def turn_order(self):
        """
        Returns what the turn order flag is set to.
        :return:
        """
        return self._turn_order

    @turn_order.setter
    def turn_order(self, flag):
        """
        Sets the turn order flag.
        :param flag: True / False
        :return:
        """
        self._turn_order = flag

    @property
    def turn(self):
        """
        Returns which player's turn it is.
        :return:
        """
        return self._turn

    @turn.setter
    def turn(self, color):
        """
        Changes turn to given color.
        :param color:
        :return:
        """
        self._turn = color

    def change_turn(self):
        """
        Changes turn upon completion of move.
        :return:
        """
        if self.turn == 'White':
            self.turn = 'Black'
        elif self.turn == 'Black':
            self.turn = 'White'

    @property
    def passant(self):
        """
        Returns passant cell that is targetable.
        :return:
        """
        return self._passant

    @passant.setter
    def passant(self, cell):
        """
        Sets up En Passant information for following turn.
        :param cell: grid location where En Passant is possible
        :return:
        """
        self._passant = cell

    @property
    def passant_pawn(self):
        """
        Returns the pawn at risk from passant.
        :return:
        """
        return self._passant_pawn

    @passant_pawn.setter
    def passant_pawn(self, piece):
        """
        Sets piece at risk of En Passant.
        :param piece: Pawn
        :return:
        """
        self._passant_pawn = piece

    @property
    def black_king(self):
        """
        Returns black king object.
        :return:
        """
        return self._black_king

    @black_king.setter
    def black_king(self, obj):
        """
        Sets black king variable to point at black king object.
        :return:
        """
        self._black_king = obj

    @property
    def white_king(self):
        """
        Returns white king object. If argument given, sets obj as King.
        :return:
        """
        return self._white_king

    @white_king.setter
    def white_king(self, obj):
        """
        Sets white king variable to point at white king object.
        :return:
        """
        self._white_king = obj

    def scan_board(self):
        """
        Clears occupied cells variable and repopulates it with current cells occupied by other pieces.
        :return:
        """
        self.occupied_cells.clear()
        for sprite in self.game.all_sprites:
            self.occupied_cells.append(sprite.cell_location)

    def populate_board(self):
        """
        Places initial pieces on the board, creating piece objects for each of them.
        :return:
        """

        # Back row starting positions
        rooks = [('Black', (0, 0)), ('Black', (7, 0)), ('White', (0, 7)), ('White', (7, 7))]
        knights = [('Black', (1, 0)), ('Black', (6, 0)), ('White', (1, 7)), ('White', (6, 7))]
        bishops = [('Black', (2, 0)), ('Black', (5, 0)), ('White', (2, 7)), ('White', (5, 7))]
        kings = [('Black', (4, 0)), ('White', (4, 7))]
        queens = [('Black', (3, 0)), ('White', (3, 7))]

        for element in rooks:
            piece = Rook(element[0], element[1], 'Rook', self)
            self.game.all_sprites.add(piece)

        for element in knights:
            piece = Knight(element[0], element[1], 'Knight', self)
            self.game.all_sprites.add(piece)

        for element in bishops:
            piece = Bishop(element[0], element[1], 'Bishop', self)
            self.game.all_sprites.add(piece)

        for element in kings:
            piece = King(element[0], element[1], 'King', self)
            self.game.all_sprites.add(piece)

        for element in queens:
            piece = Queen(element[0], element[1], 'Queen', self)
            self.game.all_sprites.add(piece)

        # Pawn starting positions
        for x in range(0, 8):
            b_piece = Pawn('Black', (x, 1), 'Pawn', self)
            w_piece = Pawn('White', (x, 6), 'Pawn', self)
            self.game.all_sprites.add(b_piece)
            self.game.all_sprites.add(w_piece)

    @staticmethod
    def cell_pos(pos):
        """
        Takes a given pixel coordinate on the screen and returns the cell position on the board.
        :param pos: tuple
        :return:
        """
        x, y = pos
        x = (x - X_OFFSET) / TILESIZE
        y = (y - Y_OFFSET) / TILESIZE
        if x < 0 or x > 8 or y < 0 or y > 8:
            return None
        else:
            x, y = int(x), int(y)
            return x, y

    @staticmethod
    def global_pos(cell):
        """
        Opposite of cell_pos method, converts a cell grid position to it's center pixel.
        :param cell: tuple
        :return:
        """
        if cell:  # does not attempt to convert when cell is None
            x, y = cell
            x = x * TILESIZE + X_OFFSET + TILESIZE/2
            y = y * TILESIZE + Y_OFFSET + TILESIZE/2
            return x, y

    @property
    def winner(self):
        """
        Returns the winner of the game.
        :return:
        """
        return self._winner

    @winner.setter
    def winner(self, color):
        """
        Sets the winner to a certain color.
        :param color:
        :return:
        """
        self._winner = color

    @property
    def verified_black_moves(self):
        """
        Verified positions black can move on their turn.
        :return:
        """
        return self._verified_black_moves

    @verified_black_moves.setter
    def verified_black_moves(self, cell):
        """
        List of verified positions at least 1 black piece can move.
        :param cell: tuple
        :return:
        """
        self._verified_black_moves = cell

    @property
    def verified_white_moves(self):
        """
        Verified positions white can move on their turn.
        :return:
        """
        return self._verified_white_moves

    @verified_white_moves.setter
    def verified_white_moves(self, cell):
        """
        List of verified positions at least 1 white piece can move.
        :param cell: tuple
        :return:
        """
        self._verified_white_moves = cell

    def get_piece(self):
        """
        Returns piece located at mouse pos.
        :return:
        """
        pos = pg.mouse.get_pos()
        clicked_sprites = [s for s in self.game.all_sprites if s.rect.collidepoint(pos)]
        if clicked_sprites:
            return clicked_sprites[0]
        else:
            return None

    def get_rect(self):
        """
        Returns the rect located at mouse pos.
        :return:
        """
        pos = pg.mouse.get_pos()
        clicked_rect = [r for r in self.game.ui if r.box.collidepoint(pos)]
        if clicked_rect:
            return clicked_rect[0]
        else:
            return None

    def get_piece_from_coord(self, coord):
        """
        Returns piece object from given Coord. In the event that two pieces occupy the same cell (which
        happens during move simulation), precedence is given to Kings. This fixes an issue with detecting
        check / checkmate.
        :param coord: cell to check, based on grid coords, not pixel coords
        :return: Piece object
        """
        if self.black_king.cell_location == coord:
            return self.black_king
        elif self.white_king.cell_location == coord:
            return self.white_king
        else:
            for sprite in self.game.all_sprites:
                if sprite.cell_location == coord:
                    return sprite

    def find_closest_cell(self, piece):
        """
        Attempts to position dropped piece into nearest cell.
        :param piece:
        :return:
        """
        if piece:
            cell = self.cell_pos(piece.pixel_location)
            global_coord = self.global_pos(cell)
            if global_coord:
                x, y = global_coord
                return x + TILESIZE / 2, y + TILESIZE / 2
            else:
                return piece.previous_pixel

    def update_move_banks(self, exclude=None):
        """
        Cycles through all pieces and updates move banks.
        :param exclude: optional. if given, will exclude that piece from move updates.
        :return:
        """
        self.black_attacking.clear(), self.white_attacking.clear()
        for sprite in self.game.all_sprites:
            if sprite != exclude:
                sprite.move_bank.clear()
                if sprite.cell_location is not None:
                    sprite.update_move_bank()

    def clear_team_move_banks(self):
        """
        Clears verified move banks of teams.
        :return:
        """
        self.verified_white_moves.clear()
        self.verified_black_moves.clear()

    def resolve_attack(self, piece, passant):
        """
        Checks if there is a collision between two chess pieces and resolves it.
        :param piece: piece most recently moved
        :param passant: if to allow passant kills
        :return:
        """
        if piece:
            if passant:
                if piece.color != self.passant_pawn.color:
                    self.passant_pawn.kill()
            for sprite in self.game.all_sprites:
                if sprite is not piece:
                    if sprite.pixel_location == piece.pixel_location:
                        if sprite.color != piece.color:
                            sprite.kill()
                        else:
                            piece.pixel_location = piece.previous_pixel

    def evaluate_check(self, king):
        """
        Evaluates if king is currently in check. Sets the check flag when needed.
        :param king: king piece being evaluated
        :return: True if a check is in effect
        """
        if king.color == 'Black':
            if king.cell_location in self.white_attacking:
                return True
        elif king.color == 'White':
            if king.cell_location in self.black_attacking:
                return True
        return False

    def mate_check(self):
        """
        Evaluates if check mate exists and sets winner.
        :return:
        """
        if not self.verified_black_moves:
            self.winner = 'White'
        if not self.verified_white_moves:
            self.winner = 'Black'
