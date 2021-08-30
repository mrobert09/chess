from pieces import *

class GameData:
    """
    Main data class for game.
    """

    def __init__(self, game):
        self._board = None
        self._selected_piece = None
        self._occupied_cells = []
        self._highlighted_cells = []
        self._black_attacking = []
        self._white_attacking = []
        self._black_moves = []
        self._white_moves = []
        self._passant = None
        self._passant_pawn = None
        self._black_king = None  # special pointers to black and white kings
        self._white_king = None
        self._winner = None
        self._game = game

    def add_black_bank(self, cell):
        """
        Adds cell as being attacked by at least 1 black piece.
        :param cell: tuple
        :return:
        """
        self._black_attacking.append(cell)

    def get_black_bank(self):
        """
        Returns black attacking data.
        :return:
        """
        return self._black_attacking

    def add_white_bank(self, cell):
        """
        Adds cell as being attacked by at least 1 white piece.
        :param cell: tuple
        :return:
        """
        self._white_attacking.append(cell)

    def get_white_bank(self):
        """
        Returns white attacking data.
        :return:
        """
        return self._white_attacking

    def clear_attacking_banks(self):
        """
        Clears both colors attacking data.
        :return:
        """
        self._black_attacking = []
        self._white_attacking = []

    def get_selected_piece(self):
        """
        Returns the currently selected piece.
        :return:
        """
        return self._selected_piece

    def set_selected_piece(self, piece):
        """
        Sets the currently selected piece.
        :return:
        """
        self._selected_piece = piece

    def get_occupied(self):
        return self._occupied_cells

    def add_occupied(self, cell):
        """
        Adds cell coord to occupied cell list.
        :param cell: tuple
        :return:
        """
        self._occupied_cells.append(cell)

    def remove_occupied(self, cell):
        """
        Removes cell coord to occupied cell list.
        :param cell: tuple
        :return:
        """
        self._occupied_cells.remove(cell)

    def set_highlights(self, move_list):
        """
        Sets highlight for where a piece can move.
        :param move_list:
        :return:
        """
        self._highlighted_cells = move_list

    def get_highlights(self):
        """
        Returns currently highlighted cells.
        :return:
        """
        return self._highlighted_cells

    def clear_highlights(self):
        """
        Clears currently highlight cells.
        :return:
        """
        self._highlighted_cells = []

    def set_passant(self, cell, piece):
        """
        Sets up En Passant information for following turn.
        :param cell: grid location where En Passant is possible
        :param piece: piece object at risk of En Passant
        :return:
        """
        self._passant = cell
        self._passant_pawn = piece

    def get_passant(self):
        """
        Returns passant cell that is targetable.
        :return:
        """
        return self._passant

    def get_passant_pawn(self):
        """
        Returns the pawn at risk from passant.
        :return:
        """
        return self._passant_pawn

    def clear_passant(self):
        """
        Clear En Passant data. Sets both to None.
        :return:
        """
        self._passant = None
        self._passant_pawn = None

    def black_king(self, obj=None):
        """
        Returns black King object. If argument given, sets obj as King.
        :return:
        """
        if obj:
            self._black_king = obj
        return self._black_king

    def white_king(self, obj=None):
        """
        Returns white King object. If argument given, sets obj as King.
        :return:
        """
        if obj:
            self._white_king = obj
        return self._white_king

    def scan_board(self):
        """
        Clears occupied cells variable and repopulates it with current cells occupied by other pieces.
        :return:
        """
        self._occupied_cells.clear()
        for sprite in self._game.all_sprites:
            self._occupied_cells.append(sprite.get_cell_location())

    def populate_board(self):
        """
        Places initial pieces on the board, creating piece objects for each of them.
        :return:
        """

        # Back row starting positions
        rooks = [('Black', (0, 0)), ('Black', (7, 0)), ('White', (0, 7)), ('White', (7, 7))]
        knights = [('Black', (1, 0)), ('Black', (6, 0)), ('White', (1, 7)), ('White', (6, 7))]
        bishops = [('Black', (2, 0)), ('Black', (5, 0)), ('White', (2, 7)), ('White', (5, 7))]
        kings =  [('Black', (4, 0)), ('White', (4, 7))]
        queens = [('Black', (3, 0)), ('White', (3, 7))]

        for element in rooks:
            piece = Rook(element[0], element[1], self)
            self._game.all_sprites.add(piece)

        for element in knights:
            piece = Knight(element[0], element[1], self)
            self._game.all_sprites.add(piece)

        for element in bishops:
            piece = Bishop(element[0], element[1], self)
            self._game.all_sprites.add(piece)

        for element in kings:
            piece = King(element[0], element[1], self)
            self._game.all_sprites.add(piece)

        for element in queens:
            piece = Queen(element[0], element[1], self)
            self._game.all_sprites.add(piece)

        # Pawn starting positions
        for x in range(0, 8):
            b_piece = Pawn('Black', (x, 1), self)
            w_piece = Pawn('White', (x, 6), self)
            self._game.all_sprites.add(b_piece)
            self._game.all_sprites.add(w_piece)

    def cell_pos(self, pos):
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
            return (x, y)

    def global_pos(self, cell):
        """
        Opposite of cell_pos method, converts a cell grid position to it's center pixel.
        :param cell: tuple
        :return:
        """
        if cell:  # does not attempt to convert when cell is None
            x, y = cell
            x = x * TILESIZE + X_OFFSET + TILESIZE/2
            y = y * TILESIZE + Y_OFFSET + TILESIZE/2
            return (x, y)

    def select_piece(self):
        """
        Selects and deselects cells when clicking. Records which piece is in cell selected.
        :return:
        """
        self.set_selected_piece(self.get_piece())

    def clear_selected_piece(self):
        """
        Sets selected cell to be None.
        :return:
        """
        self.set_selected_piece(None)

    def get_piece(self):
        """
        Returns piece located at mouse pos.
        :return:
        """
        pos = pg.mouse.get_pos()
        clicked_sprites = [s for s in self._game.all_sprites if s.rect.collidepoint(pos)]
        if clicked_sprites:
            return clicked_sprites[0]
        else:
            return None

    def get_piece_from_coord(self, coord):
        """
        Returns piece object from given Coord.
        :param coord: cell to check, based on grid coords, not pixel coords
        :return: Piece object
        """
        for sprite in self._game.all_sprites:
            if sprite.get_cell_location() == coord:
                return sprite

    def find_closest_cell(self, piece):
        """
        Attempts to position dropped piece into nearest cell.
        :param piece:
        :return:
        """
        if piece:
            cell = self.cell_pos(piece.get_location())
            global_coord = self.global_pos(cell)
            if global_coord:
                x, y = global_coord
                return (x + TILESIZE/2, y + TILESIZE/2)
            else:
                return piece.get_previous_location()

    def update_move_banks(self, exclude=None):
        """
        Cycles through all pieces and updates move banks.
        :param exclude: optional. if given, will exclude that piece from move updates.
        :return:
        """
        self.clear_attacking_banks()
        for sprite in self._game.all_sprites:
            if sprite != exclude:
                sprite.clear_move_bank()
                if sprite.get_cell_location() is not None:
                    sprite.update_move_bank()
        # if not self.black_king().get_has_moved():
        #     self.black_king().castle_check(4, 0)
        # if not self.white_king().get_has_moved():
        #     self.white_king().castle_check(4, 7)

    def clear_team_move_banks(self):
        """
        Clears verified move banks of teams.
        :return:
        """
        self._white_moves.clear()
        self._black_moves.clear()

    def resolve_attack(self, piece, passant):
        """
        Checks if there is a collision between two chess pieces and resolves it.
        :param piece: piece most recently moved
        :param passant: if to allow passant kills
        :return:
        """
        if piece:
            if passant:
                if piece._color != self._passant_pawn._color:
                    self._passant_pawn.kill()
            for sprite in self._game.all_sprites:
                if sprite is not piece:
                    if sprite.get_location() == piece.get_location():
                        if sprite.get_color() != piece.get_color():
                            sprite.kill()
                        else:
                            piece.set_location(piece.get_previous_location())

    def evaluate_check(self, king):
        """
        Evaluates if king is currently in check. Sets the check flag when needed.
        :param king: king piece being evaluated
        :return: True if a check is in effect
        """
        king.set_check_flag(False)
        if king.get_color() == 'Black':
            if king.get_cell_location() in self.get_white_bank():
                king.set_check_flag(True)
                return True
        elif king.get_color() == 'White':
            if king.get_cell_location() in self.get_black_bank():
                king.set_check_flag(True)
                return True
        return False

    def mate_check(self):
        """
        Evaluates if check mate exists and sets winner.
        :return:
        """
        if not self._black_moves:
            self._winner = 'White'
        if not self._white_moves:
            self._winner = 'Black'
