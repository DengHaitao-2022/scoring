import pygame

class Button:
    def __init__(self, ai_game, msg, position):
        """Initialize button attributes."""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # Set dimensions and properties of the button
        self.width, self.height = 200, 50
        self.button_color =(173, 216, 230)  # 浅蓝色
        self.text_color = (0, 0, 0)  # 黑色
        self.font = pygame.font.SysFont(None, 48)
       

        # Create the button's rect object and center it
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = position

        # Prep the button message
        self.prep_msg(msg)

    def prep_msg(self, msg):
        """Turn the msg into a rendered image and center it on the button."""
        self.msg_image = self.font.render(msg, True, self.text_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        """Draw blank button and then draw the message and image."""
        self.screen.fill(self.button_color, self.rect)  # 填充按钮颜色
        self.screen.blit(self.msg_image, self.msg_image_rect)  # 绘制文本
    def check_click(self, mouse_pos):
        """Check if the button is clicked."""
        return self.rect.collidepoint(mouse_pos)
