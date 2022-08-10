__doc__ = """
Original code of Dice Math, by Al Sweigart
The Big Book of Small Python Projects 81 Easy Practice Programs by Al Sweigart
"""
# --------------------------------------------- library --------------------------------------------- #
from random import choice, randint

# --------------------------------------------- Variables --------------------------------------------- #
DICE_WIDTH: int = 9
DICE_HEIGHT: int = 5
CANVAS_WIDTH: int = 50
CANVAS_HEIGHT: int = 17 - 3 # -3 for room to enter the sum at the bottom.
MAX_POINT_TO_GET_VICTORY: int = 100

# The duration is in seconds:
QUIZ_DURATION: int = 20 # (!) Try changing this to 10 or 60.
MIN_DICE: int = 2 # (!) Try changing this to 1 or 5.
MAX_DICE: int = 6 # (!) Try changing this to 14.

# (!) Try changing these to different numbers:
REWARD: int = 5 # (!) Points awarded for correct answers.
PENALTY: int = 5 # (!) Points removed for incorrect answers.
# (!) Try setting PENALTY to a negative number to give points for wrong answers!

# Special char:
DOWNRIGHT: str = chr(9484) # Character 9484 is '┌'
DOWNLEFT: str = chr(9488) # Character 9488 is '┐'
UPRIGHT: str = chr(9492) # Character 9492 is '└'
UPLEFT: str = chr(9496) # Character 9496 is '┘'
UPDOWN: str = chr(9474) # Character 9474 is '│'
LEFTRIGHT: str = chr(9472) # Character 9472 is '─'

# Dice faces:
D1: tuple = ([
    '┌───────┐',
    '│       │',
    '│   @   │',
    '│       │',
    '└───────┘'
], 1)

D2a: tuple = ([
    '┌───────┐',
    '│     @ │',
    '│       │',
    '│ @     │',
    '└───────┘'
], 2)

D2b: tuple = ([
    '┌───────┐',
    '│ @     │',
    '│       │',
    '│     @ │',
    '└───────┘'
], 2)

D3a: tuple = ([
    '┌───────┐',
    '│     @ │',
    '│   @   │',
    '│ @     │',
    '└───────┘'
], 3)

D3b: tuple = ([
    '┌───────┐',
    '│ @     │',
    '│   @   │',
    '│     @ │',
    '└───────┘'
], 3)

D4: tuple = ([
    '┌───────┐',
    '│ @   @ │',
    '│       │',
    '│ @   @ │',
    '└───────┘'
], 4)

D5: tuple = ([
    '┌───────┐',
    '│ @   @ │',
    '│   @   │',
    '│ @   @ │',
    '└───────┘'
], 5)

D6a: tuple = ([
    '┌───────┐',
    '│ @   @ │',
    '│ @   @ │',
    '│ @   @ │',
    '└───────┘'
], 6)

D6b: tuple = ([
    '┌───────┐',
    '│ @ @ @ │',
    '│       │',
    '│ @ @ @ │',
    '└───────┘'
], 6)

ALL_DICE: list = [D1, D2a, D2b, D3a, D3b, D4, D5, D6a, D6b]

BANNER: str = f"""
{__doc__}
┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐┌───────┐
│       ││     @ ││ @     ││     @ ││ @     ││ @   @ ││ @   @ ││ @   @ ││ @ @ @ │
│   @   ││       ││       ││   @   ││   @   ││       ││   @   ││ @   @ ││       │
│       ││ @     ││     @ ││ @     ││     @ ││ @   @ ││ @   @ ││ @   @ ││ @ @ @ │
└───────┘└───────┘└───────┘└───────┘└───────┘└───────┘└───────┘└───────┘└───────┘

Forked From Dice Math, by Mehrdad Arman nasaB
Add up the sides of all the dice displayed on the screen. You have
{QUIZ_DURATION} seconds to answer as many as possible. You get {REWARD} points for each
correct answer and lose {PENALTY} point for each incorrect answer.
If you get {MAX_POINT_TO_GET_VICTORY} point (solve [{MAX_POINT_TO_GET_VICTORY // REWARD}] challenge) in {QUIZ_DURATION} seconds,
I will give you the VICTORY-FLAG!.

Commands:
>>> start : play game
>>> exit : good bye
>>> help : show this screen

When you send 'start', I will send to you dice challenge and you should send to me sum of dice on screen.
Just send me "number" or "Digit"
If I couldn't send to you challenge, restart me :) sockets are not fast same as cpu!
"""

# --------------------------------------------- Functions --------------------------------------------- #
def create_challenge() -> tuple:
    sum_answer: int = 0
    dice_faces: list = []
    for _ in range(randint(MIN_DICE, MAX_DICE)):
        dice: tuple = choice(ALL_DICE)
        dice_faces.append(dice[0]) # dice[0] contain the list of string of the dice face.
        sum_answer += dice[1] # dice[1] contain the integer number of pips on the face.

    # Contains (x, y) tuples of the top-left corner of each dice.
    top_left_dice_corners: list = []

    # Figure out where dice should go:
    for i in range(len(dice_faces)):
        while True:
            left: int = randint(0, CANVAS_WIDTH - DICE_WIDTH - 1)
            top: int = randint(0, CANVAS_HEIGHT - DICE_HEIGHT - 1)
            # Get the x, y coordinates for all four corners:
            #       left
            #       v
            # top > ┌───────┐ ^
            #       │ O   O │ │
            #       │   O   │ │ DICE_HEIGHT (5)
            #       │ O   O │ │
            #       └───────┘ v
            #       <───────>
            #       DICE_WIDTH (9)
            top_left_X: int = left
            top_left_Y: int = top
            top_right_X: int = left + DICE_WIDTH
            top_right_Y: int = top
            bottom_left_X: int = left
            bottom_left_Y: int = top + DICE_HEIGHT
            bottom_right_X: int = left + DICE_WIDTH
            bottom_right_Y: int = top + DICE_HEIGHT
            # Check if this die overlaps with previous dice.
            overlaps: bool = False
            
            for prev_dice_left, prev_dice_top in top_left_dice_corners:
                prev_dice_right: int = prev_dice_left + DICE_WIDTH
                prev_dice_bottom: int = prev_dice_top + DICE_HEIGHT
                # Check each corner of this dice to see if it is inside
                # of the area the previous die:
                for corner_X, corner_Y in (
                    (top_left_X, top_left_Y),
                    (top_right_X, top_right_Y),
                    (bottom_left_X, bottom_left_Y),
                    (bottom_right_X, bottom_right_Y)):
                    if (prev_dice_left <= corner_X < prev_dice_right) and (prev_dice_top <= corner_Y < prev_dice_bottom):
                        overlaps = True

            if not overlaps:
                # It doesn't overlap, so we can put it here:
                top_left_dice_corners.append((left, top))
                break
    return (top_left_dice_corners, dice_faces, sum_answer)

def create_canvas(top_left_dice_corners: list, dice_faces: list) -> dict:
    canvas: dict = {}
    # Loop over each dice:
    for i, (dice_left, dice_top) in enumerate(top_left_dice_corners):
        # Loop over each character in the dice's face:
        dice_face: list = dice_faces[i]
        for dx in range(DICE_WIDTH):
            for dy in range(DICE_HEIGHT):
                # Copy this character to the correct place on the canvas
                canvas_X: int = dice_left + dx
                canvas_Y: int = dice_top + dy
                # Note that in dieFace, a list of strings, the x and y are swapped:
                canvas[(canvas_X, canvas_Y)] = dice_face[dy][dx]
    return canvas

def show_canvas(canvas: dict) -> str:
    buffer: list = []
    for cy in range(CANVAS_HEIGHT):
        for cx in range(CANVAS_WIDTH):
            if canvas.get((cx, cy)) is None:
                buffer.append(' ')
            else:
                buffer.append(canvas.get((cx, cy)))
            # print(canvas.get((cx, cy)), end='')
        buffer.append('\n')
        # print() # Print a newline.
    return ''.join(buffer)

def check_answer(correct_answers: list, player_answers: list) -> tuple:
    correct_answer: int = 0
    incorrect_answer: int = 0
    for ca, pa in zip(correct_answers, player_answers):
        if ca == pa: correct_answer += 1
        else: incorrect_answer += 1
    # Display the final score:
    correct_answers.clear(); player_answers.clear()
    score: int = (correct_answer * REWARD) - (incorrect_answer * PENALTY)
    return (correct_answer, incorrect_answer, score)
