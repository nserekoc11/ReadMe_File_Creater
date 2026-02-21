import pygame 

pygame.init()   

# Screen setup
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)

#Button class
class Button:
    def __init__(self,x,y,width,height,text,color, text_color):
        self.rect = pygame.Rect(x,y,width,height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hovered = False

    def draw(self,screen,font):

