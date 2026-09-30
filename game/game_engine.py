import random
import pygame

from game.text_box import TextBox


class GameEngine:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.words = [
            "PYTHON",
            "PYGAME",
            "PLANET",
            "ROCKET",
            "GALAXY",
            "STREAM",
            "PUZZLE",
            "ALGORITHM"
        ]

        self.secret_word = ""
        self.scrambled_word = ""
        self.score = 0

        # Hint system
        self.revealed_indices = set()

        # Countdown timer
        self.round_time = 20
        self.round_start_time = 0
        self.time_up = False
        self.time_up_time = 0

        # Letter tile system
        self.available_letters = []
        self.rack_letters = []
        self.selected_rack_index = None

        self.feedback_msg = "Unscramble the letters above!"
        self.feedback_color = (210, 215, 225)

        self.input_box = TextBox(
            width // 2 - 130,
            330,
            160,
            46
        )

        self.submit_btn = pygame.Rect(
            width // 2 + 45,
            330,
            95,
            46
        )

        self.hint_btn = pygame.Rect(
            width // 2 + 150,
            330,
            75,
            46
        )

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_word = pygame.font.SysFont(None, 52)
        self.font_msg = pygame.font.SysFont(None, 26)
        self.font_btn = pygame.font.SysFont(None, 24)

        self.tile_font = pygame.font.SysFont(None, 36)
        self.tile_size = 48
        self.tile_gap = 8

        self.next_round()

    def scramble_string(self, word):

        letters = list(word)

        while True:

            random.shuffle(letters)
            shuffled = "".join(letters)

            if shuffled != word or len(word) <= 1:
                return shuffled

    def next_round(self):

        self.secret_word = random.choice(self.words)
        self.scrambled_word = self.scramble_string(self.secret_word)

        # Reset hints
        self.revealed_indices.clear()

        # Reset timer
        self.round_start_time = pygame.time.get_ticks()
        self.time_up = False
        self.time_up_time = 0

        # Reset letter tiles
        self.available_letters = list(self.scrambled_word)
        self.rack_letters = []
        self.selected_rack_index = None

        self.input_box.clear()

    def use_hint(self):

        for index in range(len(self.secret_word)):

            if index not in self.revealed_indices:

                self.revealed_indices.add(index)

                self.score = max(0, self.score - 1)

                self.feedback_msg = "Hint used! 1 point deducted."
                self.feedback_color = (240, 170, 50)

                return

    def submit_guess(self):

        if self.time_up:
            return

        guess = self.input_box.text.strip().upper()

        if not guess:

            self.feedback_msg = "Type a word before submitting!"
            self.feedback_color = (240, 170, 50)

            return

        # Existing guess validation is unchanged.
        is_correct = (guess == self.secret_word)

        if is_correct:

            self.score += 1
            self.feedback_msg = f"CORRECT! '{self.secret_word}' is right."
            self.feedback_color = (80, 230, 110)

            self.next_round()

        else:

            self.feedback_msg = "WRONG GUESS! Try again."
            self.feedback_color = (240, 80, 80)

            self.input_box.clear()

    def handle_tile_click(self, pos):

        # Don't allow tile interaction after timeout.
        if self.time_up:
            return

        # First check the rack.
        rack_start_x = self.width // 2 - (
            len(self.rack_letters) *
            (self.tile_size + self.tile_gap)
        ) // 2

        rack_y = 250

        for index in range(len(self.rack_letters)):

            x = rack_start_x + index * (
                self.tile_size + self.tile_gap
            )

            rect = pygame.Rect(
                x,
                rack_y,
                self.tile_size,
                self.tile_size
            )

            if rect.collidepoint(pos):

                # If another rack tile is selected,
                # swap the two tiles.
                if self.selected_rack_index is not None:

                    selected = self.selected_rack_index

                    self.rack_letters[selected], self.rack_letters[index] = (
                        self.rack_letters[index],
                        self.rack_letters[selected]
                    )

                    self.selected_rack_index = None

                else:

                    # Select this rack tile.
                    self.selected_rack_index = index

                return

        # Check available scrambled letters.
        available_start_x = self.width // 2 - (
            len(self.available_letters) *
            (self.tile_size + self.tile_gap)
        ) // 2

        available_y = 175

        for index in range(len(self.available_letters)):

            x = available_start_x + index * (
                self.tile_size + self.tile_gap
            )

            rect = pygame.Rect(
                x,
                available_y,
                self.tile_size,
                self.tile_size
            )

            if rect.collidepoint(pos):

                # Move the clicked letter to the rack.
                letter = self.available_letters.pop(index)
                self.rack_letters.append(letter)

                self.selected_rack_index = None

                return

    def handle_event(self, event):

        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:

            self.submit_guess()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if self.submit_btn.collidepoint(event.pos):

                self.submit_guess()

            elif self.hint_btn.collidepoint(event.pos):

                self.use_hint()

            else:

                self.handle_tile_click(event.pos)

    def update(self):

        if self.time_up:

            if pygame.time.get_ticks() - self.time_up_time >= 1000:
                self.next_round()

            return

        elapsed_time = (
            pygame.time.get_ticks() - self.round_start_time
        ) / 1000

        remaining_time = self.round_time - elapsed_time

        if remaining_time <= 0:

            self.time_up = True
            self.time_up_time = pygame.time.get_ticks()

            # Reveal the complete correct answer.
            self.revealed_indices = set(
                range(len(self.secret_word))
            )

            self.feedback_msg = "TIME'S UP!"
            self.feedback_color = (240, 80, 80)

    def draw_tile(self, screen, letter, x, y, selected=False):

        tile_rect = pygame.Rect(
            x,
            y,
            self.tile_size,
            self.tile_size
        )

        if selected:

            tile_color = (255, 190, 70)

        else:

            tile_color = (55, 65, 80)

        pygame.draw.rect(
            screen,
            tile_color,
            tile_rect,
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            (220, 220, 220),
            tile_rect,
            width=2,
            border_radius=6
        )

        letter_surf = self.tile_font.render(
            letter,
            True,
            (255, 255, 255)
        )

        screen.blit(
            letter_surf,
            (
                tile_rect.centerx -
                letter_surf.get_width() // 2,
                tile_rect.centery -
                letter_surf.get_height() // 2
            )
        )

    def render(self, screen):

        screen.fill((26, 30, 38))

        title_surf = self.font_title.render(
            "Word Scramble Arena",
            True,
            (245, 245, 245)
        )

        screen.blit(
            title_surf,
            (
                self.width // 2 -
                title_surf.get_width() // 2,
                25
            )
        )

        score_surf = self.font_msg.render(
            f"Score: {self.score}",
            True,
            (255, 220, 80)
        )

        screen.blit(
            score_surf,
            (
                self.width // 2 -
                score_surf.get_width() // 2,
                70
            )
        )

        # -------------------------
        # Countdown timer
        # -------------------------

        if self.time_up:

            remaining_time = 0

        else:

            elapsed_time = (
                pygame.time.get_ticks() -
                self.round_start_time
            ) / 1000

            remaining_time = max(
                0,
                self.round_time - elapsed_time
            )

        timer_text = self.font_msg.render(
            f"Time: {remaining_time:.1f}s",
            True,
            (255, 255, 255)
        )

        screen.blit(
            timer_text,
            (
                self.width // 2 -
                timer_text.get_width() // 2,
                100
            )
        )

        timer_bar_width = 300
        timer_bar_height = 12

        timer_bar_x = (
            self.width // 2 -
            timer_bar_width // 2
        )

        timer_bar_y = 125

        pygame.draw.rect(
            screen,
            (70, 70, 80),
            (
                timer_bar_x,
                timer_bar_y,
                timer_bar_width,
                timer_bar_height
            ),
            border_radius=6
        )

        timer_fill_width = int(
            timer_bar_width *
            (remaining_time / self.round_time)
        )

        if timer_fill_width > 0:

            pygame.draw.rect(
                screen,
                (80, 200, 110),
                (
                    timer_bar_x,
                    timer_bar_y,
                    timer_fill_width,
                    timer_bar_height
                ),
                border_radius=6
            )

        # -------------------------
        # Hint / revealed pattern
        # -------------------------

        if self.revealed_indices:

            revealed_pattern = " ".join(
                self.secret_word[index]
                if index in self.revealed_indices
                else "_"
                for index in range(len(self.secret_word))
            )

            pattern_surf = self.font_word.render(
                revealed_pattern,
                True,
                (100, 200, 255)
            )

            screen.blit(
                pattern_surf,
                (
                    self.width // 2 -
                    pattern_surf.get_width() // 2,
                    145
                )
            )

        # -------------------------
        # Available letter tiles
        # -------------------------

        available_start_x = self.width // 2 - (
            len(self.available_letters) *
            (self.tile_size + self.tile_gap)
        ) // 2

        available_y = 175

        for index, letter in enumerate(self.available_letters):

            x = available_start_x + index * (
                self.tile_size + self.tile_gap
            )

            self.draw_tile(
                screen,
                letter,
                x,
                available_y
            )

        # -------------------------
        # Rearrangement rack
        # -------------------------

        rack_label = self.font_msg.render(
            "Your arrangement:",
            True,
            (210, 215, 225)
        )

        screen.blit(
            rack_label,
            (
                self.width // 2 -
                rack_label.get_width() // 2,
                235
            )
        )

        rack_start_x = self.width // 2 - (
            len(self.rack_letters) *
            (self.tile_size + self.tile_gap)
        ) // 2

        rack_y = 260

        for index, letter in enumerate(self.rack_letters):

            x = rack_start_x + index * (
                self.tile_size + self.tile_gap
            )

            self.draw_tile(
                screen,
                letter,
                x,
                rack_y,
                selected=(
                    index == self.selected_rack_index
                )
            )

        # -------------------------
        # Input / buttons
        # -------------------------

        self.input_box.render(screen)

        # SUBMIT
        pygame.draw.rect(
            screen,
            (50, 150, 85),
            self.submit_btn,
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            (220, 220, 220),
            self.submit_btn,
            width=2,
            border_radius=6
        )

        btn_text = self.font_btn.render(
            "SUBMIT",
            True,
            (255, 255, 255)
        )

        screen.blit(
            btn_text,
            (
                self.submit_btn.centerx -
                btn_text.get_width() // 2,
                self.submit_btn.centery -
                btn_text.get_height() // 2
            )
        )

        # HINT
        pygame.draw.rect(
            screen,
            (70, 100, 170),
            self.hint_btn,
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            (220, 220, 220),
            self.hint_btn,
            width=2,
            border_radius=6
        )

        hint_text = self.font_btn.render(
            "HINT",
            True,
            (255, 255, 255)
        )

        screen.blit(
            hint_text,
            (
                self.hint_btn.centerx -
                hint_text.get_width() // 2,
                self.hint_btn.centery -
                hint_text.get_height() // 2
            )
        )

        # -------------------------
        # Feedback
        # -------------------------

        feedback_surf = self.font_msg.render(
            self.feedback_msg,
            True,
            self.feedback_color
        )

        screen.blit(
            feedback_surf,
            (
                self.width // 2 -
                feedback_surf.get_width() // 2,
                395
            )
        )