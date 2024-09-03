from struct import unpack

import pygame
from numpy import clip

PWM_PERIOD = 100

SIZE = 2

UNIT = 100 * SIZE
WINDOW_SIZE = (4 * UNIT, 3 * UNIT)
FONT_SIZE = 10 * SIZE
FONT_INFLATION = 20 * SIZE
HALF_A = 10 * SIZE
A = HALF_A * 2
WIDTH = 4 * SIZE

BACK = (0, 0, 0)
FRONT = (255, 255, 255)
LOCK = (255, 0, 0)
ACTUAL = (128, 128, 255)
TARGET = (128, 128, 128)
OUTPUT = (255, 128, 0)
# MOUSE_ON = (255, 255, 0)
CLICK_MAX_MILLISECONDS = 200
MAX_SPEED_CLIP = 1
MIN_PID_CLIP = 0
MAX_PID_CLIP = 127

SPEED_CONTROL = 0.9


class Dummy:
    def __init__(self, enabled: bool, input_protocol: int):
        self.force_stop = False
        self.enabled = enabled
        self.input_protocol = input_protocol

        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("DejaVuSansMono", FONT_SIZE)
        self.screen = pygame.display.set_mode(WINDOW_SIZE)

        self.left_rect = self.right_rect = self.top_rect = self.bottom_rect = pygame.Rect(0, 0, 0, 0)
        self.text_rect = [[[pygame.Rect(0, 0, 0, 0)] * 3] * 4] * 2
        self.left_lock = False
        self.right_lock = False
        self.mouse_down_tick = -1000
        self.mouse_pos = (0, 0)
        self.left_mouse_offset = None
        self.right_mouse_offset = None
        self.mouse_on_text = None

        self.status_code = 0
        self.motor = [0.0, 0.0]
        self.brush = False
        self.back_open = False
        self.motor_PID = [[15, 10, 40, 10, 0, 10, 5, 0], [15, 10, 40, 10, 0, 10, 5, 0]]

        self.stm_input = bytes((1,) * 96) if input_protocol == 128 else bytes((1,) * 17)
        self.unpacked_stm_input = None
        self.output = bytes((0,) * 16)

    def get_output(self, stm_input: bytes, unpacked_stm_input) -> bytes:
        """
        Process the input and generate the output.

        Args:
            stm_input (bytes): The input data.
            unpacked_stm_input: The unpacked input data.

        Returns:
            bytes: The generated output.
        """
        # Rest of the code...
        if stm_input is not None:
            self.stm_input = stm_input
        if unpacked_stm_input is not None:
            self.unpacked_stm_input = unpacked_stm_input

        self.mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if (
                event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                and (event.key in [pygame.K_ESCAPE, pygame.K_q])
            ):
                exit()
            elif self.enabled:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_down_tick = pygame.time.get_ticks()
                    if self.top_rect.collidepoint(self.mouse_pos):
                        self.brush = not self.brush
                    if self.bottom_rect.collidepoint(self.mouse_pos):
                        self.back_open = not self.back_open
                    if self.left_rect.collidepoint(self.mouse_pos):
                        self.left_lock = True
                        self.left_mouse_offset = self.mouse_pos[1] - self.left_rect.centery
                    if self.right_rect.collidepoint(self.mouse_pos):
                        self.right_lock = True
                        self.right_mouse_offset = self.mouse_pos[1] - self.right_rect.centery
                elif event.type == pygame.MOUSEBUTTONUP:
                    if pygame.time.get_ticks() - self.mouse_down_tick < CLICK_MAX_MILLISECONDS:
                        if self.left_mouse_offset is not None:
                            self.left_lock = False
                        if self.right_mouse_offset is not None:
                            self.right_lock = False
                    self.left_mouse_offset = None
                    self.right_mouse_offset = None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_i:
                        self.brush = not self.brush
                    elif event.key == pygame.K_o:
                        self.back_open = not self.back_open
                elif event.type == pygame.MOUSEWHEEL:
                    if self.mouse_on_text is not None:
                        print(self.mouse_on_text)
                        a, b = (self.mouse_on_text[0], self.mouse_on_text[1] * 2 + self.mouse_on_text[2] // 2)
                        self.motor_PID[a][b] += event.y
                        self.motor_PID[a][b] = int(clip(self.motor_PID[a][b], MIN_PID_CLIP, MAX_PID_CLIP))

        if pygame.mouse.get_pressed()[0]:
            if self.left_mouse_offset is not None:
                self.motor[0] = float(
                    clip(
                        (1.5 * UNIT - pygame.mouse.get_pos()[1] + self.left_mouse_offset) / (0.5 * UNIT),
                        -MAX_SPEED_CLIP,
                        MAX_SPEED_CLIP,
                    )
                )
            if self.right_mouse_offset is not None:
                self.motor[1] = float(
                    clip(
                        (1.5 * UNIT - pygame.mouse.get_pos()[1] + self.right_mouse_offset) / (0.5 * UNIT),
                        -MAX_SPEED_CLIP,
                        MAX_SPEED_CLIP,
                    )
                )

        keys = pygame.key.get_pressed()

        self.force_stop = keys[pygame.K_s]
        self.status_code = 1 if keys[pygame.K_r] else 0

        motor_prev = self.motor

        self.motor = [0, 0]
        if keys[pygame.K_UP]:
            if keys[pygame.K_LEFT]:
                self.motor = [0, 1]
            elif keys[pygame.K_RIGHT]:
                self.motor = [1, 0]
            else:
                self.motor = [1, 1]
        elif keys[pygame.K_DOWN]:
            if keys[pygame.K_LEFT]:
                self.motor = [-1, 0]
            elif keys[pygame.K_RIGHT]:
                self.motor = [0, -1]
            else:
                self.motor = [-1, -1]
        elif keys[pygame.K_LEFT]:
            self.motor = [-1, 1]
        elif keys[pygame.K_RIGHT]:
            self.motor = [1, -1]

        self.motor = [self.motor[0] * SPEED_CONTROL, self.motor[1] * SPEED_CONTROL]

        if self.left_lock:
            self.motor[0] = motor_prev[0]
        if self.right_lock:
            self.motor[1] = motor_prev[1]

        output = (
            [
                128,
                self.status_code,
                int(self.motor[1] * PWM_PERIOD),
                int(self.motor[0] * PWM_PERIOD),
                int(self.brush),
                int(self.back_open),
                0,
                0,
            ]
            + self.motor_PID[1]
            + self.motor_PID[0]
        )

        for i in range(len(output)):
            if output[i] < 0:
                output[i] += 256

        self.output = bytes(output)

        self.draw()

        return self.output

    def drawn_rect(self, x, y_normalized, color, width=0) -> pygame.Rect:
        """
        Draw a rectangle on the screen.

        Args:
            self (object): The object instance.
            x (int): The x-coordinate of the top-left corner of the rectangle.
            y_normalized (float): The normalized y-coordinate of the top-left corner of the rectangle.
            color (tuple): The color of the rectangle in RGB format.
            width (int, optional): The width of the rectangle's outline. Defaults to 0.

        Returns:
            rect (pygame.Rect): The rectangle object that was drawn.
        """
        rect = pygame.Rect(x - HALF_A, 1.5 * UNIT - y_normalized * 0.5 * UNIT - HALF_A, A, A)
        pygame.draw.rect(self.screen, color, rect, width)
        return rect

    def draw_text(self) -> None:
        """
        Render and display text on the screen.

        - This method is responsible for rendering and displaying various text elements on the screen.
        - It iterates over the motor_PID list and renders the values at specific positions using the font provided.
        - The rendered text is then blitted onto the screen at the calculated offset positions.
        - The method also renders and displays the output and stm_input values at specific positions on the screen.

        Returns:
            None
        """

        def j_offset(_j):
            """
            Calculate the offset value based on the input parameter _j.

            Args:
                _j (int): The input parameter representing the value of _j.

            Returns:
                float: The calculated offset value.
            """
            return 1.7 * UNIT if _j == 3 else UNIT + 0.5 * UNIT * j

        def j_text(_j):
            """
            Returns "<<" if _j is equal to 3, otherwise returns "/"

            Args:
                _j (int): The value to be checked

            Returns:
                str: The resulting string
            """
            return "<<" if _j == 3 else "/"

        if self.input_protocol == 128:
            self.mouse_on_text = None
            for i in range(2):
                for j in range(4):
                    text = self.font.render(str(self.motor_PID[i][2 * j]), True, FRONT)
                    rect = text.get_rect()
                    offset = (0.5 * UNIT + 2.5 * UNIT * i - rect.centerx, j_offset(j) - rect.centery)
                    self.text_rect[i][j][0] = rect.move(offset).inflate(FONT_INFLATION, FONT_INFLATION)
                    if self.text_rect[i][j][0].collidepoint(self.mouse_pos) and self.enabled:
                        self.mouse_on_text = i, j, 0
                        text = self.font.render(str(self.motor_PID[i][2 * j]), True, BACK, FRONT)
                    self.screen.blit(text, offset)

                    text = self.font.render(j_text(j), True, FRONT)
                    rect = text.get_rect()
                    offset = (0.75 * UNIT + 2.5 * UNIT * i - rect.centerx, j_offset(j) - rect.centery)
                    self.text_rect[i][j][1] = rect.move(offset).inflate(FONT_INFLATION, FONT_INFLATION)
                    self.screen.blit(text, offset)

                    text = self.font.render(str(self.motor_PID[i][2 * j + 1]), True, FRONT)
                    rect = text.get_rect()
                    offset = (UNIT + 2.5 * UNIT * i - rect.centerx, j_offset(j) - rect.centery)
                    self.text_rect[i][j][2] = rect.move(offset).inflate(FONT_INFLATION, FONT_INFLATION)
                    if self.text_rect[i][j][2].collidepoint(self.mouse_pos) and self.enabled:
                        self.mouse_on_text = i, j, 2
                        text = self.font.render(str(self.motor_PID[i][2 * j + 1]), True, BACK, FRONT)
                    self.screen.blit(text, offset)

                text = self.font.render(
                    str(unpack("<i", self.stm_input[52 + 32 * i : 56 + 32 * i])[0]), True, ACTUAL
                )
                rect = text.get_rect()
                offset = (0.75 * UNIT + 2.5 * UNIT * i - rect.centerx, 1.3 * UNIT - rect.centery)
                self.screen.blit(text, offset)

        text = self.font.render(self.output.hex(" "), True, FRONT)
        self.screen.blit(text, (0.2 * UNIT, 0.2 * UNIT))
        text = self.font.render(self.stm_input.hex(" "), True, FRONT)
        self.screen.blit(text, (0.2 * UNIT, 0.3 * UNIT))

    def draw(self) -> None:
        """
        Draw the screen based on the input protocol and other parameters.

        - If the input protocol is 128, it draws rectangles based on specific values from the `stm_input` array.
        - If the input protocol is 127, it draws rectangles based on either the `unpacked_stm_input` array or
        specific values from the `stm_input` array.
        - If `enabled` is True, it draws rectangles based on the `motor` and `left_lock`/`right_lock` values.
        - If `enabled` is False and the input protocol is 128, it draws rectangles based on specific values from
        the `stm_input` array.
        - It also draws rectangles based on the `brush` and `back_open` values.
        - Finally, it displays the text and updates the display.

        Returns:
            None
        """
        self.screen.fill(BACK)

        if self.input_protocol == 128:

            self.drawn_rect(1.5 * UNIT, unpack("<i", self.stm_input[48:52])[0] / 256 / 100, OUTPUT)
            self.drawn_rect(1.5 * UNIT, unpack("<i", self.stm_input[40:44])[0] / 256 / 100, ACTUAL)
            self.drawn_rect(1.5 * UNIT, unpack("<i", self.stm_input[44:48])[0] / 256 / 100, TARGET)

            self.drawn_rect(2.5 * UNIT, unpack("<i", self.stm_input[80:84])[0] / 256 / 100, OUTPUT)
            self.drawn_rect(2.5 * UNIT, unpack("<i", self.stm_input[72:76])[0] / 256 / 100, ACTUAL)
            self.drawn_rect(2.5 * UNIT, unpack("<i", self.stm_input[76:80])[0] / 256 / 100, TARGET)

        elif self.input_protocol == 127:

            if self.unpacked_stm_input is None:
                self.drawn_rect(
                    1.5 * UNIT,
                    unpack("<h", self.stm_input[5:7])[0]
                    * 72000000
                    / 44
                    / unpack("<I", self.stm_input[1:5])[0]
                    / 90,
                    ACTUAL,
                )
                self.drawn_rect(
                    2.5 * UNIT,
                    unpack("<h", self.stm_input[11:13])[0]
                    * 72000000
                    / 44
                    / unpack("<I", self.stm_input[7:11])[0]
                    / 90,
                    ACTUAL,
                )
            else:
                self.drawn_rect(
                    1.5 * UNIT,
                    self.unpacked_stm_input[3] * 72000000 / 44 / self.unpacked_stm_input[1] / 90,
                    ACTUAL,
                )
                self.drawn_rect(
                    2.5 * UNIT,
                    self.unpacked_stm_input[2] * 72000000 / 44 / self.unpacked_stm_input[0] / 90,
                    ACTUAL,
                )

        if self.enabled:
            self.left_rect = self.drawn_rect(1.5 * UNIT, self.motor[0], LOCK if self.left_lock else FRONT)
            self.right_rect = self.drawn_rect(2.5 * UNIT, self.motor[1], LOCK if self.right_lock else FRONT)

        if self.enabled:
            self.top_rect = self.drawn_rect(2 * UNIT, 1, FRONT, 0 if self.brush else WIDTH)
            self.bottom_rect = self.drawn_rect(2 * UNIT, -1, FRONT, 0 if self.back_open else WIDTH)
        else:
            if self.input_protocol == 128:
                self.drawn_rect(2 * UNIT, 1, TARGET, 0 if int(self.stm_input[8]) == 1 else WIDTH)
                self.drawn_rect(2 * UNIT, -1, TARGET, 0 if int(self.stm_input[9]) == 1 else WIDTH)

        self.draw_text()

        pygame.display.flip()
