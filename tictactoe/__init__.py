from otree.api import *
import json

doc = """
Tic-tac-toe
"""


class Constants(BaseConstants):
    name_in_url = 'tictactoe'
    players_per_group = None
    num_rounds = 1
    BLANK = ' '


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    winner = models.StringField()
    board_state = models.LongStringField(initial=Constants.BLANK * 9)
    whose_turn = models.StringField(initial='X')


class Player(BasePlayer):
    is_winner = models.BooleanField()
    symbol = models.StringField()


def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        p.symbol = {1: 'X', 2: 'O'}[p.id_in_group]


def get_winning_symbol(board: list):
    winning_lines = [
        # rows
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        # columns
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        # diagonals
        [0, 4, 8],
        [2, 4, 6],
    ]
    for entries in winning_lines:
        values = [board[coord] for coord in entries]
        if values in [['X', 'X', 'X'], ['O', 'O', 'O']]:
            return values[0]


class Play(Page):
    @staticmethod
    def js_vars(player: Player):
        return dict(my_symbol=player.symbol)

    @staticmethod
    def live_method(player: Player, data: dict):
        group = player.group
        board = list(group.board_state)
        broadcast = {}
        if 'move' in data:
            move = data['move']

            # you can't mark a square that was already marked
            if not board[move] == Constants.BLANK:
                return

            # you can't move out of turn
            if player.symbol != group.whose_turn:
                return

            group.whose_turn = player.get_others_in_group()[0].symbol

            board[move] = player.symbol
            group.board_state = ''.join(board)
        broadcast['board_state'] = board
        winning_symbol = get_winning_symbol(board)
        players = group.get_players()
        if winning_symbol:
            for p in players:
                p.is_winner = p.symbol == winning_symbol
            broadcast['winning_symbol'] = winning_symbol
        elif Constants.BLANK in board:
            broadcast['whose_turn'] = group.whose_turn
        else:
            broadcast['draw'] = True
        return {0: broadcast}


page_sequence = [Play]
