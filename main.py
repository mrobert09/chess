from data import *


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
        self.b1 = None
        self.b2 = None
        self.running = True

    def new(self):
        """
        New Game
        :return:
        """
        self.data = GameData(self)
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.data.populate_board()
        self.data.scan_board()
        self.data.update_move_banks()
        for sprite in self.all_sprites:
            sprite.set_previous_location()
            sprite.emulate_move_bank()
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
                self.data.select_piece()
                piece = self.data.get_selected_piece()
                if piece:
                    if self.data._turn_order is True:
                        if piece.get_color() == self.data._turn:
                            piece.set_previous_location()
                        else:
                            piece.clear_verified_move_bank()
                    elif self.data._turn_order is False:
                        piece.set_previous_location()

            # Most game logic happens under this piece. Game state updates upon dropping piece on location.
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                piece = self.data.get_selected_piece()
                if piece:
                    nearest_cell = self.data.cell_pos(piece.get_location())
                    if piece.move_validation(nearest_cell):
                        self.data.scan_board()
                        self.data.update_move_banks()
                        self.data.change_turn()
                if self.data.evaluate_check(self.data.black_king()):
                    self.data.black_king().set_check_flag(True)
                else:
                    self.data.black_king().set_check_flag(False)
                if self.data.evaluate_check(self.data.white_king()):
                    self.data.white_king().set_check_flag(True)
                else:
                    self.data.white_king().set_check_flag(False)

                self.data.clear_selected_piece()
                self.data.clear_highlights()
                self.data.clear_team_move_banks()
                for sprite in self.all_sprites:
                    sprite.set_previous_location()
                    sprite.emulate_move_bank()
                if not self.data.black_king().get_has_moved():
                    self.data.black_king().castle_check(4, 0)
                if not self.data.white_king().get_has_moved():
                    self.data.white_king().castle_check(4, 7)
                self.data.mate_check()

            # Functionality to drag and drop chess pieces
            click = pg.mouse.get_pressed(3)
            if click[0]:
                piece = self.data.get_selected_piece()
                if piece:  # prevents None from causing error
                    pg.mouse.set_visible(False)
                    self.all_sprites.move_to_front(piece)
                    piece.set_location(pg.mouse.get_pos())
                    self.data.set_highlights(piece.get_verified_move_bank())

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

    def draw(self):
        """
        Game Loop - Draw
        :return:
        """
        self.screen.fill(WHITE)
        self.draw_grid()
        self.draw_highlights()
        self.draw_turn_buttons()
        self.all_sprites.draw(self.screen)
        self.draw_text()

        # always do last after drawing everything
        pg.display.flip()

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
        Draws a highlight around the currently selected cell.
        :return:
        """
        for cell in self.data.get_highlights():
            screen = self.screen
            g_pos = self.data.global_pos(cell)
            offset = TILESIZE / 2
            x, y = g_pos
            x -= offset
            y -= offset
            g_pos = (x, y)
            pg.draw.line(screen, YELLOW, g_pos, (g_pos[0] + TILESIZE, g_pos[1]), 3)
            pg.draw.line(screen, YELLOW, g_pos, (g_pos[0], g_pos[1] + TILESIZE), 3)
            pg.draw.line(screen, YELLOW, (g_pos[0], g_pos[1] + TILESIZE), (g_pos[0] + TILESIZE, g_pos[1] + TILESIZE), 3)
            pg.draw.line(screen, YELLOW, (g_pos[0] + TILESIZE, g_pos[1]), (g_pos[0] + TILESIZE, g_pos[1] + TILESIZE), 3)

    def draw_turn_buttons(self):
        """
        Draws buttons to interact with on the UI.
        :return:
        """
        global b1
        global b2
        x = X_OFFSET
        y = BOARDHEIGHT + Y_OFFSET + TILESIZE / 2
        x2 = x + 3*TILESIZE
        self.b1 = pg.Rect(x, y, 2 * TILESIZE + TILESIZE/2, TILESIZE)
        self.b2 = pg.Rect(x2, y, 2 * TILESIZE + TILESIZE/2, TILESIZE)
        pg.draw.rect(self.screen, BLACK, self.b1, 2)
        pg.draw.rect(self.screen, BLACK, self.b2, 2)

    def draw_text(self):
        """
        Used for debugging at the moment.
        :return:
        """
        # piece = self.data.get_piece()
        # mouse_pos = pg.mouse.get_pos()
        # cell = self.data.cell_pos(mouse_pos)
        # if cell:
        #     if cell in self.data.get_white_bank():
        #         x = 'Attacked'
        #     else:
        #         x = 'Safe'
        #     text = self.font.render(x, True, BLACK)
        text = self.font.render(str(self.data._winner), True, BLACK)
        # text = self.font.render(str(self.data.get_piece_from_coord((1, 0))._verified_move_bank), True, BLACK)
        text_rect = text.get_rect()
        text_rect.topleft = (600, 100)
        self.screen.blit(text, text_rect)

        b1_text = self.font.render('Turn Order On', True, BLACK)
        b2_text = self.font.render('Turn Order Off', True, BLACK)
        b1_text_rect = b1_text.get_rect()
        b2_text_rect = b2_text.get_rect()
        b1_text_rect.center = self.b1.center
        b2_text_rect.center = self.b2.center
        # b1_text.
        self.screen.blit(b1_text, b1_text_rect)
        self.screen.blit(b2_text, b2_text_rect)

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
    test_var = 3
    main()
