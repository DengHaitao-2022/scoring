import pygame
from pygame.sprite import Sprite
import os

class AlienBullet(Sprite):
    """A class to manage bullets fired from the aliens."""

    def __init__(self, ai_game, alien):
        """Create a bullet object at the alien's current position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.alien_bullet_color

        # Create a bullet rect at (0, 0) and then set correct position.
        zid_image_path = os.path.join(os.path.dirname(__file__), 'images', 'zid.png')
        self.image = pygame.image.load(zid_image_path) # 这里替换为你自己的子弹图片路径
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width,
            self.settings.bullet_height)
        self.rect.midbottom = alien.rect.midbottom

        # Store the bullet's position as a float.
        self.y = float(self.rect.y)

    def update(self):
        """Move the bullet down the screen."""
        # Update the exact position of the bullet.
        self.y += self.settings.alien_bullet_speed
        # Update the rect position.
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw the bullet to the screen."""
        self.screen.blit(self.image, self.rect) 