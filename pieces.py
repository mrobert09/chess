from settings import *


class Piece(pg.sprite.Sprite):
    """
    General information applicable to all pieces.
    """

    def __init__(self, color, location, data):
        """
        Initialization of piece data. Some redundant info is recorded. Hope to clean up at some point.
        :param color: 'White' / 'Black'
        :param location: original cell location of piece
        :param data: window to the data class that object was created in
        """
        pg.sprite.Sprite.__init__(self)
        self._data = data
        self._color = color  # black or white
        self._cell_location = location  # position in board grid
        self._previous_cell = None
        self._move_bank = []
        self._verified_move_bank = []
        self._location = self._data.global_pos(location)
        self._previous_location = None
        self._starting_cell = self._cell_location
        self._has_moved = False
        self._pawn = False
        if self._starting_cell[1] == 1 or self._starting_cell[1] == 6:
            self._pawn = True
        self._king = False
        if self._starting_cell[0] == 4 and (self._starting_cell[1] == 0 or self._starting_cell[1] == 7):
            self._king = True
        self._layer = 0

        # debug
        self._debug = 0

    def set_location(self, loc):
        """
        Sets current pixel location.
        :param loc:
        :return:
        """
        self._location = loc

    def set_previous_location(self):
        """
        Sets previous pixel / cell location of a piece. Used right before temporarily changing the piece's location
        for evaluation purposes.
        :return:
        """
        self._previous_location = self._location
        self._previous_cell = self._cell_location

    def get_location(self):
        """
        Returns current location of piece. This is often a temporary value as a piece gets evaluated.
        :return:
        """
        return self._location

    def get_previous_location(self):
        """
        Returns previous pixel location of piece.
        :return:
        """
        return self._previous_location

    def get_cell_location(self):
        """
        Returns current location of piece. Note: This may be a temporary location for evaluations.
        :return:
        """
        return self._cell_location

    def get_has_moved(self):
        """
        Returns if a piece has moved.
        :return:
        """
        return self._has_moved

    def set_cell_location(self, cell):
        """
        Sets piece's currently cell location.
        :return:
        """
        self._cell_location = cell

    def get_previous_cell(self):
        """
        Returns last cell position of piece.
        :return:
        """
        return self._previous_cell

    def get_color(self):
        """
        Returns color of piece.
        :return:
        """
        return self._color

    def get_move_bank(self):
        """
        Returns piece's current move bank.
        :return:
        """
        return self._move_bank

    def get_verified_move_bank(self):
        """
        Returns the verified move bank.
        :return:
        """
        return self._verified_move_bank

    def clear_move_bank(self):
        """
        Clears move bank for piece.
        :return:
        """
        self._move_bank.clear()

    def check_passant(self):
        """
        Checks status of passant and updates variable.
        :return:
        """
        if self._previous_cell == self._starting_cell:
            if self._previous_cell[0] == self._cell_location[0]:
                if self.get_color() == 'White':
                    self._data.set_passant((self._previous_cell[0], self._previous_cell[1] - 1), self)
                else:
                    self._data.set_passant((self._previous_cell[0], self._previous_cell[1] + 1), self)

    def resolve_castle(self, cell):
        """
        Resolves Kings trying to castle.
        :return:
        """
        # If King castled left
        if self._starting_cell[0] == cell[0] + 2:
            rook = self._data.get_piece_from_coord((0, cell[1]))
            rook.set_location(self._data.global_pos((cell[0] + 1, cell[1])))
            rook.set_cell_location((cell[0] + 1, cell[1]))

        # If King castled right
        if self._starting_cell[0] == cell[0] - 2:
            rook = self._data.get_piece_from_coord((7, cell[1]))
            rook.set_location(self._data.global_pos((cell[0] - 1, cell[1])))
            rook.set_cell_location((cell[0] - 1, cell[1]))

    def move_validation(self, cell):
        """
        Updated move_validation function for determining if attempted move is valid.
        :return:
        """
        if cell not in self._verified_move_bank:
            print('Bad Move Condition')
            self._location = self._previous_location
            self._cell_location = self._previous_cell
            return False
        self.set_location((self._data.global_pos(cell)))
        if self._data.get_passant() == cell and self._pawn:
            self._data.resolve_attack(self, True)
        else:
            self._data.resolve_attack(self, False)
        self._data.clear_passant()
        if self._pawn:
            self.check_passant()
        if self._king and not self.get_has_moved():
            self.resolve_castle(cell)
        self._has_moved = True
        return True

    def add_to_move_bank(self, cell, verified=False):
        """
        Adds cell to piece's move bank, and also adds to team attacking bank.
        :param cell: tuple
        :param verified: If True, also add to the verified move bank.
        :return:
        """
        self._move_bank.append(cell)
        self.add_attacking_bank(cell)
        if verified and self._color == 'Black':
            self._data._black_moves.append(cell)
            self._verified_move_bank.append(cell)
        if verified and self._color == 'White':
            self._data._white_moves.append(cell)
            self._verified_move_bank.append(cell)

    def add_attacking_bank(self, cell):
        """
        Adds cell to bank of cells currently under attack by a team.
        :param cell: tuple
        :return:
        """
        if self.get_color() == 'Black':
            if cell not in self._data.get_black_bank():
                self._data.add_black_bank(cell)
        if self.get_color() == 'White':
            if cell not in self._data.get_white_bank():
                self._data.add_white_bank(cell)

    def emulate_move_bank(self):
        """
        Simulates each move in bank to see if they are actually legal (can't make a play that leaves self in check).
        Replaces original move bank with only legal moves.
        :return:
        """
        original_position = self.get_cell_location()
        new_move_bank = []
        for move in self.get_move_bank():
            self.set_cell_location(move)
            self._data.scan_board()
            self._data.update_move_banks(self)  # excludes self from updates
            if self.get_color() == 'Black':
                if not self._data.evaluate_check(self._data.black_king()):
                    new_move_bank.append(move)
            else:
                if not self._data.evaluate_check(self._data.white_king()):  # for white king
                    new_move_bank.append(move)

        self.set_cell_location(original_position)
        self._data.scan_board()
        self._data.update_move_banks(self)
        self.clear_move_bank()
        for move in new_move_bank:
            self.add_to_move_bank(move, True)
        self._verified_move_bank = self._move_bank.copy()
        self._data.evaluate_check(self._data.black_king())
        self._data.evaluate_check(self._data.white_king())

    def update(self):
        """
        Update information for pieces.
        :return:
        """
        self.rect.center = self._location
        self._cell_location = self._data.cell_pos(self._location)


class King(Piece):
    """
    King specific information.
    """

    def __init__(self, color, location, data):
        super().__init__(color, location, data)
        if color == 'Black':
            self.image = pg.image.load(path(img_folder, 'bk.svg'))
            self._data.black_king(self)
        else:
            self.image = pg.image.load(path(img_folder, 'wk.svg'))
            self._data.white_king(self)
        self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.center = self._location
        self._in_check = False

    def update_move_bank(self):
        """
        Updates available moves.
        :return:
        """
        self._move_bank.clear()
        x = self._cell_location[0]
        y = self._cell_location[1]

        # Blank move bank for simulating being attacked
        if self._data.get_occupied().count((x, y)) == 2:  # another piece being simulated is on top of this piece
            return

        self.update_move_bank_helper(x + 1, y + 1)
        self.update_move_bank_helper(x + 1, y - 1)
        self.update_move_bank_helper(x + 1, y)
        self.update_move_bank_helper(x - 1, y + 1)
        self.update_move_bank_helper(x - 1, y - 1)
        self.update_move_bank_helper(x - 1, y)
        self.update_move_bank_helper(x, y + 1)
        self.update_move_bank_helper(x, y - 1)

    def update_move_bank_helper(self, x, y):
        """
        Helper function to reduce code clutter.
        :return:
        """
        if (x, y) in self._data.get_occupied():
            if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                self.add_to_move_bank((x, y))
            else:
                return
        elif x < 0 or x > 7 or y < 0 or y > 7:
            pass
        else:
            self.add_to_move_bank((x, y))

    def castle_check(self, x, y):
        """
        Checks if any castle move is available.
        :return:
        """
        if self.get_has_moved():
            return False

        if self._in_check:
            return False

        left_rook = self._data.get_piece_from_coord((x - 4, y))
        right_rook = self._data.get_piece_from_coord((x + 3, y))

        if self.get_color() == 'Black':
            if (x, y) not in self._data.get_white_bank():
                # Check left castle
                if (x - 1, y) not in self._data.get_occupied() and (x - 1, y) not in self._data.get_white_bank():
                    if (x - 2, y) not in self._data.get_occupied() and (x - 2, y) not in self._data.get_white_bank():
                        if (x - 3, y) not in self._data.get_occupied() \
                                and (x - 3, y) not in self._data.get_white_bank():
                            if left_rook and not left_rook.get_has_moved() \
                                    and (x - 4, y) not in self._data.get_white_bank():
                                self.add_to_move_bank((x - 2, y), True)

                # Check right castle
                if (x + 1, y) not in self._data.get_occupied() and (x + 1, y) not in self._data.get_white_bank():
                    if (x + 2, y) not in self._data.get_occupied() and (x + 2, y) not in self._data.get_white_bank():
                        if right_rook and not right_rook.get_has_moved() \
                                and (x + 3, y) not in self._data.get_white_bank():
                            self.add_to_move_bank((x + 2, y), True)

        elif self.get_color() == 'White':
            if (x, y) not in self._data.get_black_bank():
                # Check left castle
                if (x - 1, y) not in self._data.get_occupied() and (x - 1, y) not in self._data.get_black_bank():
                    if (x - 2, y) not in self._data.get_occupied() and (x - 2, y) not in self._data.get_black_bank():
                        if (x - 3, y) not in self._data.get_occupied() \
                                and (x - 3, y) not in self._data.get_black_bank():
                            if left_rook and not left_rook.get_has_moved() \
                                    and (x - 4, y) not in self._data.get_black_bank():
                                self.add_to_move_bank((x - 2, y), True)

                # Check right castle
                if (x + 1, y) not in self._data.get_occupied() and (x + 1, y) not in self._data.get_black_bank():
                    if (x + 2, y) not in self._data.get_occupied() and (x + 2, y) not in self._data.get_black_bank():
                        if right_rook and not right_rook.get_has_moved() \
                                and (x + 3, y) not in self._data.get_black_bank():
                            self.add_to_move_bank((x + 2, y), True)

    def set_check_flag(self, flag):
        """
        Sets whether king is currently in check or not.
        :param flag: True/False
        :return:
        """
        self._in_check = flag

    def get_check_flag(self):
        """
        Returns current state of check.
        :return:
        """
        return self._in_check


class Queen(Piece):
    """
    Queen specific information.
    """

    def __init__(self, color, location, data):
        super().__init__(color, location, data)
        if color == 'Black':
            self.image = pg.image.load(path(img_folder, 'bq.svg'))
        else:
            self.image = pg.image.load(path(img_folder, 'wq.svg'))
        self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.center = self._location

    def update_move_bank(self):
        """
        Updates available moves.
        :return:
        """
        self._move_bank.clear()
        cell_location = self._cell_location

        # Blank move bank for simulating being attacked
        if self._data.get_occupied().count(cell_location) == 2:  # another piece being simulated is on top of this piece
            return

        # Check N
        step = 1
        while step:
            x = cell_location[0]
            y = cell_location[1] - step
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1
        # Check S
        step = 1
        while step:
            x = cell_location[0]
            y = cell_location[1] + step
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1
        # Check E
        step = 1
        while step:
            x = cell_location[0] + step
            y = cell_location[1]
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1
        # Check W
        step = 1
        while step:
            x = cell_location[0] - step
            y = cell_location[1]
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1
        # Check NE
        step = 1
        while step:
            x = cell_location[0] + step
            y = cell_location[1] - step
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1
        # Check NW
        step = 1
        while step:
            x = cell_location[0] - step
            y = cell_location[1] - step
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1
        # Check SE
        step = 1
        while step:
            x = cell_location[0] + step
            y = cell_location[1] + step
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1
        # Check SW
        step = 1
        while step:
            x = cell_location[0] - step
            y = cell_location[1] + step
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1


class Bishop(Piece):
    """
    Bishop specific information.
    """

    def __init__(self, color, location, data):
        super().__init__(color, location, data)
        if color == 'Black':
            self.image = pg.image.load(path(img_folder, 'bb.svg'))
        else:
            self.image = pg.image.load(path(img_folder, 'wb.svg'))
        self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.center = self._location

    def update_move_bank(self):
        """
        Updates available moves.
        :return:
        """
        self._move_bank.clear()
        cell_location = self._cell_location

        # Blank move bank for simulating being attacked
        if self._data.get_occupied().count(cell_location) == 2:  # another piece being simulated is on top of this piece
            return

        # Check NE
        step = 1
        while step:
            x = cell_location[0] + step
            y = cell_location[1] - step
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1
        # Check NW
        step = 1
        while step:
            x = cell_location[0] - step
            y = cell_location[1] - step
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1
        # Check SE
        step = 1
        while step:
            x = cell_location[0] + step
            y = cell_location[1] + step
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1
        # Check SW
        step = 1
        while step:
            x = cell_location[0] - step
            y = cell_location[1] + step
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1


class Knight(Piece):
    """
    Knight specific information.
    """

    def __init__(self, color, location, data):
        super().__init__(color, location, data)
        if color == 'Black':
            self.image = pg.image.load(path(img_folder, 'bn.svg'))
        else:
            self.image = pg.image.load(path(img_folder, 'wn.svg'))
        self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.center = self._location

        self._debug = 1

    def update_move_bank(self):
        """
        Updates available moves. Checks all 8 possible jump spots to see if piece is present.
        :return:
        """
        self._move_bank.clear()
        x = self._cell_location[0]
        y = self._cell_location[1]

        # Blank move bank for simulating being attacked
        if self._data.get_occupied().count((x, y)) == 2:  # another piece being simulated is on top of this piece
            return

        self.update_move_bank_helper(x + 2, y + 1)
        self.update_move_bank_helper(x + 2, y - 1)
        self.update_move_bank_helper(x - 2, y + 1)
        self.update_move_bank_helper(x - 2, y - 1)
        self.update_move_bank_helper(x + 1, y + 2)
        self.update_move_bank_helper(x - 1, y + 2)
        self.update_move_bank_helper(x + 1, y - 2)
        self.update_move_bank_helper(x - 1, y - 2)

    def update_move_bank_helper(self, x, y):
        """
        Helper function to reduce code clutter.
        :param x: x-coord of move being checked
        :param y: y-coord of move being checked
        :return:
        """
        if (x, y) in self._data.get_occupied():
            if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                self.add_to_move_bank((x, y))
            else:
                return
        elif x < 0 or x > 7 or y < 0 or y > 7:
            pass
        else:
            self.add_to_move_bank((x, y))


class Rook(Piece):
    """
    Rook specific information.
    """

    def __init__(self, color, location, data):
        super().__init__(color, location, data)
        if color == 'Black':
            self.image = pg.image.load(path(img_folder, 'br.svg'))
        else:
            self.image = pg.image.load(path(img_folder, 'wr.svg'))
        self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.center = self._location

    def update_move_bank(self):
        """
        Updates available moves.
        :return:
        """
        self._move_bank.clear()
        cell_location = self._cell_location

        # Blank move bank for simulating being attacked
        if self._data.get_occupied().count(cell_location) == 2:  # another piece being simulated is on top of this piece
            return

        # Check N
        step = 1
        while step:
            x = cell_location[0]
            y = cell_location[1] - step
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1
        # Check S
        step = 1
        while step:
            x = cell_location[0]
            y = cell_location[1] + step
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1
        # Check E
        step = 1
        while step:
            x = cell_location[0] + step
            y = cell_location[1]
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1
        # Check W
        step = 1
        while step:
            x = cell_location[0] - step
            y = cell_location[1]
            if (x, y) in self._data.get_occupied():
                if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                    self.add_to_move_bank((x, y))
                step = 0
            elif x < 0 or x > 7 or y < 0 or y > 7:
                step = 0
            else:
                self.add_to_move_bank((x, y))
                step += 1


class Pawn(Piece):
    """
    Pawn specific information.
    """

    def __init__(self, color, location, data):
        super().__init__(color, location, data)
        if color == 'Black':
            self.image = pg.image.load(path(img_folder, 'bp.svg'))
        else:
            self.image = pg.image.load(path(img_folder, 'wp.svg'))
        self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.center = self._location

    def update_move_bank(self):
        """
        Updates available moves.
        :return:
        """
        self._move_bank.clear()
        x = self._cell_location[0]
        y = self._cell_location[1]

        # Blank move bank for simulating being attacked
        if self._data.get_occupied().count((x, y)) == 2:  # another piece being simulated is on top of this piece
            return

        # Check N
        if self.update_move_bank_helper(x, y - 1, False):
            if self.get_color() == 'White':
                self._move_bank.append((x, y - 1))
                # Check N+N
                if (x, y) == self._starting_cell:
                    if self.update_move_bank_helper(x, y - 2, False):
                        self._move_bank.append((x, y - 2))
        # Check S
        if self.update_move_bank_helper(x, y + 1, False):
            if self.get_color() == 'Black':
                self._move_bank.append((x, y + 1))
                # Check S+S
                if (x, y) == self._starting_cell:
                    if self.update_move_bank_helper(x, y + 2, False):
                        self._move_bank.append((x, y + 2))
        # Check NE
        if self.update_move_bank_helper(x + 1, y - 1, True):
            if self.get_color() == 'White':
                self._move_bank.append((x + 1, y - 1))
                self.add_attacking_bank((x + 1, y - 1))
        # Check NW
        if self.update_move_bank_helper(x - 1, y - 1, True):
            if self.get_color() == 'White':
                self._move_bank.append((x - 1, y - 1))
                self.add_attacking_bank((x - 1, y - 1))
        # Check SE
        if self.update_move_bank_helper(x + 1, y + 1, True):
            if self.get_color() == 'Black':
                self._move_bank.append((x + 1, y + 1))
                self.add_attacking_bank((x + 1, y + 1))
        # Check SW
        if self.update_move_bank_helper(x - 1, y + 1, True):
            if self.get_color() == 'Black':
                self._move_bank.append((x - 1, y + 1))
                self.add_attacking_bank((x - 1, y + 1))

    def update_move_bank_helper(self, x, y, attacking):
        """
        Helper function to reduce code clutter.
        :param x: cell x-coord
        :param y: cell y-coord
        :param attacking: True / False if this move would be valid attack attempt
        :return: True if move is valid, False otherwise
        """
        if (x, y) in self._data.get_occupied():
            if self._data.get_piece_from_coord((x, y)).get_color() != self.get_color():
                if attacking:
                    return True
                else:
                    return False
            else:
                return False
        elif attacking:  # only allow attack on empty square if it is En Passant
            if (x, y) == self._data.get_passant() and self.get_color() != self._data.get_passant_pawn().get_color():
                return True
            else:
                if -1 < x < 8 and -1 < y < 8:
                    self.add_attacking_bank((x, y))  # still will add to potential attacking spots for pawns
                return False
        elif x < 0 or x > 7 or y < 0 or y > 7:
            return False
        else:
            return True
