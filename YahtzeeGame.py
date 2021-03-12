import numpy as np
import itertools
from DiceSet import DiceSet


class GameLog:
    def __init__(self):
        self.log = []

    def add_step(self, dice_values, dice_fixed, position_taken, score):
        self.log.append([dice_values, dice_fixed, position_taken, score])

    def print(self):
        print(f'----Game log----')
        for line in self.log:
            dice_values, dice_fixed, position_name, score = line
            if dice_fixed is not None:
                newly_rolled = str(dice_values)
                for digit in str(dice_fixed):
                    index = newly_rolled.find(str(digit))
                    newly_rolled = newly_rolled[0: index] + newly_rolled[index + 1:]
                print(f'kept {dice_fixed}, rolled {newly_rolled}')
            elif position_name is not None:
                print(f'used {dice_values} for {position_name} with score {score}')
            else:
                print(f'rolled {dice_values}')
        print(f'----End of game log----')


class YahtzeeGame:
    # class variables
    UPPER_SECTION_END = 5
    THREE_OF_A_KIND = 6
    FOUR_OF_A_KIND = 7
    FULL_HOUSE = 8
    SMALL_STRAIGHT = 9
    LARGE_STRAIGHT = 10
    YAHTZEE = 11
    BONUS_YAHTZEE = 12
    CHANCE = 13
    NUM_SLOTS = 14

    UPPER_SECTION_MASK = np.array([1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.int8)
    LOWER_SECTION_MASK = -1 * (UPPER_SECTION_MASK - 1)
    BONUS_YAHTZEE_MASK = np.ones(NUM_SLOTS, dtype=np.int8)
    BONUS_YAHTZEE_MASK[BONUS_YAHTZEE] = 0
    POSITION_MULTIPLIER = np.array([10000, 1000, 100, 10, 1], dtype=np.int32)

    @staticmethod
    def position_name(position):
        if position <= YahtzeeGame.UPPER_SECTION_END:
            return f'{position + 1}s'
        elif position == YahtzeeGame.THREE_OF_A_KIND:
            return "Three of a Kind"
        elif position == YahtzeeGame.FOUR_OF_A_KIND:
            return "Four of a Kind"
        elif position == YahtzeeGame.FULL_HOUSE:
            return "Full House"
        elif position == YahtzeeGame.SMALL_STRAIGHT:
            return "Small Straight"
        elif position == YahtzeeGame.LARGE_STRAIGHT:
            return "Large Straight"
        elif position == YahtzeeGame.YAHTZEE:
            return "Yahtzee"
        elif position == YahtzeeGame.BONUS_YAHTZEE:
            return "Bonus Yahtzee"
        elif position == YahtzeeGame.CHANCE:
            return "Chance"

    @classmethod
    def dice_values_to_num(cls, dice_values):
        if dice_values is None:
            return None
        else:
            num = np.dot(dice_values, cls.POSITION_MULTIPLIER[-len(dice_values):])
            return num

    @classmethod
    def score_dice(cls, dice_values):
        position_scores = np.zeros(cls.NUM_SLOTS, dtype=np.int8)
        dice_sum = np.sum(dice_values)
        # upper section
        for position in range(6):
            position_dice_value = position + 1
            position_scores[position] = position_dice_value * np.count_nonzero(dice_values == position_dice_value)
        # three and four of a kind
        unique, counts = np.unique(dice_values, return_counts=True)
        for i in range(len(counts)):
            if counts[i] >= 3:
                position_scores[cls.THREE_OF_A_KIND] = dice_sum
            if counts[i] >= 4:
                position_scores[cls.FOUR_OF_A_KIND] = dice_sum
            if counts[i] == 5:
                position_scores[cls.YAHTZEE] = 50
                position_scores[cls.BONUS_YAHTZEE] = 100
        # full house
        if len(counts) == 2:
            if counts[0] * counts[1] == 6:
                # it's a full house
                position_scores[cls.FULL_HOUSE] = 25
        # small and large straights
        dice_values.sort()
        in_a_row = 1
        last_value = dice_values[0]
        for i in range(1, len(dice_values)):
            if dice_values[i] == last_value + 1:
                in_a_row += 1
                if in_a_row == 4:  # need 4 in a row for small straight
                    position_scores[cls.SMALL_STRAIGHT] = 30  # score for small straight
                if in_a_row == 5:
                    position_scores[cls.LARGE_STRAIGHT] = 40  # score for small straight
            elif dice_values[i] > last_value + 1:
                in_a_row = 1
            last_value = dice_values[i]
        # chance
        position_scores[cls.CHANCE] = dice_sum
        return position_scores

    def __init__(self, dice_type, position_costs=None, debug=False, dice_format=None):
        self.debug = debug
        self.dice = DiceSet(dice_type, dice_format)
        self.reset_game(position_costs)
        self.calculate_dice_combination_scores()
        self.calculate_next_roll_possibilities()

    def reset_game(self, position_costs=None):
        self.rolls_left = 3
        self.scores = np.zeros(YahtzeeGame.NUM_SLOTS, dtype=np.int16)
        self.game_log = GameLog()
        self.position_available = np.ones(YahtzeeGame.NUM_SLOTS, dtype=np.int8)
        self.position_available[YahtzeeGame.BONUS_YAHTZEE] = 0  # not available until there's been a Yahtzee
        # position cost = opportunity cost of using up this position.
        if position_costs is None:
            self.position_costs = np.zeros_like(YahtzeeGame.UPPER_SECTION_MASK)
        else:
            self.position_costs = np.array(position_costs, dtype=np.int8)

    def calculate_dice_combination_scores(self):
        num_combinations = 252  # the number of combinations
        self.dice_scores = np.zeros((num_combinations, YahtzeeGame.NUM_SLOTS), dtype=np.int8)
        self.combination_ids = {}
        dice_score_id = 0
        for dice_value_list in itertools.combinations_with_replacement(DiceSet.POSSIBLE_VALUES, 5):
            values_array = np.array(dice_value_list, dtype=np.int8)
            num = self.dice_values_to_num(values_array)
            self.combination_ids[num] = dice_score_id
            self.dice_scores[dice_score_id, :] = self.score_dice(values_array)
            dice_score_id += 1

    def calculate_next_roll_possibilities(self):
        num_combinations = 209
        self.expected_value_if_rolled = np.zeros((num_combinations, YahtzeeGame.NUM_SLOTS), dtype=np.float)
        self.next_roll_probabilities = np.zeros((num_combinations, YahtzeeGame.NUM_SLOTS), dtype=np.float)
        fixed_value_list_id = 0

        for num_fixed in range(1, 5):
            num_to_roll = 5 - num_fixed
            for fixed_values in itertools.combinations_with_replacement(DiceSet.POSSIBLE_VALUES, num_fixed):
                num_rolls = 0
                num_nonzero_scores = np.zeros(YahtzeeGame.NUM_SLOTS, dtype=np.int8)
                scores = np.zeros(YahtzeeGame.NUM_SLOTS, dtype=np.int32)
                for roll_results in itertools.combinations_with_replacement(DiceSet.POSSIBLE_VALUES, num_to_roll):
                    full_list = np.array(fixed_values + roll_results, dtype=np.int8)
                    full_list.sort()
                    full_list_id = self.dice_values_to_id(full_list)
                    score = self.dice_scores[full_list_id, :]
                    num_nonzero_scores[score > 0] += 1
                    scores += score
                    num_rolls += 1
                # average_scores = 0 for positions we never get to
                possible_positions = (num_nonzero_scores > 0)
                average_scores = np.zeros_like(scores, dtype=np.int32)
                average_scores[possible_positions] = scores[possible_positions] / num_nonzero_scores[possible_positions]
                fixed_values_number = self.dice_values_to_num(fixed_values)
                self.combination_ids[fixed_values_number] = fixed_value_list_id
                self.expected_value_if_rolled[fixed_value_list_id] = average_scores
                self.next_roll_probabilities[fixed_value_list_id] = num_nonzero_scores / num_rolls
                fixed_value_list_id += 1

    def dice_values_to_id(self, dice_values):
        # dice_values must be sorted
        num = self.dice_values_to_num(dice_values)
        return self.combination_ids[num]

    def game_complete(self):
        return self.rounds_remaining() == 0

    def rounds_remaining(self):
        rounds_remaining = np.sum(np.dot(self.position_available, YahtzeeGame.BONUS_YAHTZEE_MASK))
        return rounds_remaining

    def total_score(self):
        upper_section = np.sum(self.scores * YahtzeeGame.UPPER_SECTION_MASK)
        if upper_section >= 63:
            bonus = 35
        else:
            bonus = 0
        lower_section = np.sum(self.scores * YahtzeeGame.LOWER_SECTION_MASK)
        total = upper_section + bonus + lower_section
        return total, upper_section, bonus, lower_section

    def is_taken(self, position):
        if position < YahtzeeGame.NUM_SLOTS:
            if position == YahtzeeGame.BONUS_YAHTZEE:
                return False  # bonus yahtzee has space for more
            else:
                return self.position_available[position] == 0
        else:
            raise Exception(f'Invalid position {position} '
                            f'{YahtzeeGame.position_name(position)} was passed to is_taken().')

    def best_dice_to_fix(self, dice_values):
        best_score = None
        best_fixed_values = None
        for num_fixed in range(1, 5):
            for fixed_values in itertools.combinations(dice_values, num_fixed):
                fixed_value_list_id = self.dice_values_to_id(fixed_values)
                score = self.expected_value(fixed_value_list_id)
                if best_score is None or score > best_score:
                    best_score = score
                    best_fixed_values = list(fixed_values)
        return best_fixed_values, best_score

    def expected_value(self, fixed_value_list_id):
        value_if_rolled = self.expected_value_if_rolled[fixed_value_list_id]
        feasible_values = value_if_rolled * self.position_available - self.position_costs
        prob = self.next_roll_probabilities[fixed_value_list_id]
        expected_value = 0
        sum_of_probabilities = 0
        for index in np.argsort(- 1 * feasible_values):
            # from largest to smallest
            adjusted_prob = min(prob[index], 1-sum_of_probabilities)
            sum_of_probabilities += adjusted_prob
            expected_value += feasible_values[index] * adjusted_prob
            if sum_of_probabilities >= 1:
                break
        return expected_value

    def best_position(self, dice_values):
        dice_value_id = self.dice_values_to_id(dice_values)
        dice_scores = self.dice_scores[dice_value_id, :]
        feasible_values = dice_scores * self.position_available - self.position_costs
        min_value = np.min(feasible_values)
        # make sure that infeasible numbers are not the max
        feasible_values[self.position_available == 0] = min_value - 1
        if dice_scores[YahtzeeGame.BONUS_YAHTZEE] == 0:
            # can only use the Bonus Yahtzee slot if we actually have a bonus yahtzee. Can't put a zero there.
            feasible_values[YahtzeeGame.BONUS_YAHTZEE] = min_value - 1
        pos = np.argmax(feasible_values)
        score = feasible_values[pos]  # value at pos
        return pos, score

    def recommended_next_step(self, dice_values):
        best_position, score = self.best_position(dice_values)
        if self.rolls_left > 0:
            best_fixed_values, expected_next_roll_score = self.best_dice_to_fix(dice_values)
        if self.rolls_left == 0 or score > expected_next_roll_score:
            return best_position, None
        else:
            return None, best_fixed_values

    def accept_score(self, position, dice_values):
        if self.is_taken(position):
            raise Exception(f'position {position} {YahtzeeGame.position_name(position)} was already taken.')
        else:
            dice_value_id = self.dice_values_to_id(dice_values)
            score = self.dice_scores[dice_value_id, position]
            # previous value of self.scores[position] will be zero,
            # except if this is a bonus yahtzee and there was a previous bonus yahtzee
            self.scores[position] += score
            if position != YahtzeeGame.BONUS_YAHTZEE:
                # mark as taken
                # bonus yahtzee slot can be used multiple times
                self.position_available[position] = 0
            if position == YahtzeeGame.YAHTZEE and score > 0:
                # if this was a yahtzee, then we can now score bonus yahtzees
                # bonus yahtzee not available if we put a zero in yahtzee
                self.position_available[YahtzeeGame.BONUS_YAHTZEE] = 1
            if self.debug:
                self.game_log.add_step(self.dice_values_to_num(dice_values), None,
                                       YahtzeeGame.position_name(position), score)
            self.rolls_left = 3
            return score

    def dice_rolled_manually(self, dice_fixed, dice_values):
        # used if rolling dice in a GUI
        self.rolls_left -= 1
        if self.debug:
            self.game_log.add_step(self.dice_values_to_num(dice_values), self.dice_values_to_num(dice_fixed), None, None)

    def roll_dice(self, dice_fixed):
        dice_values = self.dice.roll(dice_fixed)
        if self.debug:
            self.game_log.add_step(self.dice_values_to_num(dice_values), self.dice_values_to_num(dice_fixed), None, None)
        self.rolls_left -= 1
        return dice_values

    def play_game(self):
        if self.debug or self.dice.dice_type == DiceSet.DICE_TYPE_MANUAL:
            print(f'Starting game.')
        self.reset_game(self.position_costs)
        dice_to_fix = None
        while not self.game_complete():
            dice_values = self.roll_dice(dice_to_fix)
            if self.debug or self.dice.dice_type == DiceSet.DICE_TYPE_MANUAL:
                print(f'rolled {self.dice.dice_format(dice_values)}')
            position_to_take, dice_to_fix = self.recommended_next_step(dice_values)
            if dice_to_fix is not None:
                #  fix the recommended dice, and roll again
                if self.debug:
                    print(f'keeping {self.dice.dice_format(dice_to_fix)}, rolling again')
            else:
                # use the current dice for position_to_take
                score = self.accept_score(position_to_take, dice_values)
                if self.debug or self.dice.dice_type == DiceSet.DICE_TYPE_MANUAL:
                    print(f'used dice {self.dice.dice_format(dice_values)} '
                          f'for position {YahtzeeGame.position_name(position_to_take)} with score {score}')
                if self.dice.dice_type == DiceSet.DICE_TYPE_MANUAL:
                    print(f'===================')  # marker for new rolls of dice
                rounds_remaining = self.rounds_remaining()
                if rounds_remaining > 0 and (self.debug or self.dice.dice_type == DiceSet.DICE_TYPE_MANUAL):
                    print(f'- {rounds_remaining} rounds left -')
        total, upper_section, bonus, lower_section = self.total_score()
        if self.debug:
            self.game_log.print()
        if self.debug or self.dice.dice_type == DiceSet.DICE_TYPE_MANUAL:
            self.print_score_sheet()
        return total

    def print_score_sheet(self):
        total, upper_section, bonus, lower_section = self.total_score()
        print(f'===========SCORE SHEET================')
        for pos in range(YahtzeeGame.NUM_SLOTS):
            print(f'{YahtzeeGame.position_name(pos)}: {self.scores[pos]}')
            if pos == YahtzeeGame.UPPER_SECTION_END:
                print(f'===')
                print(f'Upper section: {upper_section}')
                print(f'Bonus: {bonus}')
                print(f'===')
        print(f'===')
        print(f'Lower section: {lower_section}')
        print(f'===')
        print(f'FINAL SCORE: {total}')
