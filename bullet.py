import pygame
from pygame.sprite import Sprite
import os

class Bullet(Sprite):
    """A class to manage bullets fired from the ship."""

    def __init__(self, ai_game, ship):
        """Create a bullet object at the ship's current position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load the bullet image and get its rect.
        zd_image_path = os.path.join(os.path.dirname(__file__), 'images', '2.png')
        self.image = pygame.image.load(zd_image_path) # 这里替换为你自己的子弹图片路径
        self.rect = self.image.get_rect()
        self.rect.midtop = ship.rect.midtop  # 使用传入的飞船位置

        # Store the bullet's position as a float.
        self.y = float(self.rect.y)

    def update(self):
        """Move the bullet up the screen."""
        # Update the exact position of the bullet.
        self.y -= self.settings.bullet_speed
        # Update the rect position.
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw the bullet to the screen."""
        self.screen.blit(self.image, self.rect)