import numpy as np
from YahtzeeGame import YahtzeeGame


class YahtzeePositionCostOptimizer:
    @staticmethod
    def css(input_list):
        # convert a list to a comma-separated string
        return f'[{", ".join(str(i) for i in input_list)}]'

    @staticmethod
    def random_change(position_costs, change_size):
        position_to_change = np.random.randint(0, YahtzeeGame.NUM_SLOTS)
        choices = np.array([-1, 1], dtype=np.int8)
        change_direction = np.random.choice(choices)
        new_position_costs = np.copy(position_costs)
        new_position_costs[position_to_change] += change_size * change_direction
        return new_position_costs

    def try_random_position_costs(self, num_tries, num_iterations_each_try, dice_type, position_costs=None, debug=False, dice_format=None):
        change_size = 1
        best_average_score = None
        best_position_costs = None
        if position_costs is None:
            # here's a good starting point
            position_costs = np.random.randint(0, 30, YahtzeeGame.NUM_SLOTS)
            upper_section_cost_multiplier = np.random.randint(1, 4)
            for k in range(YahtzeeGame.UPPER_SECTION_END + 1):
                position_costs[k] = upper_section_cost_multiplier * (k + 1)
            position_costs[YahtzeeGame.CHANCE] = 10
            position_costs[YahtzeeGame.THREE_OF_A_KIND] = position_costs[YahtzeeGame.CHANCE] - 1
            position_costs[YahtzeeGame.FOUR_OF_A_KIND] = position_costs[YahtzeeGame.THREE_OF_A_KIND] - 1
            position_costs[YahtzeeGame.LARGE_STRAIGHT] = 0
            position_costs[YahtzeeGame.YAHTZEE] = 0
            position_costs[YahtzeeGame.BONUS_YAHTZEE] = 0
        yg = YahtzeeGame(dice_type, position_costs, debug, dice_format=dice_format)
        for i in range(num_tries):
            game_scores = np.zeros(num_iterations_each_try, dtype=np.int32)
            for j in range(num_iterations_each_try):
                yg.reset_game(position_costs)
                game_scores[j] = yg.play_game()
            average_score = np.mean(game_scores)
            if len(game_scores) == 1:
                sem = 0
            else:
                sem = np.std(game_scores, ddof=1) / len(game_scores)**0.5  # standard error of the mean, using unbiased variance
            if best_average_score is None or average_score > best_average_score:
                best_average_score = average_score
                best_score_sem = sem
                best_position_costs = position_costs
            print(f'On try {i} with position costs {self.css(position_costs)}')
            print(f'average score = {np.around(average_score,1)} +/- {np.around(sem, 1)}, '
                  f'best average score so far = {np.around(best_average_score,1)} +/-{np.around(best_score_sem, 1)}')
            # try a small change from our best position_costs so far
            position_costs = self.random_change(best_position_costs, change_size)
        print(f'best average score = {np.around(best_average_score,1)} +/- {np.around(best_score_sem,1)}')
        print(f'best position costs = {self.css(best_position_costs)}')
        self.position_costs = best_position_costs