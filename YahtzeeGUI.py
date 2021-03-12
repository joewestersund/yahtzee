from tkinter import *
from tkinter import ttk
from tkinter import font
from YahtzeeGame import YahtzeeGame
from DiceSet import DiceSet

class YahtzeeGUI:
    def __init__(self, position_costs=None, debug=False):
        self.yahtzee_game = YahtzeeGame(DiceSet.DICE_TYPE_MANUAL, position_costs, debug, None)
        self.dice_values_text = None
        self.rounds_remaining = None
        self.instructions = None
        self.fixed_dice = None
        self.position_scores = []
        self.position_labels = []

    def ok_click(self, *args):
        dice_value_string = self.dice_values_text.get()
        dice_entered = DiceSet.parse_dice_values(dice_value_string)
        if dice_entered is None:
            extra_message = "Dice values not recognized"
            self.set_instructions(extra_message)
        else:
            # valid digits were entered. Check whether it was the right number of them
            dice_values = []
            if self.fixed_dice is not None:
                dice_values.extend(self.fixed_dice)
            dice_values.extend(dice_entered)
            dice_values.sort()
            if len(dice_values) != 5:
                # incorrect input from user
                extra_message = "Dice values not recognized"
                self.set_instructions(extra_message)
            else:
                self.yahtzee_game.dice_rolled_manually(self.fixed_dice, dice_values)
                position_to_take, dice_to_fix = self.yahtzee_game.recommended_next_step(dice_values)
                # clear the dice textbox
                self.dice_values_text.set("")
                self.fixed_dice = dice_to_fix
                if dice_to_fix is not None:
                    self.set_instructions(None)
                else:
                    self.yahtzee_game.accept_score(position_to_take, dice_values)
                    # have to get score from the scores array, because bonus yahtzees are cumulative
                    score = self.yahtzee_game.scores[position_to_take]
                    # show score on interface
                    self.show_position_score(position_to_take, score)

                    game_complete = self.yahtzee_game.game_complete()
                    if game_complete:
                        # disable the OK button
                        self.ok_button.state(['disabled'])
                        # show the overall scores
                        total, upper_section, bonus, lower_section = self.yahtzee_game.total_score()
                        self.upper_section.set(upper_section)
                        self.bonus.set(bonus)
                        self.lower_section.set(lower_section)
                        self.total_score.set(total)
                    extra_message = f'Used dice {dice_values} as {YahtzeeGame.position_name(position_to_take)} with score {score}'
                    self.set_rounds_remaining()
                    self.set_instructions(extra_message, game_complete)

    def initialize_position_score(self, position_number):
        self.position_scores[position_number].set('-')
        self.position_labels[position_number].configure(font=('TkDefaultFont', 15, 'normal'))

    def show_position_score(self, position_number, score):
        self.position_scores[position_number].set(score)
        # previously used  'Helvetica 18 bold'
        self.position_labels[position_number].configure(font=('TkDefaultFont', 18, 'bold'))

    def set_focus_on_dice_values(self):
        self.dice_entry.focus()

    def set_rounds_remaining(self):
        rr = self.yahtzee_game.rounds_remaining()
        if rr == 0:
            self.rounds_remaining.set("")
        else:
            self.rounds_remaining.set(f'{rr} rounds remaining')

    def set_instructions(self, extra_message=None, game_complete=False):
        if self.fixed_dice is None:
            fix_str = ""
            num_dice_to_roll = 5
        else:
            fix_str = f'Fixing {self.fixed_dice}\n'
            num_dice_to_roll = 5 - len(self.fixed_dice)
        if extra_message is not None:
            extra_str = f'{extra_message}\n'
        else:
            extra_str = ""
        roll_str = f'{fix_str}Please roll {num_dice_to_roll} dice and enter the values here.'
        game_over_str = "The game is complete."
        if game_complete:
            self.instructions.set(f'{extra_str}{game_over_str}')
        else:
            self.instructions.set(f'{extra_str}{roll_str}')

    def show_form(self):
        root = Tk()
        root.title = "Yahtzee"

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        totals_label_font = ('TkDefaultFont', 18, 'bold italic')
        totals_label_initial_text = ""
        row = 1
        for pos in range(YahtzeeGame.NUM_SLOTS):
            #label for position score
            label_text = StringVar()
            position_label = ttk.Label(mainframe, textvariable=label_text)
            position_label.grid(column=1, row=row, sticky=W)
            self.position_labels.append(position_label)
            self.position_scores.append(label_text)
            # initialize value of the label
            self.initialize_position_score(pos)

            # label for name of position
            position_name = YahtzeeGame.position_name(pos)
            ttk.Label(mainframe, text=position_name).grid(column=2, row=row, sticky=W)

            if pos == YahtzeeGame.UPPER_SECTION_END:
                # upper section and upper section bonus labels
                row += 1
                label_text = StringVar()
                ttk.Label(mainframe, textvariable=label_text, font=totals_label_font).grid(column=1, row=row, sticky=E)
                ttk.Label(mainframe, text="Upper Section").grid(column=2, row=row, sticky=W)
                label_text.set(totals_label_initial_text)
                self.upper_section = label_text
                row += 1
                label_text = StringVar()
                ttk.Label(mainframe, textvariable=label_text, font=totals_label_font).grid(column=1, row=row, sticky=E)
                ttk.Label(mainframe, text="Bonus").grid(column=2, row=row, sticky=W)
                label_text.set(totals_label_initial_text)
                self.bonus = label_text
            row += 1
        # lower section and total score labels
        label_text = StringVar()
        ttk.Label(mainframe, textvariable=label_text, font=totals_label_font).grid(column=1, row=row, sticky=E)
        ttk.Label(mainframe, text="Lower Section").grid(column=2, row=row, sticky=W)
        label_text.set(totals_label_initial_text)
        self.lower_section = label_text
        row += 1
        label_text = StringVar()
        ttk.Label(mainframe, textvariable=label_text, font=totals_label_font).grid(column=1, row=row, sticky=E)
        ttk.Label(mainframe, text="Total Score").grid(column=2, row=row, sticky=W)
        label_text.set(totals_label_initial_text)
        self.total_score = label_text
        row += 1

        # rounds remaining
        self.rounds_remaining = StringVar()
        ttk.Label(mainframe, textvariable=self.rounds_remaining).grid(column=1, row=row, columnspan=2, sticky=W)
        self.set_rounds_remaining()
        row += 1

        # instructions
        self.instructions = StringVar()
        ttk.Label(mainframe, textvariable=self.instructions).grid(column=1, row=row, columnspan=2, sticky=W)
        self.set_instructions(None)
        row += 1

        dice_frame = Frame(mainframe)
        dice_frame.grid(column=1, columnspan=2, row=row, sticky=E)
        self.dice_values_text = StringVar()
        ttk.Label(dice_frame, text="Dice values").grid(column=1, row=1, sticky=W)
        self.dice_entry = ttk.Entry(dice_frame, justify="left", textvariable=self.dice_values_text)
        self.dice_entry.grid(column=2, row=1, sticky=E)

        row += 1
        button_frame = Frame(mainframe)
        button_frame.grid(column=1, columnspan=2, row=row, sticky=E)
        self.ok_button = ttk.Button(button_frame, text="OK", command=self.ok_click, default="active")
        self.ok_button.grid(column=1, row=1, sticky=W)
        ttk.Button(button_frame, text="Exit", command=exit).grid(column=2, row=1, sticky=E)

        # add some padding around each element in mainframe
        for child in mainframe.winfo_children():
            child.grid_configure(padx=1, pady=1)

        root.bind("<Return>", self.ok_click)
        self.set_focus_on_dice_values()

        root.mainloop()



