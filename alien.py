import pygame
import random
from pygame.sprite import Sprite
import os

class Alien(Sprite):
    """A class to represent a single alien in the fleet."""

    def __init__(self, ai_game):
        """Initialize the alien and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load the alien image and set its rect attribute.
        Alien_image_path = os.path.join(os.path.dirname(__file__), 'images', '12.png')
        self.image = pygame.image.load(Alien_image_path)
        self.rect = self.image.get_rect()

        # Start each new alien at a random position on the screen (excluding the bottom edge).
        self.rect.x = random.randint(0, self.screen.get_width() - self.rect.width)
        # Ensure the alien does not start at the bottom edge
        self.rect.y = random.randint(0, self.screen.get_height() - self.rect.height - 400)  # 减去1以确保不在下边界

        # Store the alien's exact position as a float.
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # Set a random speed for the alien's movement.
        self.speed_x = random.choice([-1, 1]) * random.uniform(0.5, 1.5)  # 横向移动速度
        self.speed_y = random.choice([-1, 1]) * random.uniform(0.5, 1.5)  # 纵向移动速度

    def check_edges(self):
        """Return True if alien is at edge of screen."""
        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0) or \
               (self.rect.bottom >= screen_rect.bottom) or (self.rect.top <= 0)

    def update(self):
        """Move the alien randomly."""
        # 更新位置
        self.x += self.speed_x
        self.y += self.speed_y

        # 更新rect的位置
        self.rect.x = self.x
        self.rect.y = self.y

        # 检查边缘并反向移动
        if self.check_edges():
            self.speed_x *= -1
            self.speed_y *= -1
