import sys
from time import sleep

import pygame
import random
import os

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
        bg_music_path = os.path.join(os.path.dirname(__file__), 'bj.mp3')
        pygame.mixer.music.load(bg_music_path)
        pygame.mixer.music.play(-1)  # -1 表示循环播放

        # Start Alien Invasion in an inactive state.
        self.game_active = False
        self.mode_selection_active = False  # 添加模式选择状态
        self.two_player_mode = False  # 添加双人游戏模式标志

        # Create an instance to store game statistics.
        self.stats = GameStats(self)

        # Create an instance of Scoreboard
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()
        
        explosion_sound_path = os.path.join(os.path.dirname(__file__), 'ship_hit.mp3')
        self.explosion_sound = pygame.mixer.Sound(explosion_sound_path)

        # Load the background image
        bg_image_path = os.path.join(os.path.dirname(__file__), 'images', 'bj.bmp')
        self.bg_image = pygame.image.load(bg_image_path)
        self.bg_image = pygame.transform.scale(self.bg_image, (self.settings.screen_width, self.settings.screen_height))

        # Load cover image
        cover_image_path = os.path.join(os.path.dirname(__file__), 'images', 'bj.png')
        self.cover_image = pygame.image.load(cover_image_path)
        self.cover_image = pygame.transform.scale(self.cover_image, (self.settings.screen_width, self.settings.screen_height))

        # Load font for title
        self.title_font = pygame.font.Font(None, 150)  # 选择合适的字体和大小

        # 创建按钮
        self.play_button = Button(self, "Play", (600, 350))
        self.single_player_button = Button(self, "Single Player", (600, 350))
        self.two_player_button = Button(self, "Two Players", (600, 450))
        self.exit_button = Button(self, "Exit", (600, 550))

        # 初始化键盘事件处理方法
        self._keydown_events = self._single_player_keydown_events
        self._keyup_events = self._single_player_keyup_events

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events() # 监视键盘和鼠标事件
            if self.game_active:
                self.ship.update()
                if self.two_player_mode:
                    self.ship2.update()
                self._update_bullets()
                self._update_aliens()
                self._update_alien_bullets()
            else:
                self._show_cover()  # 显示封面
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.mode_selection_active:
                    self._check_single_player_button(mouse_pos)
                    self._check_two_player_button(mouse_pos)
                else:
                    self._check_play_button(mouse_pos)
                    self._check_exit_button(mouse_pos)  # 检查退出按钮

    def _check_play_button(self, mouse_pos):
        """Display mode selection buttons when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.mode_selection_active = True  # 激活模式选择

    def _check_single_player_button(self, mouse_pos):
        """Start a single player game when the player clicks Single Player."""
        button_clicked = self.single_player_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.two_player_mode = False  # 设置为单人游戏模式
            self._start_game()

    def _check_two_player_button(self, mouse_pos):
        """Start a two player game when the player clicks Two Players."""
        button_clicked = self.two_player_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.two_player_mode = True  # 设置为双人游戏模式
            self._start_game()

    def _check_exit_button(self, mouse_pos):
        """Exit the game when the player clicks Exit."""
        button_clicked = self.exit_button.check_click(mouse_pos)
        if button_clicked:
            pygame.quit()
            sys.exit()

    def _start_game(self):
        """Start a new game."""
        # Reset the game settings.
        self.settings.initialize_dynamic_settings()

        # Reset the game statistics.
        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_high_score()
        self.sb.prep_level()
        self.sb.prep_ships()

        # 重新激活游戏状态和关闭模式选择状态
        self.game_active = True
        self.mode_selection_active = False

        # 清空所有剩余的子弹和外星人
        self.bullets.empty()
        self.alien_bullets.empty()
        self.aliens.empty()

        # 创建新的外星人群并将飞船重置到屏幕底部中央
        self._create_fleet()

        # 重置第一艘飞船的位置
        self.ship.center_ship()

        # 处理双人模式的重置
        if self.two_player_mode:
            # 创建并重置第二艘飞船，指定初始位置
            initial_position = (self.screen.get_rect().midbottom[0] + 150, self.screen.get_rect().midbottom[1])
            self.ship2 = Ship(self, initial_position=initial_position)

            # 设置双人模式的键盘事件处理
            self._keydown_events = self._two_player_keydown_events
            self._keyup_events = self._two_player_keyup_events
        else:
            self.ship2 = None
            self._keydown_events = self._single_player_keydown_events
            self._keyup_events = self._single_player_keyup_events

        # 隐藏鼠标光标
        pygame.mouse.set_visible(False)




    def _single_player_keydown_events(self, event):
        """Respond to keypresses in single player mode."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet(self.ship)

    def _single_player_keyup_events(self, event):
        """Respond to key releases in single player mode."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False

    def _two_player_keydown_events(self, event):
        """Respond to keypresses in two player mode."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True
        elif event.key == pygame.K_d:
            self.ship2.moving_right = True
        elif event.key == pygame.K_a:
            self.ship2.moving_left = True
        elif event.key == pygame.K_w:
            self.ship2.moving_up = True
        elif event.key == pygame.K_s:
            self.ship2.moving_down = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet(self.ship)
        elif event.key == pygame.K_LCTRL:
            self._fire_bullet(self.ship2)

    def _two_player_keyup_events(self, event):
        """Respond to key releases in two player mode."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False
        elif event.key == pygame.K_d:
            self.ship2.moving_right = False
        elif event.key == pygame.K_a:
            self.ship2.moving_left = False
        elif event.key == pygame.K_w:
            self.ship2.moving_up = False
        elif event.key == pygame.K_s:
            self.ship2.moving_down = False

    def _fire_bullet(self, ship):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < 20:  # 限制最多发射 20 发子弹
            new_bullet = Bullet(self, ship)  # 创建新子弹
            self.bullets.add(new_bullet)  # 将新子弹添加到子弹组

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self.explosion_sound.play()  # 播放爆炸音效
            self.sb.prep_score()
            self.sb.check_high_score()  # 确保调用 check_high_score 方法
        bullet_collisions = pygame.sprite.groupcollide(self.bullets, self.alien_bullets, True, True)
        if bullet_collisions:
            for bullets in bullet_collisions.values():
                self.explosion_sound.play()  # 播放音效
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit(self.ship)
        if self.two_player_mode and pygame.sprite.spritecollideany(self.ship2, self.aliens):
            self._ship_hit(self.ship2)

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

        # Aliens fire bullets randomly
        self._alien_fire_bullet()

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

    def _create_fleet(self):
        """Create a full fleet of aliens."""
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number * 2 * alien_width,
                                   row_number * 2 * alien_height)

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit.
                self._ship_hit(self.ship)
                break

    def _ship_hit(self, ship):
        """Respond to the ship being hit by an alien."""
        if ship == self.ship:
            if self.stats.ships_left > 0:
                self.stats.ships_left -= 1
                self.sb.prep_ships()
            else:
                self.game_active = False
                pygame.mouse.set_visible(True)
        elif ship == self.ship2:
            if self.stats.ship2_left > 0:
                self.stats.ship2_left -= 1
                self.sb.prep_ships()
            else:
                self.game_active = False
                pygame.mouse.set_visible(True)

        # Get rid of any remaining bullets and aliens.
        self.bullets.empty()
        self.alien_bullets.empty()
        self.aliens.empty()

        # Create a new fleet and center the ship(s).
        self._create_fleet()
        self.ship.center_ship()
        if self.two_player_mode:
            self.ship2.center_ship()

        # Pause.
        sleep(0.5)

    def _alien_fire_bullet(self):
        """Create a new alien bullet and add it to the alien bullets group."""
        if len(self.alien_bullets) < self.settings.alien_bullets_allowed and self.aliens:
            firing_alien = random.choice(self.aliens.sprites())
            new_bullet = AlienBullet(self, firing_alien)
            self.alien_bullets.add(new_bullet)

    def _update_alien_bullets(self):
        """Update position of alien bullets and get rid of old bullets."""
        # Update bullet positions.
        self.alien_bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)

        # Check for alien bullet-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            self._ship_hit(self.ship)
        if self.two_player_mode and pygame.sprite.spritecollideany(self.ship2, self.alien_bullets):
            self._ship_hit(self.ship2)

    def _show_cover(self):
        """Display the cover image."""
        self.screen.blit(self.cover_image, (0, 0))  # 先绘制封面
        if self.mode_selection_active:
            self.single_player_button.draw_button()  # 绘制单人游戏按钮
            self.two_player_button.draw_button()  # 绘制双人游戏按钮
        else:
            self.play_button.draw_button()  # 绘制Play按钮
            self.exit_button.draw_button()  # 绘制Exit按钮
    
        # 更新屏幕以显示封面
        pygame.display.flip()

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        if self.game_active:
            self.screen.blit(self.bg_image, (0, 0))  # 仅在游戏激活时绘制背景
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()  
            for bullet in self.alien_bullets.sprites():
                bullet.draw_bullet()
            self.ship.blitme()
            if self.two_player_mode:
                self.ship2.blitme()
            self.aliens.draw(self.screen)

            # Draw the score information.
            self.sb.show_score()
        else:
            self.screen.blit(self.cover_image, (0, 0))  # 先绘制封面
            if self.mode_selection_active:
                self.single_player_button.draw_button()  # 绘制单人游戏按钮
                self.two_player_button.draw_button()  # 绘制双人游戏按钮
            else:
                self.play_button.draw_button()  # 绘制Play按钮
                self.exit_button.draw_button()  # 绘制Exit按钮

        pygame.display.flip()

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()