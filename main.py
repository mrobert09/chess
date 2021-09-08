from data import *
from ui import *


class Game:
    """
    Instance of PyGame.
    """

    def __init__(self):
        """
        Init
        """
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.font = pg.font.Font(FONT_NAME, FONT_SIZE)
        self.clock = pg.time.Clock()
        self.running = True

    def new(self):
        """
        New Game
        :return:
        """
        self.data = GameData(self)
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.captured_sprites = pg.sprite.LayeredUpdates()
        self.ui = [] # list of all UI elements (like rects)
        self.create_ui()
        self.data.populate_board()
        self.data.scan_board()
        self.data.update_move_banks()
        for sprite in self.all_sprites:
            sprite.set_previous_location()
            sprite.simulate_move_bank()
        self.run()

    def run(self):
        """
        Game Loop
        :return:
        """
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        """
        Game Loop - Events
        :return:
        """
        for event in pg.event.get():

            # check for clicking of mouse
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                clicked_something = self.clicked_on()
                if clicked_something == 'Piece':
                    piece = self.data.get_piece()
                    self.data.selected_piece = piece
                    if self.data.turn_order is True:
                        if piece.color == self.data.turn:
                            piece.set_previous_location()
                        else:
                            piece.verified_move_bank.clear()
                    elif self.data.turn_order is False:
                        piece.set_previous_location()
                elif clicked_something == 'Rect':
                    rect = self.data.get_rect()
                    if rect.text == 'Turn Order On':
                        self.data.turn_order = True
                    elif rect.text == 'Turn Order Off':
                        self.data.turn_order = False


            # Most game logic happens under this piece. Game state updates upon dropping piece on location.
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                piece = self.data.selected_piece
                if piece:
                    self.data.selected_piece = piece
                    nearest_cell = self.data.cell_pos(piece.pixel_location)
                    if piece.move_validation(nearest_cell):
                        self.data.scan_board()
                        self.data.update_move_banks()
                        self.data.change_turn()
                if self.data.evaluate_check(self.data.black_king):
                    self.data.black_king.check_flag = True
                else:
                    self.data.black_king.check_flag = False
                if self.data.evaluate_check(self.data.white_king):
                    self.data.white_king.check_flag = True
                else:
                    self.data.white_king.check_flag = False

                self.data.selected_piece = None
                self.data.highlighted_cells.clear()
                self.data.clear_team_move_banks()
                for sprite in self.all_sprites:
                    sprite.set_previous_location()
                    sprite.simulate_move_bank()
                if not self.data.black_king.has_moved:
                    self.data.black_king.castle_check(4, 0)
                if not self.data.white_king.has_moved:
                    self.data.white_king.castle_check(4, 7)
                self.data.mate_check()

            # Functionality to drag and drop chess pieces
            click = pg.mouse.get_pressed(3)
            if click[0]:
                piece = self.data.selected_piece
                if piece:  # prevents None from causing error
                    pg.mouse.set_visible(False)
                    self.all_sprites.move_to_front(piece)
                    piece.pixel_location = pg.mouse.get_pos()
                    self.data.highlighted_cells = piece.verified_move_bank.copy()

            elif not click[0]:
                pg.mouse.set_visible(True)

            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def update(self):
        """
        Game Loop - Update
        :return:
        """
        self.all_sprites.update()
        self.captured_sprites.update()

    def draw(self):
        """
        Game Loop - Draw
        :return:
        """
        self.screen.fill(WHITE)
        self.draw_board()
        self.draw_ui()

        # always do last after drawing everything
        pg.display.flip()

    def clicked_on(self):
        """
        Determines if the mouse clicked on any element (sprite, rect, etc) on the screen.
        :return: Type of element clicked on, False if nothing
        """
        pos = pg.mouse.get_pos()
        clicked_sprites = [sprite for sprite in self.all_sprites if sprite.rect.collidepoint(pos)]
        clicked_rects = [element for element in self.ui if element.box.collidepoint(pos)]
        if clicked_sprites:
            return 'Piece'
        elif clicked_rects:
            return 'Rect'
        else:
            return False

    def create_ui(self):
        """
        Creates all UI objects and adds them to self.ui list.
        :return:
        """
        self.create_turn_buttons()
        self.create_captured_boxes()

    def create_turn_buttons(self):
        """
        Creates turn order buttons for debugging.
        :return:
        """
        x = X_OFFSET
        y = BOARDHEIGHT + Y_OFFSET + TILESIZE/2
        x2 = x + 3 * TILESIZE
        length = 2 * TILESIZE + TILESIZE/2
        width = TILESIZE

        order_on = TextBox('Turn Order On', (x, y), (length, width), self)
        self.ui.append(order_on)

        order_off = TextBox('Turn Order Off', (x2, y), (length, width), self)
        self.ui.append(order_off)

    def create_captured_boxes(self):
        """
        Creates boxes to display captured pieces.
        :return:
        """

        x = BOARDWIDTH + X_OFFSET + TILESIZE
        y = Y_OFFSET
        y2 = BOARDHEIGHT + Y_OFFSET - TILESIZE*2
        length = TILESIZE*3 - TILESIZE/2
        width = TILESIZE * 2

        black_captures = CapturedBox((x, y), (length, width), 'White', self)
        self.ui.append(black_captures)

        white_captures = CapturedBox((x, y2), (length, width), 'Black', self)
        self.ui.append(white_captures)

    def draw_board(self):
        """
        Holds all the board related draws.
        :return:
        """
        self.draw_grid()
        self.draw_highlights()
        self.all_sprites.draw(self.screen)
        self.captured_sprites.draw(self.screen)

    def draw_ui(self):
        """
        Holds all the UI related draws.
        :return:
        """
        for ui_element in self.ui:
            ui_element.draw()
        self.draw_text()

    def draw_grid(self):
        """
        Draws Chess board. X_OFFSET and Y_OFFSET can be adjusted in settings.py to adjust where the board appears.
        Lines drawn after tiles for better visuals.
        :return:
        """
        # Fill Colors
        for x_inter, x in enumerate(range(0 + X_OFFSET, BOARDWIDTH + X_OFFSET, TILESIZE)):
            for y_inter, y in enumerate(range(0 + Y_OFFSET, BOARDHEIGHT + Y_OFFSET, TILESIZE)):
                if (x_inter + y_inter) % 2 == 1:
                    pg.draw.rect(self.screen, GRAY, (x, y, TILESIZE, TILESIZE))

        # Draw Lines
        for x in range(0 + X_OFFSET, BOARDWIDTH+1 + X_OFFSET, TILESIZE):
            pg.draw.line(self.screen, BLACK, (x, 0 + Y_OFFSET), (x, BOARDHEIGHT + Y_OFFSET))
        for y in range(0 + Y_OFFSET, BOARDHEIGHT+1 + Y_OFFSET, TILESIZE):
            pg.draw.line(self.screen, BLACK, (0 + X_OFFSET, y), (BOARDWIDTH + X_OFFSET, y))

    def draw_highlights(self):
        """
        Highlights cells when moving and also highlights turn order button.
        :return:
        """
        for cell in self.data.highlighted_cells:
            g_pos = self.data.global_pos(cell)
            offset = TILESIZE / 2
            x, y = g_pos
            x -= offset
            y -= offset
            highlight = pg.Surface((TILESIZE-1, TILESIZE-1))
            highlight.set_alpha(128)
            highlight.fill(YELLOW)
            self.screen.blit(highlight, (x+1, y+1))

        y = BOARDHEIGHT + Y_OFFSET + TILESIZE / 2
        length = 2 * TILESIZE + TILESIZE / 2
        width = TILESIZE
        turn_order_highlight = pg.Surface((length, width))
        turn_order_highlight.set_alpha(128)
        turn_order_highlight.fill(GREEN)
        x_pos = X_OFFSET
        if self.data.turn_order == False:
            x_pos += (3 * TILESIZE)
        self.screen.blit(turn_order_highlight, (x_pos, y))

    def draw_text(self):
        """
        Used for debugging at the moment.
        :return:
        """
        text = self.font.render('Winner: ' + str(self.data.winner), True, BLACK)
        text_rect = text.get_rect()
        text_rect.topleft = (X_OFFSET, BOARDHEIGHT + Y_OFFSET + TILESIZE*(5/3))
        self.screen.blit(text, text_rect)

    def show_start_screen(self):
        """
        Game splash / start screen
        :return:
        """
        pass

    def show_go_screen(self):
        """
        Game over / continue
        :return:
        """
        pass


def main():
    g = Game()
    g.show_start_screen()
    while g.running:
        g.new()
        g.show_go_screen()
    pg.quit()


if __name__ == '__main__':
    main()
