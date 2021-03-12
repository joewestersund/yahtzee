import random
import numpy as np


class DiceSet:
    POSSIBLE_VALUES = [1, 2, 3, 4, 5, 6]
    DICE_TYPE_AUTO = 1
    DICE_TYPE_MANUAL = 2

    @staticmethod
    def parse_dice_values(user_entered_str):
        user_str = user_entered_str.replace(" ", "")  # replace any spaces
        if user_str.isdigit():
            num = int(user_str)
            digits = []
            while num > 0:
                digit = num % 10
                if digit < 1 or digit > 6:
                    return None  # could not parse
                digits.append(digit)
                num = num // 10
            return digits
        else:
            return None

    @staticmethod
    def default_format(x):
        return x

    def __init__(self, dice_type=DICE_TYPE_AUTO, dice_format=None):
        self.dice_values = np.ndarray(5, dtype=np.byte)
        self.dice_type = dice_type
        if dice_type == DiceSet.DICE_TYPE_AUTO:
            # initialize the dice
            self.roll(None)
        if dice_format is None:
            self.dice_format = self.default_format  # assign function to this value
        else:
            self.dice_format = dice_format

    def roll(self, fixed):
        if self.dice_type == DiceSet.DICE_TYPE_MANUAL:
            example_str = "12345"
            if fixed is None:
                fix_str = ""
                dice_to_roll = 5
            else:
                fix_str = f'fixed dice: {self.dice_format(fixed)}. '
                dice_to_roll = 5 - len(fixed)
            print(f'{fix_str}roll {dice_to_roll} dice.')
            while True:
                prompt = f'values of the {dice_to_roll} dice: '
                input_str = input(prompt)
                if input_str == "exit":
                    print(f'exiting program')
                    exit()
                int_list = self.parse_dice_values(input_str)
                if int_list is not None and len(int_list) == dice_to_roll:
                    break
                else:
                    print(f'Enter {dice_to_roll} digit(s), like {example_str[0:dice_to_roll]}')
            fix_index = 0
            int_list_index = 0
            for i in range(len(self.dice_values)):
                if fixed is None or fix_index == len(fixed) or self.dice_values[i] != fixed[fix_index]:
                    self.dice_values[i] = int_list[int_list_index]
                    int_list_index += 1
                else:
                    fix_index += 1
            self.dice_values.sort()  # results always sorted
            return self.dice_values
        else:
            # automatically roll dice
            fix_index = 0
            for i in range(len(self.dice_values)):
                if fixed is None or fix_index == len(fixed) or self.dice_values[i] != fixed[fix_index]:
                    self.dice_values[i] = random.randint(1, 6)
                else:
                    fix_index += 1
            self.dice_values.sort()  # results always sorted
            return self.dice_values
