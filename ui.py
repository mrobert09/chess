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