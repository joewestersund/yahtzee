from YahtzeeGame import YahtzeeGame
from YahtzeePositionCostOptimizer import YahtzeePositionCostOptimizer
from DiceSet import DiceSet
from YahtzeeGUI import YahtzeeGUI

def dice_format(input_list):
    return "".join(str(i) for i in input_list)

def main():
    debug = False
    modes = ["optimize position_costs", "test GUI", "play text mode"]
    mode = 1
    #position_costs = [1, 2, 3, 4, 5, 6, 9, 5, 1, 3, 0, 0, 0, 10]
    #position_costs = [0, 2, 2, 6, 5, 7, 9, 5, 1, 4, 0, -1, 0, 11]  #average 222.4 +/- 1.8
    #position_costs = [1, 1, 2, 6, 5, 7, 10, 5, 1, 4, 0, -1, 1, 11]  # average 223.7 +/- 1.7
    #position_costs = [1, 1, 2, 6, 6, 7, 11, 5, 1, 4, 0, -1, 1, 9]  # best average score = 238.5 +/- 2.9
    #position_costs = [1, 1, 2, 6, 6, 7, 11, 5, 1, 5, 0, -3, 1, 9]  # best average score = 240.7 +/- 3.2
    #position_costs = [1, 1, 2, 5, 6, 7, 11, 6, 2, 4, 0, -3, 1, 9]  # best average score = 230.8 +/- 3.5
    position_costs = [1, 1, 2, 6, 6, 7, 11, 6, 2, 4, 0, -3, 1, 9]  # best average score = 231.6 +/- 3.2

    if mode == 0:
        pco = YahtzeePositionCostOptimizer()
        dice_type = DiceSet.DICE_TYPE_AUTO
        num_tries = 200
        num_iterations_each_try = 300
        pco.try_random_position_costs(num_tries, num_iterations_each_try, dice_type, position_costs, debug, dice_format)
    elif mode == 1:
        gui = YahtzeeGUI()
        gui.show_form()
    else:
        dice_type = DiceSet.DICE_TYPE_MANUAL
        yg = YahtzeeGame(dice_type, position_costs, debug, dice_format)
        yg.play_game()

# UPPER_SECTION_END = 5
# THREE_OF_A_KIND = 6
# FOUR_OF_A_KIND = 7
# FULL_HOUSE = 8
# SMALL_STRAIGHT = 9
# LARGE_STRAIGHT = 10
# YAHTZEE = 11
# BONUS_YAHTZEE = 12
# CHANCE = 13
# NUM_SLOTS = 14

if __name__ == '__main__':
    main()