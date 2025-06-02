    def draw_settings_screen(self):
        """Draw the settings screen"""
        # Background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_GRAY)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.title_font.render("SETTINGS", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Settings options
        options = [
            f"Theme: {self.current_theme}",
            f"Player Mode: {self.player_mode}-Player",
            f"Sound: {'On' if self.sound_enabled else 'Off'}",
            "Back to Main Menu"
        ]
        
        y_pos = 250
        for i, option in enumerate(options):
            color = YELLOW if i == self.selected_option else WHITE
            option_text = self.font.render(option, True, color)
            self.screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, y_pos))
            y_pos += 60
            
        # Instructions
        instructions = self.small_font.render("Use UP/DOWN to navigate, ENTER to select, ESC to go back", True, LIGHT_GRAY)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 600))
        
    def draw_paused_screen(self):
        """Draw the paused screen overlay"""
        # Draw the game in the background
        self.draw_board()
        self.draw_coins()
        self.draw_striker()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Paused text
        paused = self.title_font.render("GAME PAUSED", True, WHITE)
        continue_text = self.font.render("Press ESC or P to Continue", True, WHITE)
        save_text = self.font.render("Press S to Save Game", True, WHITE)
        menu_text = self.font.render("Press M for Main Menu", True, WHITE)
        
        self.screen.blit(paused, (SCREEN_WIDTH // 2 - paused.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(save_text, (SCREEN_WIDTH // 2 - save_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
