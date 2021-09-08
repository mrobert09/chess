from settings import *


class Piece(pg.sprite.Sprite):
    """
    General information applicable to all pieces.
    """

    def __init__(self, color, location, piece_type, img, data):
        """
        Initialization of piece data. Some redundant info is recorded. Hope to clean up at some point.
        Difference between moves and verified moves. The base move bank is all moves that look possible on a
        1st pass. Only during simulation of that move does the system determine if that move lead to a legal
        board state or not. For example, moving a piece in a legal direction for that piece's move set, but
        causing a self-check. If during the simulation it is determined that a move leads to a non-legal board
        position, then that move is not added to the verified move bank.
        :param color: 'White' / 'Black'
        :param location: original cell location of piece
        :param data: window to the data class that object was created in
        :param piece_type: string of type of piece (Pawn / Knight / Queen etc)
        """
        pg.sprite.Sprite.__init__(self)
        self.data = data
        self.color = color  # black or white
        self.piece_type = piece_type
        self.cell_location = location  # position in board grid
        self.previous_cell = None
        self.pixel_location = self.data.global_pos(location)
        self.previous_pixel = None
        self.move_bank = []
        self.verified_move_bank = []
        self.starting_cell = self.cell_location
        self.has_moved = False

        self.image = pg.image.load(path(img_folder, img))
        self.image = pg.transform.scale(self.image, (TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.center = self.pixel_location
        self._layer = 0

        # debug
        self._debug = 0

    @property
    def pixel_location(self):
        """
        Returns current location of piece. This is often a temporary value as a piece gets evaluated.
        :return:
        """
        return self._pixel_location

    @pixel_location.setter
    def pixel_location(self, loc):
        """
        Sets current pixel location.
        :param loc:
        :return:
        """
        self._pixel_location = loc

    @property
    def cell_location(self):
        """
        Returns current location of piece. Note: This may be a temporary location for evaluations.
        :return:
        """
        return self._cell_location

    @cell_location.setter
    def cell_location(self, cell):
        """
        Sets piece's currently cell location.
        :return:
        """
        self._cell_location = cell

    @property
    def previous_cell(self):
        """
        Returns last cell position of piece.
        :return:
        """
        return self._previous_cell

    @previous_cell.setter
    def previous_cell(self, cell):
        """
        Sets the previous cell position of a piece.
        :param cell: tuple
        :return:
        """
        self._previous_cell = cell

    @property
    def previous_pixel(self):
        """
        Returns the previous pixel location of piece.
        :return:
        """
        return self._previous_pixel

    @previous_pixel.setter
    def previous_pixel(self, pixel):
        """
        Sets previous pixel location of a piece.
        :param pixel: tuple
        :return:
        """
        self._previous_pixel = pixel

    def set_previous_location(self):
        """
        Sets previous pixel / cell location of a piece. Used right before temporarily changing the piece's location
        for evaluation purposes.
        :return:
        """
        self.previous_pixel = self.pixel_location
        self.previous_cell = self.cell_location

    @property
    def piece_type(self):
        """
        Returns the type of piece it is.
        :return: 'Knight', 'Pawn', etc.
        """
        return self._piece_type
    
    @piece_type.setter
    def piece_type(self, piece_type):
        """
        Sets the type of piece. Currently unused but a needed as a component of @property.
        :return: 
        """
        self._piece_type = piece_type

    @property
    def color(self):
        """
        Returns color of piece.
        :return:
        """
        return self._color

    @color.setter
    def color(self, color):
        """
        Setter for color of piece. Currently unusued but needed as a component of @property.
        :param color: 'Black' or 'White'
        :return:
        """
        self._color = color

    @property
    def has_moved(self):
        """
        Returns if a piece has moved.
        :return:
        """
        return self._has_moved

    @has_moved.setter
    def has_moved(self, flag):
        """
        Sets flag for if piece has moved.
        :param flag: True / False
        :return:
        """
        self._has_moved = flag

    @property
    def starting_cell(self):
        """
        Returns cell the piece started in.
        :return:
        """
        return self._starting_cell

    @starting_cell.setter
    def starting_cell(self, cell):
        """
        Sets the starting cell of piece.
        :param cell: tuple
        :return:
        """
        self._starting_cell = cell

    @property
    def move_bank(self):
        """
        Returns piece's current move bank.
        :return:
        """
        return self._move_bank

    @move_bank.setter
    def move_bank(self, cell):
        """
        Used for modifying move_bank.
        :param cell: tuple
        :return:
        """
        self._move_bank = cell

    @property
    def verified_move_bank(self):
        """
        Returns the verified move bank.
        :return:
        """
        return self._verified_move_bank

    @verified_move_bank.setter
    def verified_move_bank(self, cell):
        """
        Modifies verified move bank.
        :param cell: tuple
        :return:
        """
        self._verified_move_bank = cell

    def change_transform(self, scale):
        """
        Changes the size of the sprite image.
        :param scale:
        :return:
        """
        self.image = pg.transform.scale(self.image, (scale, scale))
        self.rect = self.image.get_rect()

    def check_passant(self):
        """
        Checks status of passant and updates variable.
        :return:
        """
        if self.previous_cell == self.starting_cell:
            if self.previous_cell[0] == self.cell_location[0] \
                    and abs(self.previous_cell[1] - self.cell_location[1]) == 2:
                if self.color == 'White':
                    self.data.passant = (self.previous_cell[0], self.previous_cell[1] - 1)
                else:
                    self.data.passant = (self.previous_cell[0], self.previous_cell[1] + 1)
                self.data.passant_pawn = self

    def resolve_castle(self, cell):
        """
        Resolves Kings trying to castle.
        :return:
        """
        # If King castled left
        if self.starting_cell[0] == cell[0] + 2:
            rook = self.data.get_piece_from_coord((0, cell[1]))
            rook.pixel_location = self.data.global_pos((cell[0] + 1, cell[1]))
            rook.cell_location = (cell[0] + 1, cell[1])

        # If King castled right
        if self.starting_cell[0] == cell[0] - 2:
            rook = self.data.get_piece_from_coord((7, cell[1]))
            rook.pixel_location = self.data.global_pos((cell[0] - 1, cell[1]))
            rook.cell_location = (cell[0] - 1, cell[1])

    def move_validation(self, cell):
        """
        Updated move_validation function for determining if attempted move is valid.
        :return:
        """
        if cell not in self.verified_move_bank:
            print('Bad Move Condition')
            self.pixel_location = self.previous_pixel
            self.cell_location = self.previous_cell
            return False
        self.pixel_location = (self.data.global_pos(cell))
        if self.data.passant == cell and self.piece_type == 'Pawn':
            self.data.resolve_attack(self, True)
        else:
            self.data.resolve_attack(self, False)
        self.data.passant = None
        self.data.passant_pawn = None
        if self.piece_type == 'Pawn':
            self.check_passant()
        if self.piece_type == 'King' and not self.has_moved:
            self.resolve_castle(cell)
        self.has_moved = True
        return True

    def add_to_move_bank(self, cell, verified=False):
        """
        Adds cell to piece's move bank, and also adds to team attacking bank.
        :param cell: tuple
        :param verified: If True, also add to the verified move bank.
        :return:
        """
        self.move_bank.append(cell)
        self.add_attacking_bank(cell)
        if verified and self.color == 'Black':
            self.data.verified_black_moves.append(cell)
            self.verified_move_bank.append(cell)
        if verified and self.color == 'White':
            self.data.verified_white_moves.append(cell)
            self.verified_move_bank.append(cell)

    def add_attacking_bank(self, cell):
        """
        Adds cell to bank of cells currently under attack by a team.
        :param cell: tuple
        :return:
        """
        if self.color == 'Black':
            if cell not in self.data.black_attacking:
                self.data.black_attacking.append(cell)
        if self.color == 'White':
            if cell not in self.data.white_attacking:
                self.data.white_attacking.append(cell)

    def simulate_move_bank(self):
        """
        Simulates each move in bank to see if they are actually legal (can't make a play that leaves self in check).
        Replaces original move bank with only legal moves.
        :return:
        """
        original_position = self.cell_location
        new_move_bank = []
        for move in self.move_bank:
            self.cell_location = move
            self.data.scan_board()
            self.data.update_move_banks(self)  # excludes self from updates

            # early scan and recheck to fix error related to kings capturing protected pieces
            if self.piece_type == 'King':
                self.data.scan_board()
                self.data.update_move_banks(self)

            if self.color == 'Black':
                if not self.data.evaluate_check(self.data.black_king):
                    new_move_bank.append(move)
            else:
                if not self.data.evaluate_check(self.data.white_king):  # for white king
                    new_move_bank.append(move)

        self.cell_location = original_position
        self.data.scan_board()
        self.data.update_move_banks(self)
        self.move_bank.clear()
        for move in new_move_bank:
            self.add_to_move_bank(move, True)
        self.verified_move_bank = self.move_bank.copy()
        self.data.evaluate_check(self.data.black_king)
        self.data.evaluate_check(self.data.white_king)

    def update(self):
        """
        Update information for pieces.
        :return:
        """
        self.rect.center = self.pixel_location
        self.cell_location = self.data.cell_pos(self.pixel_location)


class King(Piece):
    """
    King specific information.
    """

    def __init__(self, color, location, piece_type, img, data):
        super().__init__(color, location, piece_type, img, data)
        if color == 'Black':
            self.data.black_king = self
        else:
            self.data.white_king = self
        self.in_check = False

    def update_move_bank(self):
        """
        Updates available moves.
        :return:
        """
        self._move_bank.clear()
        x = self.cell_location[0]
        y = self.cell_location[1]

        # Blank move bank for simulating being attacked
        if self.data.occupied_cells.count((x, y)) == 2:  # another piece being simulated is on top of this piece
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
        if (x, y) in self.data.occupied_cells:
            if self.data.get_piece_from_coord((x, y)).color != self.color:
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
        if self.has_moved:
            return False

        if self._in_check:
            return False

        left_rook = self.data.get_piece_from_coord((x - 4, y))
        right_rook = self.data.get_piece_from_coord((x + 3, y))

        if self.color == 'Black':
            if (x, y) not in self.data.white_attacking:
                # Check left castle
                if (x - 1, y) not in self.data.occupied_cells and (x - 1, y) not in self.data.white_attacking:
                    if (x - 2, y) not in self.data.occupied_cells and (x - 2, y) not in self.data.white_attacking:
                        if (x - 3, y) not in self.data.occupied_cells \
                                and (x - 3, y) not in self.data.white_attacking:
                            if left_rook and not left_rook.has_moved \
                                    and (x - 4, y) not in self.data.white_attacking:
                                self.add_to_move_bank((x - 2, y), True)

                # Check right castle
                if (x + 1, y) not in self.data.occupied_cells and (x + 1, y) not in self.data.white_attacking:
                    if (x + 2, y) not in self.data.occupied_cells and (x + 2, y) not in self.data.white_attacking:
                        if right_rook and not right_rook.has_moved \
                                and (x + 3, y) not in self.data.white_attacking:
                            self.add_to_move_bank((x + 2, y), True)

        elif self.color == 'White':
            if (x, y) not in self.data.black_attacking:
                # Check left castle
                if (x - 1, y) not in self.data.occupied_cells and (x - 1, y) not in self.data.black_attacking:
                    if (x - 2, y) not in self.data.occupied_cells and (x - 2, y) not in self.data.black_attacking:
                        if (x - 3, y) not in self.data.occupied_cells \
                                and (x - 3, y) not in self.data.black_attacking:
                            if left_rook and not left_rook.has_moved \
                                    and (x - 4, y) not in self.data.black_attacking:
                                self.add_to_move_bank((x - 2, y), True)

                # Check right castle
                if (x + 1, y) not in self.data.occupied_cells and (x + 1, y) not in self.data.black_attacking:
                    if (x + 2, y) not in self.data.occupied_cells and (x + 2, y) not in self.data.black_attacking:
                        if right_rook and not right_rook.has_moved \
                                and (x + 3, y) not in self.data.black_attacking:
                            self.add_to_move_bank((x + 2, y), True)

    @property
    def in_check(self):
        """
        Returns current state of check.
        :return:
        """
        return self._in_check

    @in_check.setter
    def in_check(self, flag):
        """
        Sets whether king is currently in check or not.
        :param flag: True/False
        :return:
        """
        self._in_check = flag


class Queen(Piece):
    """
    Queen specific information.
    """

    def __init__(self, color, location, piece_type, img, data):
        super().__init__(color, location, piece_type, img, data)

    def update_move_bank(self):
        """
        Updates available moves.
        :return:
        """
        self._move_bank.clear()
        cell_location = self.cell_location

        # Blank move bank for simulating being attacked
        if self.data.occupied_cells.count(cell_location) == 2:  # another piece being simulated is on top of this piece
            return

        # Check N
        step = 1
        while step:
            x = cell_location[0]
            y = cell_location[1] - step
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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

    def __init__(self, color, location, piece_type, img, data):
        super().__init__(color, location, piece_type, img, data)

    def update_move_bank(self):
        """
        Updates available moves.
        :return:
        """
        self._move_bank.clear()
        cell_location = self.cell_location

        # Blank move bank for simulating being attacked
        if self.data.occupied_cells.count(cell_location) == 2:  # another piece being simulated is on top of this piece
            return

        # Check NE
        step = 1
        while step:
            x = cell_location[0] + step
            y = cell_location[1] - step
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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

    def __init__(self, color, location, piece_type, img, data):
        super().__init__(color, location, piece_type, img, data)

        self._debug = 1

    def update_move_bank(self):
        """
        Updates available moves. Checks all 8 possible jump spots to see if piece is present.
        :return:
        """
        self._move_bank.clear()
        x = self.cell_location[0]
        y = self.cell_location[1]

        # Blank move bank for simulating being attacked
        if self.data.occupied_cells.count((x, y)) == 2:  # another piece being simulated is on top of this piece
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
        if (x, y) in self.data.occupied_cells:
            if self.data.get_piece_from_coord((x, y)).color != self.color:
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

    def __init__(self, color, location, piece_type, img, data):
        super().__init__(color, location, piece_type, img, data)

    def update_move_bank(self):
        """
        Updates available moves.
        :return:
        """
        self._move_bank.clear()
        cell_location = self.cell_location

        # Blank move bank for simulating being attacked
        if self.data.occupied_cells.count(cell_location) == 2:  # another piece being simulated is on top of this piece
            return

        # Check N
        step = 1
        while step:
            x = cell_location[0]
            y = cell_location[1] - step
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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
            if (x, y) in self.data.occupied_cells:
                if self.data.get_piece_from_coord((x, y)).color != self.color:
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

    def __init__(self, color, location, piece_type, img, data):
        super().__init__(color, location, piece_type, img, data)

    def update_move_bank(self):
        """
        Updates available moves.
        :return:
        """
        self._move_bank.clear()
        x = self.cell_location[0]
        y = self.cell_location[1]

        # Blank move bank for simulating being attacked
        if self.data.occupied_cells.count((x, y)) == 2:  # another piece being simulated is on top of this piece
            return

        # Check N
        if self.update_move_bank_helper(x, y - 1, False):
            if self.color == 'White':
                self._move_bank.append((x, y - 1))
                # Check N+N
                if (x, y) == self.starting_cell:
                    if self.update_move_bank_helper(x, y - 2, False):
                        self._move_bank.append((x, y - 2))
        # Check S
        if self.update_move_bank_helper(x, y + 1, False):
            if self.color == 'Black':
                self._move_bank.append((x, y + 1))
                # Check S+S
                if (x, y) == self.starting_cell:
                    if self.update_move_bank_helper(x, y + 2, False):
                        self._move_bank.append((x, y + 2))
        # Check NE
        if self.update_move_bank_helper(x + 1, y - 1, True):
            if self.color == 'White':
                self._move_bank.append((x + 1, y - 1))
                self.add_attacking_bank((x + 1, y - 1))
        # Check NW
        if self.update_move_bank_helper(x - 1, y - 1, True):
            if self.color == 'White':
                self._move_bank.append((x - 1, y - 1))
                self.add_attacking_bank((x - 1, y - 1))
        # Check SE
        if self.update_move_bank_helper(x + 1, y + 1, True):
            if self.color == 'Black':
                self._move_bank.append((x + 1, y + 1))
                self.add_attacking_bank((x + 1, y + 1))
        # Check SW
        if self.update_move_bank_helper(x - 1, y + 1, True):
            if self.color == 'Black':
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
        if (x, y) in self.data.occupied_cells:
            if self.data.get_piece_from_coord((x, y)).color != self.color:
                if attacking:
                    return True
                else:
                    return False
            else:
                return False
        elif attacking:  # only allow attack on empty square if it is En Passant
            if (x, y) == self.data.passant and self.color != self.data.passant_pawn.color:
                return True
            else:
                if -1 < x < 8 and -1 < y < 8:
                    self.add_attacking_bank((x, y))  # still will add to potential attacking spots for pawns
                return False
        elif x < 0 or x > 7 or y < 0 or y > 7:
            return False
        else:
            return True
