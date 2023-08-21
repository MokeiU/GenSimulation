import pygame


class Button:
    COOLDOWN = 25
    b_cycle = 0

    def __init__(self, function1, function2, surface: pygame.surface.Surface,
                 cords, color):
        self.surface = surface
        self.cords = cords
        self.color = color
        self.last_press = 0
        self.function1 = function1
        self.function2 = function2
        self.current_f1 = True

    def is_pressed(self):
        if pygame.mouse.get_pressed()[0] and self.b_cycle - self.last_press > self.COOLDOWN:
            cx, cy = pygame.mouse.get_pos()
            x, y, h, w = self.cords
            if x < cx < x + h and y < cy < y + w:
                return True
        return False

    def draw(self):
        pygame.draw.rect(self.surface, self.color, self.cords, 0, 12)
        self.b_cycle += 1

    def cooldown(self):
        self.last_press = self.b_cycle

    def check(self):
        if self.is_pressed():
            if self.current_f1:
                self.function1()
            else:
                self.function2()
            self.cooldown()
            self.current_f1 = not self.current_f1
