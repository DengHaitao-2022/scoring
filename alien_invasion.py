import sys
from time import sleep

import pygame
import random

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from alien_bullet import AlienBullet

class AlienInvasion:
    """Overall class to manage game assets and behavior."""
    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        # Load and play background music
        pygame.mixer.music.load('bj.mp3')  # 替换为您的背景音乐文件路径
        pygame.mixer.music.play(-1)  # -1 表示循环播放

        # Create an instance to store game statistics.
        self.stats = GameStats(self)

        # Create an instance of Scoreboard
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Load ship hit sound
        self.explosion_sound = pygame.mixer.Sound('ship_hit.mp3')

        # Load the background image
        self.bg_image = pygame.image.load('images/bj.bmp')  
        self.bg_image = pygame.transform.scale(self.bg_image, (self.settings.screen_width, self.settings.screen_height))

        # Load cover image
        self.cover_image = pygame.image.load('images/bj.png')  # 替换为您的封面图像路径
        self.cover_image = pygame.transform.scale(self.cover_image, (self.settings.screen_width, self.settings.screen_height))

        # Start Alien Invasion in an inactive state.
        self.game_active = False
         # Load font for title
        self.title_font = pygame.font.Font(None, 150)  # 选择合适的字体和大小
        # 创建按钮
        self.play_button = Button(self, "Play", (600, 350))
        self.exit_button = Button(self, "Exit", (600, 450))
    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_alien_bullets()
            else:
                self._show_cover()  # 显示封面

            self._update_screen()
            self.clock.tick(60)
    def _show_cover(self):
        """Display the cover image."""
        self.screen.blit(self.cover_image, (0, 0))  # 先绘制封面
    # 绘制Play和Exit按钮
        self.play_button.draw_button()  # 绘制Play按钮
        self.exit_button.draw_button()  # 绘制Exit按钮

    # 更新屏幕以显示封面
        pygame.display.flip()

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                self._check_exit_button(mouse_pos)  # 检查退出按钮

    def _check_exit_button(self, mouse_pos):
        """Exit the game when the player clicks Exit."""
        button_clicked = self.exit_button.check_click(mouse_pos)
        if button_clicked:
           pygame.quit()
           sys.exit()

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Reset the game statistics.
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)


    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
           self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
           self.ship.moving_left = True
        elif event.key == pygame.K_UP:  # 新增：向上移动
           self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:  # 新增：向下移动
           self.ship.moving_down = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
           self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
          self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
          self.ship.moving_left = False
        elif event.key == pygame.K_UP:  # 新增：停止向上移动
          self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:  # 新增：停止向下移动
          self.ship.moving_down = False

    def _fire_bullet(self):
       """Create a new bullet and add it to the bullets group."""
       if len(self.bullets) < 20:  # 限制最多发射 50 发子弹
        new_bullet = Bullet(self)  # 创建新子弹
        self.bullets.add(new_bullet)  # 将新子弹添加到子弹组
 

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positio
        self.bullets.update()
        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
          if bullet.rect.bottom <= 0:
             self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()
        # Check for collisions between bullets and aliens.
             
    def _check_bullet_alien_collisions(self):
         """Respond to bullet-alien collisions."""
         collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
         if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.explosion_sound.play()  # 播放爆炸音效
            self.sb.prep_score()
            self.sb.check_high_score()
         bullet_collisions = pygame.sprite.groupcollide(self.bullets, self.alien_bullets, True, True)
         if bullet_collisions:
            for bullets in bullet_collisions.values():
            # 播放音效或处理其他逻辑
                self.explosion_sound.play()  # 播放音效
         if not self.aliens:
             self.bullets.empty()
             self._create_fleet()
             self.settings.increase_speed()
             self.stats.level += 1
             self.sb.prep_level()

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""

        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Pause.
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()
        # Aliens fire bullets randomly
        self._alien_fire_bullet()

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit.
                # self._ship_hit()
                break

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and keep adding aliens until there's no room left.
        # Spacing between aliens is one alien width and one alien height.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            # Finished a row; reset x value, and increment y value.
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
    def _alien_fire_bullet(self):
        """Create a new alien bullet and add it to the alien bullets group."""
        if len(self.alien_bullets) < self.settings.alien_bullets_allowed and self.aliens:
            firing_alien = random.choice(self.aliens.sprites())
            new_bullet = AlienBullet(self, firing_alien)
            self.alien_bullets.add(new_bullet)
    def _update_alien_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.alien_bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)

        # Check for alien bullet-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            self._ship_hit()
   
    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        if self.game_active:
          self.screen.blit(self.bg_image, (0, 0))  # 仅在游戏激活时绘制背景
          for bullet in self.bullets.sprites():
            bullet.draw_bullet()
          for bullet in self.alien_bullets.sprites():
            bullet.draw_bullet()
            self.ship.blitme()
            self.aliens.draw(self.screen)

        # Draw the score information.
            self.sb.show_score()
             # Draw the play button if the game is inactive.
        if not self.game_active:
            self.play_button.draw_button()


        pygame.display.flip()

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()