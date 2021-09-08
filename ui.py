from settings import *

class TextBox:
    """
    Text object used to more easily blit text where desired.
    """
    def __init__(self, text, location, box_size, main):
        self.main = main
        self.text = text
        self.render_text = self.main.font.render(self.text, True, BLACK)
        self.text_rect = self.render_text.get_rect()
        self.x, self.y = location
        self.length, self.width = box_size
        self.box = pg.Rect(self.x, self.y, self.length, self.width)
        self.text_rect.center = self.box.center

    def draw(self):
        pg.draw.rect(self.main.screen, BLACK, self.box, 2)
        self.main.screen.blit(self.render_text, self.text_rect)

class CapturedBox:
    """
    Box used to display pieces captured by each team.
    """
    def __init__(self, location, box_size, color, main):
        self.main = main
        self.text = None
        self.color = color
        self.x, self.y = location
        self.length, self.width = box_size
        self.box = pg.Rect(self.x, self.y, self.length, self.width)
        self.x += TILESIZE / 4
        self.y += TILESIZE / 4
        location = (self.x, self.y)
        self.next_box_position = location
        self.column = 0

    @property
    def next_box_position(self):
        """
        Returns the next position in box for captured piece to be displayed.
        :return:
        """
        return self._next_box_position

    @next_box_position.setter
    def next_box_position(self, location):
        """
        Sets next position in box for captured piece to be displayed.
        :param location: tuple
        :return:
        """
        self._next_box_position = location

    def set_next_box_position(self):
        """
        Function that's actually called to run the setter.
        :return:
        """
        x, y = self.next_box_position
        self.column += 1
        if self.column == 5:
            self.column = 0
            y += TILESIZE / 2
            x = self.x
        else:
            x += TILESIZE / 2
        self.next_box_position = (x, y)

    def draw(self):
        pg.draw.rect(self.main.screen, BLACK, self.box, 2)
