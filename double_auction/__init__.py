from otree.api import *
import time
import datetime
import random
import math
import copy
import ast
import json
import settings




class Constants(BaseConstants):
    name_in_url = 'double_auction'
    players_per_group = None
    num_rounds = 100 # Arbitrarily set over here. Session configs determine the actual number of rounds
    #min_induced_price = 20 # The lower threshold for the first 'step' of seller's induced value
    #num_units = 5 # 'units' here is confusing. Actually, this determines the total number of 'steps' on a subject's demand/supply curve (each step can have multiple units at that particular induced value)
    #eq_units_per_player = 4 # To get theoretical predictions, this specifies the number of 'steps' for which it is optimal for a subject to trade (In aggregation, this helps in giving the point of vertical intersection of the market demand and supply curves)




class Subsession(BaseSubsession):
    pass




def vars_for_admin_report(subsession):
    num_buyers = 0
    num_sellers = 0

    # The following long block of code basically processes the data on inducements so that it can be presented using highcharts as stepped demand and supply curves.
    if subsession.session.num_types == 2:
        type1_buyers = 0
        type1_sellers = 0

        for p in subsession.get_players():
            if p.is_buyer:
                num_buyers += 1
                if p.type == 1:
                    type1_buyers += 1
            else:
                num_sellers += 1
                if p.type == 1:
                    type1_sellers += 1

        buyer_type1_data = [[[type1_buyers * int(subsession.session.buyer_type1_presets[j][i][1]),
                              subsession.session.buyer_type1_presets[j][i][0]] for i in
                             range(subsession.session.num_induc_val_steps)] for j in
                            range(subsession.session.total_rounds)]
        buyer_type2_data = [[[(num_buyers - type1_buyers) * int(subsession.session.buyer_type2_presets[j][i][1]),
                              subsession.session.buyer_type2_presets[j][i][0]] for i in
                             range(subsession.session.num_induc_val_steps)] for j in
                            range(subsession.session.total_rounds)]
        seller_type1_data = [[[type1_sellers * int(subsession.session.seller_type1_presets[j][i][1]),
                               subsession.session.seller_type1_presets[j][i][0]] for i in
                              range(subsession.session.num_induc_val_steps)] for j in
                             range(subsession.session.total_rounds)]
        seller_type2_data = [[[(num_sellers - type1_sellers) * int(subsession.session.seller_type2_presets[j][i][1]),
                               subsession.session.seller_type2_presets[j][i][0]] for i in
                              range(subsession.session.num_induc_val_steps)] for j in
                             range(subsession.session.total_rounds)]

        buyers_data = []

        for i in range(subsession.session.total_rounds):
            temp_1 = []
            for j in range(subsession.session.num_induc_val_steps + 1):
                if j < subsession.session.num_induc_val_steps:
                    temp_1.append(buyer_type1_data[i][j])
                    temp_1.append(buyer_type2_data[i][j])
                else:
                    temp_1.append([0, buyer_type2_data[i][j - 1][1] - (
                    (buyer_type1_data[i][j - 1][1] - buyer_type2_data[i][j - 1][1]))])
            buyers_data.append(temp_1)

        for i in range(subsession.session.total_rounds):
            for j in range(2 * subsession.session.num_induc_val_steps + 1):
                if j > 0:
                    buyers_data[i][j][0] += buyers_data[i][j - 1][0]

        temp_2 = str(copy.deepcopy(buyers_data))
        for i in range(subsession.session.total_rounds):
            for j in range(2 * subsession.session.num_induc_val_steps + 1):
                if j > 0:
                    buyers_data[i][j][0] = ast.literal_eval(temp_2)[i][j - 1][0]
                else:
                    buyers_data[i][j][0] = 0

        sellers_data = []

        for i in range(subsession.session.total_rounds):
            temp_1 = []
            for j in range(subsession.session.num_induc_val_steps + 1):
                if j < subsession.session.num_induc_val_steps:
                    temp_1.append(seller_type1_data[i][j])
                    temp_1.append(seller_type2_data[i][j])
                else:
                    temp_1.append([0, seller_type2_data[i][j - 1][1] + (
                    (seller_type2_data[i][j - 1][1] - seller_type1_data[i][j - 1][1]))])
            sellers_data.append(temp_1)

        for i in range(subsession.session.total_rounds):
            for j in range(2 * subsession.session.num_induc_val_steps + 1):
                if j > 0:
                    sellers_data[i][j][0] += sellers_data[i][j - 1][0]

        temp_2 = str(copy.deepcopy(sellers_data))
        for i in range(subsession.session.total_rounds):
            for j in range(2 * subsession.session.num_induc_val_steps + 1):
                if j > 0:
                    sellers_data[i][j][0] = ast.literal_eval(temp_2)[i][j - 1][0]
                else:
                    sellers_data[i][j][0] = 0

        for i in range(subsession.session.total_rounds):
            sellers_data[i].append([0, 0])
            sellers_data[i].sort(key=lambda x: x[1])
            sellers_data[i][2 * subsession.session.num_induc_val_steps + 1][1] = 100000000000000000000000000000000000
            buyers_data[i].append([0, 100000000000000000000000000000000000])
            buyers_data[i].sort(key=lambda x: x[1], reverse=True)
            buyers_data[i][2 * subsession.session.num_induc_val_steps + 1][1] = 0

        diff_y_axis = []
        max_y_axis = []
        for i in range(subsession.session.total_rounds):
            diff_y_axis.append(sellers_data[i][1][1])
            max_y_axis.append(buyers_data[i][1][1] + diff_y_axis[i])
    else:
        for p in subsession.get_players():
            if p.is_buyer:
                num_buyers += 1
            else:
                num_sellers += 1

        buyer_data = [[[num_buyers * int(subsession.session.buyer_presets[j][i][1]),
                              subsession.session.buyer_presets[j][i][0]] for i in
                             range(subsession.session.num_induc_val_steps)] for j in
                            range(subsession.session.total_rounds)]
        seller_data = [[[num_sellers * int(subsession.session.seller_presets[j][i][1]),
                               subsession.session.seller_presets[j][i][0]] for i in
                              range(subsession.session.num_induc_val_steps)] for j in
                             range(subsession.session.total_rounds)]

        buyers_data = []

        for i in range(subsession.session.total_rounds):
            temp_1 = []
            for j in range(subsession.session.num_induc_val_steps + 1):
                if j < subsession.session.num_induc_val_steps:
                    temp_1.append(buyer_data[i][j])
                else:
                    temp_1.append([0, buyer_data[i][j - 1][1] - (
                    (buyer_data[i][j - 2][1] - buyer_data[i][j - 1][1]))])
            buyers_data.append(temp_1)

        for i in range(subsession.session.total_rounds):
            for j in range(subsession.session.num_induc_val_steps + 1):
                if j > 0:
                    buyers_data[i][j][0] += buyers_data[i][j - 1][0]

        temp_2 = str(copy.deepcopy(buyers_data))
        for i in range(subsession.session.total_rounds):
            for j in range(subsession.session.num_induc_val_steps + 1):
                if j > 0:
                    buyers_data[i][j][0] = ast.literal_eval(temp_2)[i][j - 1][0]
                else:
                    buyers_data[i][j][0] = 0

        sellers_data = []

        for i in range(subsession.session.total_rounds):
            temp_1 = []
            for j in range(subsession.session.num_induc_val_steps + 1):
                if j < subsession.session.num_induc_val_steps:
                    temp_1.append(seller_data[i][j])
                else:
                    temp_1.append([0, seller_data[i][j - 1][1] + (
                    (seller_data[i][j - 1][1] - seller_data[i][j - 2][1]))])
            sellers_data.append(temp_1)

        for i in range(subsession.session.total_rounds):
            for j in range(subsession.session.num_induc_val_steps + 1):
                if j > 0:
                    sellers_data[i][j][0] += sellers_data[i][j - 1][0]

        temp_2 = str(copy.deepcopy(sellers_data))
        for i in range(subsession.session.total_rounds):
            for j in range(subsession.session.num_induc_val_steps + 1):
                if j > 0:
                    sellers_data[i][j][0] = ast.literal_eval(temp_2)[i][j - 1][0]
                else:
                    sellers_data[i][j][0] = 0

        for i in range(subsession.session.total_rounds):
            sellers_data[i].append([0, 0])
            sellers_data[i].sort(key=lambda x: x[1])
            sellers_data[i][subsession.session.num_induc_val_steps + 1][1] = 100000000000000000000000000000000000
            buyers_data[i].append([0, 100000000000000000000000000000000000])
            buyers_data[i].sort(key=lambda x: x[1], reverse=True)
            buyers_data[i][subsession.session.num_induc_val_steps + 1][1] = 0

    total_surplus = subsession.session.total_surplus
    print(total_surplus)

    actual_surplus = [0 for i in range(subsession.session.total_rounds)]
    efficiency = [0 for i in range(subsession.session.total_rounds)]

    for i in range(subsession.session.total_rounds):
        for p in subsession.get_players():
            actual_surplus[i] += p.in_round(i + 1).payoff_new
        efficiency[i] = round(100*actual_surplus[i] / total_surplus, 2)

    print(actual_surplus)
    print(efficiency)

    players_data = [] # A nested list which is populated with detailed data on players' role, inducements, trades, and payoff in the experiment

    for p in subsession.get_players():
        for i in range(subsession.session.total_rounds):
            players_data.append([
                p.id_in_group, # 0. Player's ID
                "buyer" if p.is_buyer else "seller", # 1. Player's role
                i + 1, # 2. Period number
                ast.literal_eval(p.in_round(i + 1).inducement)[i], # 3. Detailed data for each step of the player's induced values for the given period
                p.in_round(i + 1).payoff_new, # 4. Payoff in the the given period
                p.in_round(i + 1).session_payoff # 5. Cumulative payoff up till and including the given period
            ])

    return dict(
        buyers_data=buyers_data,
        sellers_data=sellers_data,
        total_rounds=subsession.session.total_rounds,
        offers=str(copy.deepcopy(Group.offers)),
        transactions=str(copy.deepcopy(Group.transactions)),
        players_data= str(copy.deepcopy(players_data)),
        actual_surplus = str(copy.deepcopy(actual_surplus)),
        efficiency = str(copy.deepcopy(efficiency)),
        total_surplus = total_surplus
    )




def creating_session(subsession: Subsession):
    if subsession.round_number == 1: # Assigning values to session-level variables, i.e., variables which take on values once and these values are assigned at the beginning of the experiment
        session = subsession.session

        session.num_induc_val_steps = int(subsession.session.config['num_induc_val_steps']) # The number of steps of induced values for each type of buyers/sellers
        session.quant_at_indc_val = int(subsession.session.config['quant_at_indc_val']) # Quantity endowed at each induced value step.
        session.min_induc_val = float(subsession.session.config['min_induc_val']) # The lower threshold for induced values.
        session.num_bots = int(subsession.session.config['num_bots'])
        session.num_types = int(subsession.session.config['num_types']) # The number of types of buyers/sellers. Either '1' or '2' types are currently supported.
        session.eq_indc_val_step = int(subsession.session.config['eq_indc_val_step']) # The number of steps of induced values for each type of buyers/sellers for which it is, in theory, optimal for them to carry out trade.
        session.step_diff_per_type = float(subsession.session.config['step_diff_per_type']) # The amount of difference between two consecutive steps of induced values for each type of buyers/sellers.
        session.step_up_aft_ev_round = int(subsession.session.config['step_up_aft_ev_round']) # The number of rounds after which induced values are shifted up.
        session.step_up_by = float(subsession.session.config['step_up_by']) # The amount by which induced value at each step will shift up when the shift takes place.
        session.total_rounds = int(subsession.session.config['num_rounds'])  # To make total number of rounds/trading periods configurable by the teacher, these are picked up from session configs
        session.timeout_seconds = int(subsession.session.config['timeout_seconds'])  # The amount of time per trading period is also configurable
        session.custom_inducement = (subsession.session.config['custom_inducement'])

        if session.custom_inducement == False:
            session.starting_price = random.randint(session.min_induc_val, session.min_induc_val + 10) # Randomly generates the the lowest induced value for the seller which is within 10 ECUs of 'session.min_induc_val'

            # This sets the maximum induced value for buyers which ensures, theoretically, that the vertical intersection between the supply and demand curves takes place at an aggregate quantity such that at this equilibrium level, everyone trades 'session.eq_indc_val_step'
            if session.num_types == 2:
                session.ending_price = session.starting_price + 1*(session.num_types*session.step_diff_per_type*session.eq_indc_val_step) - 2
            else:
                session.ending_price = session.starting_price + 2*(session.num_types*session.step_diff_per_type*session.eq_indc_val_step) - 2

            # The 'presets_template' is used to generate a nested list (iterated over, first, the number of 'steps' of induced values, and second, over the number of rounds/trading periods in the experiment). This list will first be populated by induced values and endowed quantities at each induced value, and later, it will be populated by user data, as the experiment progresses
            # The entries in each index of each indiviudal list are as follows: 0.induced value (assinged later), 1.quantity endowed, 2.quantity sold/purchased, 3.quantity available, 4.order type (will be populated by either 'limit' or 'market'), 5.price, 6.unit profit, 7.total profit
            # The 'if' statement below checks for whether a fixed quantity is to be endowed at each step of induced values or not.
            if session.quant_at_indc_val == 0:
                session.presets_template = [[[0, session.num_induc_val_steps-i, 0, session.num_induc_val_steps-i, '' , 0, 0, 0] for i in range(session.num_induc_val_steps)] for j in range(session.total_rounds)]
            else:
                session.presets_template = [[[0, session.quant_at_indc_val, 0, session.quant_at_indc_val, '' , 0, 0, 0] for i in range(session.num_induc_val_steps)] for j in range(session.total_rounds)]

            # If there are two types each of sellers and buyers, then each buyer/seller is assigned to one of these types. The difference between these types is that at each 'step', type 2 sellers' induced value is 'session.step_diff_per_type/2' ECUs higher than type 1 sellers and type 2 buyers' induced value is 'session.step_diff_per_type/2' ECUs lower than type 1 buyers (This distinction between types doesn't disturb the predicted equilibrium quantity)
            if session.num_types == 2:
                session.seller_type1_presets = copy.deepcopy(session.presets_template)
                session.seller_type2_presets = copy.deepcopy(session.presets_template)
                session.buyer_type1_presets = copy.deepcopy(session.presets_template)
                session.buyer_type2_presets = copy.deepcopy(session.presets_template)

                x = 1
                y = 0
                for i in range(session.total_rounds):
                    if x % (session.step_up_aft_ev_round+1) == 0: # This block of code is responsible for shifting up the induced values after every given number of rounds
                        x = 1
                        y += 1
                    for j in range(session.num_induc_val_steps):
                        session.seller_type1_presets[i][j][0] = session.starting_price + (session.step_up_by * y) + (session.step_diff_per_type * j)
                        session.seller_type2_presets[i][j][0] = session.starting_price + (session.step_up_by * y) + (session.step_diff_per_type * j) + (session.step_diff_per_type/2)
                        session.buyer_type1_presets[i][j][0] = session.ending_price + (session.step_up_by * y) - (session.step_diff_per_type * j)
                        session.buyer_type2_presets[i][j][0] = session.ending_price + (session.step_up_by * y) - (session.step_diff_per_type * j) - (session.step_diff_per_type/2)
                    x += 1
            else: # If there is only one type each of sellers and buyers then the following block executes
                session.seller_presets = copy.deepcopy(session.presets_template)
                session.buyer_presets = copy.deepcopy(session.presets_template)

                x = 1
                y = 0
                for i in range(session.total_rounds):
                    if x % (session.step_up_aft_ev_round+1) == 0:
                        x = 1
                        y += 1
                    for j in range(session.num_induc_val_steps):
                        session.seller_presets[i][j][0] = session.starting_price + (session.step_up_by * y) + (session.step_diff_per_type * j)
                        session.buyer_presets[i][j][0] = session.ending_price + (session.step_up_by * y) - (session.step_diff_per_type * j)
                    x += 1
        else:
            if session.num_types == 2:
                session.seller_type1_presets = [[[subsession.session.config['inducement_round1_seller_type1'][i][0], subsession.session.config['inducement_round1_seller_type1'][i][1], 0, subsession.session.config['inducement_round1_seller_type1'][i][1], '', 0, 0, 0] for i in range(session.num_induc_val_steps)] for j in range(session.total_rounds)]
                session.seller_type2_presets = [[[subsession.session.config['inducement_round1_seller_type2'][i][0], subsession.session.config['inducement_round1_seller_type2'][i][1], 0, subsession.session.config['inducement_round1_seller_type2'][i][1], '', 0, 0, 0] for i in range(session.num_induc_val_steps)] for j in range(session.total_rounds)]
                session.buyer_type1_presets = [[[subsession.session.config['inducement_round1_buyer_type1'][i][0], subsession.session.config['inducement_round1_buyer_type1'][i][1], 0, subsession.session.config['inducement_round1_buyer_type1'][i][1], '', 0, 0, 0] for i in range(session.num_induc_val_steps)] for j in range(session.total_rounds)]
                session.buyer_type2_presets = [[[subsession.session.config['inducement_round1_buyer_type2'][i][0], subsession.session.config['inducement_round1_buyer_type2'][i][1], 0, subsession.session.config['inducement_round1_buyer_type2'][i][1], '', 0, 0, 0] for i in range(session.num_induc_val_steps)] for j in range(session.total_rounds)]

                s_t1_preset = copy.deepcopy(session.seller_type1_presets)
                s_t2_preset = copy.deepcopy(session.seller_type2_presets)
                b_t1_preset = copy.deepcopy(session.buyer_type1_presets)
                b_t2_preset = copy.deepcopy(session.buyer_type2_presets)

                x = 1
                y = 0
                for i in range(session.total_rounds):
                    if x % (session.step_up_aft_ev_round + 1) == 0:  # This block of code is responsible for shifting up the induced values after every given number of rounds
                        x = 1
                        y += 1
                    for j in range(session.num_induc_val_steps):
                        session.seller_type1_presets[i][j][0] = s_t1_preset[i][j][0] + session.step_up_by * y
                        session.seller_type2_presets[i][j][0] = s_t2_preset[i][j][0] + session.step_up_by * y
                        session.buyer_type1_presets[i][j][0] = b_t1_preset[i][j][0] + session.step_up_by * y
                        session.buyer_type2_presets[i][j][0] = b_t2_preset[i][j][0] + session.step_up_by * y
                    x += 1
            else:  # If there is only one type each of sellers and buyers then the following block executes
                session.seller_presets = [[[subsession.session.config['inducement_round1_seller_type1'][i][0], subsession.session.config['inducement_round1_seller_type1'][i][1], 0, subsession.session.config['inducement_round1_seller_type1'][i][1], '', 0, 0, 0] for i in range(session.num_induc_val_steps)] for j in range(session.total_rounds)]
                session.buyer_presets = [[[subsession.session.config['inducement_round1_buyer_type1'][i][0], subsession.session.config['inducement_round1_buyer_type1'][i][1], 0, subsession.session.config['inducement_round1_buyer_type1'][i][1], '', 0, 0, 0] for i in range(session.num_induc_val_steps)] for j in range(session.total_rounds)]

                s_preset = copy.deepcopy(session.seller_presets)
                b_preset = copy.deepcopy(session.buyer_presets)

                x = 1
                y = 0
                for i in range(session.total_rounds):
                    if x % (session.step_up_aft_ev_round + 1) == 0:
                        x = 1
                        y += 1
                    for j in range(session.num_induc_val_steps):
                        session.seller_presets[i][j][0] = s_preset[i][j][0] + session.step_up_by * y
                        session.buyer_presets[i][j][0] = b_preset[i][j][0] + session.step_up_by * y
                    x += 1

        num_players = session.num_participants

        total_surplus = 0

        if session.num_types == 2:
            for i in range(session.eq_indc_val_step):
                total_surplus += (session.buyer_type1_presets[0][i][0] - session.seller_type1_presets[0][i][0]) * session.buyer_type1_presets[0][i][1] * num_players / 4
                total_surplus += (session.buyer_type2_presets[0][i][0] - session.seller_type2_presets[0][i][0]) * session.buyer_type2_presets[0][i][1] * num_players / 4
        else:
            for i in range(session.eq_indc_val_step):
                total_surplus += (session.buyer_presets[0][i][0] - session.seller_presets[0][i][0]) * session.buyer_presets[0][i][1] * num_players / 2

        session.total_surplus = total_surplus

        # The following block of code assigns values to variables at the participant level (instead of player level) to ensure that the beginning-of-round values for these variables don't change across rounds or sub-sessions
        for player in subsession.get_players():
            participant = player.participant
            participant.id_in_group = player.id_in_group

            participant.tot_eq_units = 0

            if participant.id_in_group <= session.num_bots:
                participant.is_bot = True
            else:
                participant.is_bot = False

            participant.is_buyer = participant.id_in_group % 2 != 0 # Ensures equal distribution of even-numbered participants into buyers and sellers

            if session.num_types == 2:
                if participant.is_buyer:
                    participant.id_by_role = int(participant.id_in_group // 2) + 1 # 'id_by_role' variable is used to equally distribute buyers into each of two types and sellers into each of two types
                    if participant.id_by_role % 2 != 0:
                        participant.type = 1
                        participant.inducement = str(copy.deepcopy(session.buyer_type1_presets))
                    else:
                        participant.type = 2
                        participant.inducement = str(copy.deepcopy(session.buyer_type2_presets))
                else:
                    participant.id_by_role = int(participant.id_in_group / 2)
                    if participant.id_by_role % 2 != 0:
                        participant.type = 1
                        participant.inducement = str(copy.deepcopy(session.seller_type1_presets))
                    else:
                        participant.type = 2
                        participant.inducement = str(copy.deepcopy(session.seller_type2_presets))
            else:
                if participant.is_buyer:
                    participant.id_by_role = int(participant.id_in_group // 2) + 1
                    participant.type = 1
                    participant.inducement = str(copy.deepcopy(session.buyer_presets))
                else:
                    participant.id_by_role = int(participant.id_in_group / 2)
                    participant.type = 1
                    participant.inducement = str(copy.deepcopy(session.seller_presets))

            for i in range(session.eq_indc_val_step):
                participant.tot_eq_units += int(ast.literal_eval(participant.inducement)[0][i][1])

    # I couldn't figure how to reference session level variables in the 'live_method' below, that's why, at the beginning of each round, I am using group level variables to pick these up
    Group.total_rounds = subsession.session.total_rounds # The total number of trading periods in a session
    Group.timeout_seconds = subsession.session.timeout_seconds # The number of seconds for which subjects can trade in each trading period
    Group.wait_timeout_seconds = int(subsession.session.config['wait_timeout_seconds']) # Specifies the number the seconds for which the subjects get a break between two consecutive trading periods
    Group.multiple_unit_trading = subsession.session.config['multiple_unit_trading'] # Set at 'False' (without quotes) in SESSION CONFIGS to only allow the subjects to trade a single unit at a time 'True' (or anything other than 'False' in this case) will allow the subjects to trade multiple units at a time
    Group.relative_price_imp = subsession.session.config['relative_price_imp'] # Set at "all" in SESSION CONFIGS to enforce price improvement relative to the current best offer. "self" (or anything other than "all" in this case) will enforce price improvement relative own best offer
    Group.offers = str(copy.deepcopy([])) # A detailed nested list of bid and ask offers made during the experiment (Primarily used for the admin_report page)
    Group.transactions = str(copy.deepcopy([])) # A detailed nested list of completed trades during the experiment (Primarily used for the admin_report page)
    Group.bids = str(copy.deepcopy([])) # A less-detailed list of bids (Primarily used for populating the bid/ask table)
    Group.asks = str(copy.deepcopy([])) # A less-detailed list of asks (Primarily used for populating the bid/ask table)
    Group.hide_total_rounds = subsession.session.config['hide_total_rounds']

    # The following block of code ensures that at the beginning of each round/sub-session, the session-wide participant variables are copied for each player (Some of these are later updated and re-populated with data from all previous rounds)
    for player in subsession.get_players():
        participant = player.participant
        player.current_offer = 0
        player.id_in_group = participant.id_in_group
        player.id_by_role = participant.id_by_role
        player.is_bot = participant.is_bot
        player.is_buyer = participant.is_buyer
        player.type = participant.type
        player.inducement = participant.inducement
        player.tot_eq_units = participant.tot_eq_units




class Group(BaseGroup):
    start_timestamp = models.IntegerField() # Captures the time at which all players arrive and the experiment begins
    total_rounds = models.IntegerField() # Captures the total number of rounds/periods in the experiment (Picked up from SESSION_CONFIGS)
    timeout_seconds = models.IntegerField() # The amount of time (in seconds) each subject will have in every period for carrying out trades (Picked up from SESSION_CONFIGS)
    wait_timeout_seconds = models.IntegerField() # The amount of time (in seconds) for which the subjects would have to wait at the end of each trading period before the next period begins (Picked up from SESSION_CONFIGS)
    multiple_unit_trading = models.BooleanField() # Captures if subjects are allowed to bid/ask or buy/sell multiple units in each offer they make (Picked up from SESSION_CONFIGS)
    relative_price_imp = models.StringField() # Enforces price improvement relative to the current best offer OR relative to own best offer (Picked up from SESSION_CONFIGS)
    offers = models.LongStringField() # A nested list which keeps track of all bid/ask offers made in the experiment
    transactions = models.LongStringField() # A nested list which keeps track of all completed transactions in the experiment
    bids = models.LongStringField() # A nested list of all outstanding bids at a given point in time
    asks = models.LongStringField() # A nested list of all outstanding asks at a given point in time
    hide_total_rounds = models.BooleanField()
    #total_surplus = models.FloatField()




class Player(BasePlayer):
    is_buyer = models.BooleanField() # 'True' if buyer, 'False' if seller
    is_bot = models.BooleanField(initial=False)
    id_by_role = models.IntegerField() # Used to distribute buyers and sellers evenly across each of their respective types
    type = models.IntegerField() # Used to distinguish between type 1 and type 2 buyers/sellers
    inducement = models.LongStringField() # All the relevant trade related data for each player is stored in this nested list
    current_offer = models.FloatField(initial=0) # Records the ECU amount of the standing offer for buyer/seller
    current_quant = models.IntegerField(initial=0) # Records the quantity offered for purchase/sale at the current/standing offer
    order_type = models.StringField() # Records whether it is a 'limit' or a 'market' order
    session_payoff = models.FloatField(initial=0) # The aggregate payoff/earnings for the player summed over all previous rounds/trading periods
    payoff_new = models.FloatField(initial=0) # The period earnings for the player (for some reason the built-in payoff variable was storing the amount rounded to the nearest integer value as float(payoff) did not return floating point numbers)
    tot_eq_units = models.IntegerField()




def find_match_new(buyers, sellers, offer_type, bids_new, asks_new): # This method is used to determine the buyer and the seller for each trade
    if offer_type == 'bid' or offer_type == 'buy':
        for buyer in buyers:
            for seller in sellers:
                if seller.current_offer == min(asks_new, key=lambda x: x[2])[2]:
                    return [buyer, seller, buyer.order_type, seller.order_type, offer_type]
    else:
        for seller in sellers:
            for buyer in buyers:
                if buyer.current_offer == max(bids_new, key=lambda x: x[2])[2]:
                    return [buyer, seller, buyer.order_type, seller.order_type, offer_type]




def live_method(player: Player, data): # Whenever a buyer or a seller submits a limit or a market order, this method is called
    group = player.group
    players = group.get_players()
    buyers = [p for p in players if p.is_buyer] # The list of players assigned the role of a buyer
    sellers = [p for p in players if not p.is_buyer] # The list of players assigned the role of a seller
    news = [] # Used to populate the 'Messages' div on the Trading page after a trade has taken place (messages pertaining to market orders are also reflected here)
    event = None # Used to populate the 'Messages' div on the Trading page after a player submits a limit order (i.e. a bid or an ask)
    agg_units_traded = 0

    bids_incl_outstanding = ast.literal_eval(Group.bids) # Stores the list of all outstanding bid prices for the current round as well as the outstanding bids from the previous round
    asks_incl_outstanding = ast.literal_eval(Group.asks) # Stores the list of all outstanding ask prices for the current round as well as the outstanding asks from the previous round

    bids_new = []  # Stores the list of all outstanding bid prices for the current round only
    asks_new = [] # Stores the list of all outstanding ask prices for the current round only

    if len(bids_incl_outstanding) != 0:
        for i in range(len(bids_incl_outstanding)):
            if bids_incl_outstanding[i][0] == player.round_number: #Appends only the outstanding bids from the current round to the 'bids_new' list
                bids_new.append(bids_incl_outstanding[i])

    if len(asks_incl_outstanding) != 0:
        for i in range(len(asks_incl_outstanding)):
            if asks_incl_outstanding[i][0] == player.round_number: #Appends only the outstanding asks from the current round to the 'asks_new' list
                asks_new.append(asks_incl_outstanding[i])

    offers = ast.literal_eval(Group.offers) # Populated with details about all of the bid/ask offers
    transactions = ast.literal_eval(Group.transactions) # Populated with details about all completed transactions

    # Data will be sent here (and some other data will be sent back) whenever a player submits a limit order (i.e. clicks on the 'Bid'/'Ask' button) or a market order (i.e. clicks on the'Buy'/'Sell' button)
    if data:
        # The following block of code determines whether a limit or a market order was placed
        if data['market_order'] != "":
            type_of_order = 'market'
        else:
            type_of_order = 'limit'

        player.order_type = type_of_order

        if type_of_order == 'limit': # If a limit order is received then capture the information on the bid/ask price as well as the quantity demanded/offered at that price

            bids_copy = []
            asks_copy = []

            # The following block of code bascially removes the details of an outstanding limit order by a buyer/seller when s/he places a new limit order
            if player.is_buyer:
                if len(bids_new) != 0:
                    for i in range(len(bids_new)):
                        if not (bids_new[i][1] == player.id_in_group and bids_new[i][0] == player.round_number):
                            bids_copy.append(bids_new[i])
                    bids_new = copy.deepcopy(bids_copy)
            else:
                if len(asks_new) != 0:
                    for i in range(len(asks_new)):
                        if not(asks_new[i][1] == player.id_in_group and asks_new[i][0] == player.round_number):
                            asks_copy.append(asks_new[i])
                    asks_new = copy.deepcopy(asks_copy)

            try:
                offer = float(data['limit_order'])
                quant = int(data['quant'])
            except Exception:
                return
            player.current_offer = offer
        else: # If a market order is received then capture the quantity demanded/offered at the going market price
            try:
                quant = int(data['quant'])
            except Exception:
                return

        player.current_quant = quant

        if type_of_order == 'limit': # Add details of the player's limit order to the bids/asks list (appends the offer price submitted by the player to the outstanding bids/asks list as many times as the quantity demanded/offered at that price)
            if player.is_buyer:
                for i in range(player.current_quant):
                    bids_new.append([player.round_number, player.id_in_group, player.current_offer])
            else:
                for i in range(player.current_quant):
                    asks_new.append([player.round_number, player.id_in_group, player.current_offer])

        sorted(bids_new,key=lambda x:x[2])
        sorted(asks_new,key=lambda x:x[2])

        #The following three variables are used to record the time on the countdown timer when a buyer/seller submits a limit order (i.e. bid/ask)
        event_sec = Group.timeout_seconds + group.start_timestamp - time.time()
        event_min,event_sec = divmod(event_sec, 60)

        if Group.timeout_seconds + group.start_timestamp - time.time() > 0:
            time_event = str(int(event_min)) + ":" + str(int(event_sec)).zfill(2)
        else:
            time_event = str(00) + ":" + str(00).zfill(2)

        event = dict(id_sender=player.id_in_group, time_event=time_event,
                     offer_amt=player.current_offer, offer_qt=player.current_quant,order_type=type_of_order)

        for p in sellers:
            for i in range(len(ast.literal_eval(p.inducement)[p.round_number - 1])):
                agg_units_traded += ast.literal_eval(p.inducement)[p.round_number - 1][i][2]

        if player.order_type == 'limit':
            offers.append([
                player.round_number,
                str(time_event),
                agg_units_traded + 1, # Records the unit number for which the offer is made (i.e. a bid for the second unit)
                player.id_in_group,
                "buyer" if player.is_buyer==True else "seller",
                "bid" if player.is_buyer==True else "ask",
                player.current_offer,
                player.current_quant,
            ])

        Group.offers = str(copy.deepcopy(offers))

        total_units = 0 # This variable records the total number of units traded per each completed trade for a given seller/buyer pair

        for i in range(player.current_quant): # Potential trades are checked for at a unit by unit level as one of the buyer/seller pair could be different for a multi-unit offer
            match_new = [] # Clears existing matches/trades

            if player.order_type == 'limit':
                if player.is_buyer and len(asks_new) > 0: # A match could be found for a given bid if there are any outstanding asks
                    if player.current_offer >= min(asks_new, key=lambda x: x[2])[2]: # Furthermore, trade can occur only if a given bid exceeds the minimum outstanding ask price
                        match_new = find_match_new(buyers=[player], sellers=sellers, offer_type='bid', bids_new=bids_new,
                                                   asks_new=asks_new)
                elif not player.is_buyer and len(bids_new) > 0: # A match could be found for a given ask if there are any outstanding bids
                    if player.current_offer <= max(bids_new, key=lambda x: x[2])[2]: # Furthermore, trade can occur only if a given ask price is below the maximum outstanding bid
                        match_new = find_match_new(buyers=buyers, sellers=[player], offer_type='ask', bids_new=bids_new,
                                                   asks_new=asks_new)
            else:
                if player.is_buyer and len(asks_new) > 0: # In the case of market order from a buyer, check if there are any outstanding asks and then use the find_match_new method to complete the trade at the minimum outstanding ask price
                    match_new = find_match_new(buyers=[player], sellers=sellers, offer_type='buy', bids_new=bids_new,
                                               asks_new=asks_new)
                elif not player.is_buyer and len(bids_new) > 0: # In the case of market order from a seller, check if there are any outstanding bids and then use the find_match_new method to complete the trade at the maximum outstanding bid
                    match_new = find_match_new(buyers=buyers, sellers=[player], offer_type='sell', bids_new=bids_new,
                                               asks_new=asks_new)

            if match_new != []: # If a match is found, that is, if a trade occurs, then the following block is executed
                [buyer, seller, buyer_order_type, seller_order_type, last_offer_type] = match_new # Receives the data sent by the match_new method after a match has been found
                if last_offer_type == 'bid' or last_offer_type == 'buy': # If trade occurred after a buyer submitted a bid that was higher than the lowest ask price in the queue, then the trade price is that ask price. If trade occurred after a buyer submitted a market order then the trade price is the lowest ask price in the queue
                    price = seller.current_offer

                else: # If trade occurred after a seller submitted an ask that was lower than the highest bid in the queue, then the trade price is that bid. If trade occurred after a seller submitted a market order then the trade price is the highest bid price in the queue
                    price = buyer.current_offer

                for i in range(len(asks_new)): # As the trade has occurred, so the ask price needs to be deleted from the list of outstanding ask prices
                    if asks_new[i][0] == seller.round_number and asks_new[i][1] == seller.id_in_group:
                        asks_new.pop(i)
                        break

                for i in range(len(bids_new)): # As the trade has occurred, so the bid price needs to be deleted from the list of outstanding bids
                    if bids_new[i][0] == buyer.round_number and bids_new[i][1] == buyer.id_in_group:
                        bids_new.pop(i)
                        break

                # The following two nested lists copy buyers and sellers data which is later updated to reflect completed trade(s)
                buyer_inducement = ast.literal_eval(buyer.inducement)
                seller_inducement = ast.literal_eval(seller.inducement)

                for i in range(len(buyer_inducement[buyer.round_number - 1])): # Iterates over the copied data of the buyer for the round in question
                    if buyer_inducement[buyer.round_number - 1][i][2] < buyer_inducement[buyer.round_number - 1][i][1]: # Check if quantity bought at the ith step of induced values for the given round is less than quantity endowed (implying that not all units endowed at this step have been bought yet), othwerwise go to the next step of induced values
                        if buyer_inducement[buyer.round_number - 1][i][5] == 0 or buyer_inducement[buyer.round_number - 1][i][5] == price: # If either no units have been bought yet at the ith step of induced values or if the price at which previous units were bought is the same as that for the current unit bought, then we just need to update data on this step
                            buyer_inducement[buyer.round_number - 1][i][2] = buyer_inducement[buyer.round_number - 1][i][2] + 1 # As an additional unit has beeen bought at ith step of induced values at the same price as previous unit(s), then reflect this change by adding 1 to the number of units bought (if there weren't any prior trades at this step of induced values then just 1 will appear here)
                            buyer_inducement[buyer.round_number - 1][i][3] = buyer_inducement[buyer.round_number - 1][i][3] - 1 # Similar logic to the comment above, reduce 1 from the number of units available
                            buyer_inducement[buyer.round_number - 1][i][4] += 'L' if buyer_order_type=='limit' else 'M' # Whether the buyer placed a limit or a market order which led to the purchase of this unit
                            buyer_inducement[buyer.round_number - 1][i][5] = float(price) # The price at which trade took place
                            buyer_inducement[buyer.round_number - 1][i][6] = buyer_inducement[buyer.round_number - 1][i][0] - float(price) # Unit profit is simply induced value at the step minus the price paid
                            buyer_inducement[buyer.round_number - 1][i][7] = buyer_inducement[buyer.round_number - 1][i][7] + buyer_inducement[buyer.round_number - 1][i][6] # Total profit is simply the existing total profit at this step (if there have been any prior trades) plus the unit profit as an additional unit was bought at this step (If there weren't any prior trades at this step, then it's just the unit profit)
                            buyer.payoff_new += buyer_inducement[buyer.round_number - 1][i][0] - float(price) # Existing buyer payoff for the current round is augmented by the profit obtained from buying the current unit
                            buyer.session_payoff += buyer_inducement[buyer.round_number - 1][i][0] - float(price) # The aggregate payoff from trade in all previous as well as the current round is being augmented here
                            break
                        else: # If unit(s) have been previously bought at the ith step of induced values at a different price, then we need to bifurcate the data for the ith step of induced values as due to different prices for different units, profits will be different
                            buyer_inducement[buyer.round_number - 1].append([buyer_inducement[buyer.round_number - 1][i][0], # The induced value in the additional row is the same as the induced value at the ith step
                                                                             buyer_inducement[buyer.round_number - 1][i][3], # Quantity endowed in this case will be the quantity which was available when this bifurcation took place
                                                                             1, # Quantity bought is 1 as this new row has just been created after this trade
                                                                             buyer_inducement[buyer.round_number - 1][i][3] - 1, # Quantity available is simply the quantity endowed minus 1
                                                                             'L' if buyer_order_type=='limit' else 'M', # Whether the buyer placed a limit or a market order which led to the purchase of this unit
                                                                             float(price), # The price at which trade took place
                                                                             buyer_inducement[buyer.round_number - 1][i][0] - float(price), # Unit profit
                                                                             buyer_inducement[buyer.round_number - 1][i][0] - float(price) # Total profit is the same as unit profit as this bifurcation has happened when 1 additional unit was bought
                                                                             ])
                            buyer_inducement[buyer.round_number - 1][i][1] = buyer_inducement[buyer.round_number - 1][i][2] # After bifurcation, the quantity endowed is set equal to the quantity bought for the earlier trade which took at a different price for ith step of induced values
                            buyer_inducement[buyer.round_number - 1][i][3] = 0 # Similarly, the quantity available is set equal to the zero for the earlier trade which took at a different price for ith step of induced values
                            buyer.payoff_new += buyer_inducement[buyer.round_number - 1][i][0] - float(price) # Existing buyer payoff for the current round is augmented by the profit obtained from buying the current unit
                            buyer.session_payoff += buyer_inducement[buyer.round_number - 1][i][0] - float(price) # The aggregate payoff from trade in all previous as well as the current round is being augmented here
                            break

                buyer_inducement[buyer.round_number - 1] = sorted(sorted(buyer_inducement[buyer.round_number - 1], key=lambda x: x[3]), key=lambda x:x[0], reverse=True) # Buyer's updated copied data for the current trading period after trade has taken place is being sorted here

                buyer.inducement = str(copy.deepcopy(buyer_inducement)) # The original data for the buyer is being updated here with the copied data

                for i in range(len(seller_inducement[seller.round_number - 1])): # Iterates over the copied data of the seller for the round in question
                    if seller_inducement[seller.round_number - 1][i][2] < seller_inducement[seller.round_number - 1][i][1]: # Check if quantity sold at the ith step of induced values for the given round is less than quantity endowed (implying that not all units endowed at this step have been sold yet), othwerwise go to the next step of induced values
                        if seller_inducement[seller.round_number - 1][i][5] == 0 or seller_inducement[seller.round_number - 1][i][5] == price: # If either no units have been sold yet at the ith step of induced values or if the price at which previous units were sold is the same as that for the current unit sold, then we just need to update data on this step
                            seller_inducement[seller.round_number - 1][i][2] = seller_inducement[seller.round_number - 1][i][2] + 1 # As an additional unit has beeen sold at ith step of induced values at the same price as previous unit(s), then reflect this change by adding 1 to the number of units sold (if there weren't any prior trades at this step of induced values then just 1 will appear here)
                            seller_inducement[seller.round_number - 1][i][3] = seller_inducement[seller.round_number - 1][i][3] - 1 # Similar logic to the comment above, reduce 1 from the number of units available
                            seller_inducement[seller.round_number - 1][i][4] += 'L' if buyer_order_type=='limit' else 'M' # Whether the seller placed a limit or a market order which led to the sale of this unit
                            seller_inducement[seller.round_number - 1][i][5] = float(price) # The price at which trade took place
                            seller_inducement[seller.round_number - 1][i][6] = float(price) - seller_inducement[seller.round_number - 1][i][0] # Unit profit is simply price received minus the induced value at the step
                            seller_inducement[seller.round_number - 1][i][7] = seller_inducement[seller.round_number - 1][i][7] + seller_inducement[seller.round_number - 1][i][6] # Total profit is simply the existing total profit at this step (if there have been any prior trades) plus the unit profit as an additional unit was sold at this step (If there weren't any prior trades at this step, then it's just the unit profit)
                            seller.payoff_new += float(price) - seller_inducement[seller.round_number - 1][i][0] # Existing seller payoff for the current round is augmented by the profit obtained from selling the current unit
                            seller.session_payoff += float(price) - seller_inducement[seller.round_number - 1][i][0] # The aggregate payoff from trade in all previous as well as the current round is being augmented here
                            break
                        else: # If unit(s) have been previously sold at the ith step of induced values at a different price, then we need to bifurcate the data for the ith step of induced values as due to different prices for different units, profits will be different
                            seller_inducement[seller.round_number - 1].append([seller_inducement[seller.round_number - 1][i][0], # The induced value in the additional row is the same as the induced value at the ith step
                                                                             seller_inducement[seller.round_number - 1][i][3], # Quantity endowed in this case will be the quantity which was available when this bifurcation took place
                                                                             1, # Quantity sold is 1 as this new row has just been created after this trade
                                                                             seller_inducement[seller.round_number - 1][i][3] - 1, # Quantity available is simply the quantity endowed minus 1
                                                                             'L' if buyer_order_type=='limit' else 'M', # Whether the seller placed a limit or a market order which led to the sale of this unit
                                                                             float(price), # The price at which trade took place
                                                                             float(price) - seller_inducement[seller.round_number - 1][i][0], # Unit profit
                                                                             float(price) - seller_inducement[seller.round_number - 1][i][0] # Total profit is the same as unit profit as this bifurcation has happened when 1 additional unit was sold
                                                                             ])
                            seller_inducement[seller.round_number - 1][i][1] = seller_inducement[seller.round_number - 1][i][2] # After bifurcation, the quantity endowed is set equal to the quantity sold for the earlier trade which took at a different price for ith step of induced values
                            seller_inducement[seller.round_number - 1][i][3] = 0 # Similarly, the quantity available is set equal to the zero for the earlier trade which took at a different price for ith step of induced values
                            seller.payoff_new += float(price) - seller_inducement[seller.round_number - 1][i][0] # Existing seller payoff for the current round is augmented by the profit obtained from selling the current unit
                            seller.session_payoff += float(price) - seller_inducement[seller.round_number - 1][i][0] # The aggregate payoff from trade in all previous as well as the current round is being augmented here
                            break

                seller_inducement[seller.round_number - 1] = sorted(sorted(seller_inducement[seller.round_number - 1], key=lambda x: x[3]), key=lambda x:x[0]) # Seller's updated copied data for the current trading period after trade has taken place is being sorted here

                seller.inducement = str(copy.deepcopy(seller_inducement)) # The original data for the seller is being updated here with the copied data

                # The following three variables are used to record the time on the countdown timer when a trade takes place
                tx_sec = Group.timeout_seconds + group.start_timestamp - time.time()
                tx_min, tx_sec = divmod(tx_sec, 60)
                if Group.timeout_seconds + group.start_timestamp - time.time() > 0:
                    time_tx = str(int(tx_min)) + ":" + str(int(tx_sec)).zfill(2)
                else:
                    time_tx = str(00) + ":" + str(00).zfill(2)

                total_units += 1 # Total units traded counter incremented by 1 after a trade has taken place

                # The following two blocks of code subtract 1 from buyer's as well as seller's outstanding orders after a unit has been traded
                if buyer.current_quant != 0:
                    buyer.current_quant = buyer.current_quant - 1
                else:
                    buyer.current_quant = 0

                if seller.current_quant != 0:
                    seller.current_quant = seller.current_quant - 1
                else:
                    seller.current_quant = 0

                # Once all units for a buyer/seller pair have been traded (indicated by either the buyer or the seller having outstanding orders for zero units), news is sent out relaying trade details which are then displayed in the 'Messages' tab of the buyer and the seller
                if buyer.current_quant == 0 or seller.current_quant == 0:
                    if news == []:
                        transactions.append([
                            buyer.round_number,
                            str(time_tx),
                            agg_units_traded + 1,
                            buyer.id_in_group,
                            buyer_order_type,
                            seller.id_in_group,
                            seller_order_type,
                            price,
                            total_units,
                            last_offer_type
                        ])
                        news.append([
                            buyer.id_in_group,
                            seller.id_in_group,
                            price,
                            total_units,
                            time_tx,
                            buyer_order_type,
                            seller_order_type,
                            last_offer_type
                        ])
                    else:
                        transactions.append([
                            buyer.round_number,
                            str(time_tx),
                            agg_units_traded + 1 + news[0][3],
                            buyer.id_in_group,
                            buyer_order_type,
                            seller.id_in_group,
                            seller_order_type,
                            price,
                            total_units- news[0][3],
                            last_offer_type
                        ])
                        news.append([
                            buyer.id_in_group,
                            seller.id_in_group,
                            price,
                            total_units - news[0][3], # For an outstanding multi-unit order of a buyer/seller to be fulfilled by two different sellers/buyers, the total units bought/sold needs to be adjusted to account for this
                            time_tx,
                            buyer_order_type,
                            seller_order_type,
                            last_offer_type
                        ])

                    Group.transactions = str(copy.deepcopy(transactions))

                # The following two blocks of code indicate the fulfilment of buyer's and/or seller's current/outstanding order
                if buyer.current_quant == 0:
                    buyer.current_offer = 0
                    buyer.order_type = ''

                if seller.current_quant == 0:
                    seller.current_offer = 0
                    seller.order_type = ''

            Group.bids = str(copy.deepcopy(bids_new))
            Group.asks = str(copy.deepcopy(asks_new))

            # This caters to the case in which there is not enough quantity available to fulfill a buyer or a seller's outstanding order
            if (player.is_buyer and len(asks_new)==0) or (not player.is_buyer and len(bids_new)==0):
                break

            # Indicates the fulfillment of an order
            if player.current_quant==0:
                break

        sorted(bids_new, key=lambda x: x[2])
        sorted(asks_new, key=lambda x: x[2])

        bids_for_freq = []
        asks_for_freq = []

        if len(bids_new) != 0:
            for i in range(len(bids_new)):
                if bids_new[i][0]==player.round_number:
                    bids_for_freq.append(bids_new[i][2])

        if len(asks_new) != 0:
            for i in range(len(asks_new)):
                if asks_new[i][0] == player.round_number:
                    asks_for_freq.append(asks_new[i][2])

        # The following two lists construct a frequency list for bids and asks, respectively which are then used to populate the bid/ask tables
        bids_freq = sorted([[float(x), bids_for_freq.count(x)] for x in set(bids_for_freq)], key=lambda x: x[0], reverse=True)
        asks_freq = sorted([[float(x), asks_for_freq.count(x)] for x in set(asks_for_freq)], key=lambda x: x[0], reverse=True)

        return {
            p.id_in_group: dict(
                bids=bids_freq,
                asks=asks_freq,
                current_offer=p.current_offer,
                current_quant=p.current_quant,
                inducement=ast.literal_eval(p.inducement),
                news=news,
                event=event,
                payoff=p.payoff_new,
                session_payoff=p.session_payoff,
                offers=offers,
                transactions=transactions,
                det_bids=bids_new,
                det_asks=asks_new,
                order_type=player.order_type,
            )
            for p in players
        }




# PAGES
class WaitToStart(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.start_timestamp = int(time.time())




class Trading(Page):
    live_method = live_method

    @staticmethod
    def js_vars(player: Player):
        # The following block of code copies data from the previous round/trading period for each player at the beginning of each round after round 1
        player_inducement = ast.literal_eval(player.inducement)
        if player.round_number > 1:
            for i in range(player.round_number):
                player_inducement[i] = ast.literal_eval(player.in_round(i + 1).inducement)[i]
        player.inducement = str(copy.deepcopy(player_inducement))

        # Similarly, the following block of code copies the session payoff/earnings from the previous round at the beginning of each round which are then augemented by profit earned from trades in the current round
        if player.round_number > 1:
            player.session_payoff = player.in_round(player.round_number - 1).session_payoff
        else:
            player.session_payoff = 0

        return dict(
            id_in_group=player.id_in_group, is_buyer=player.is_buyer, is_bot=player.is_bot, tot_eq_units=player.tot_eq_units,
            id_by_role=player.id_by_role, type=player.type, cur_round=player.round_number, total_rounds=Group.total_rounds,
            inducement=ast.literal_eval(player.inducement), session_payoff=player.session_payoff,
            multiple_unit_trading=Group.multiple_unit_trading, relative_price_imp = Group.relative_price_imp,
            hide_tot_rounds = Group.hide_total_rounds, timeout_seconds = Group.timeout_seconds,
        )

    @staticmethod
    def get_timeout_seconds(player: Player):
        #group = player.group
        return Group.timeout_seconds
        #return Group.timeout_seconds + group.start_timestamp - time.time()




class MyWaitPage(Page):

    @staticmethod
    def get_timeout_seconds(player):
        timeout = Group.wait_timeout_seconds
        return timeout

    @staticmethod
    def is_displayed(player):
        return player.round_number < Group.total_rounds

    @staticmethod
    def js_vars(player: Player):
        return dict(
            is_buyer=player.is_buyer, cur_round=player.round_number, total_rounds=Group.total_rounds, period_payoff=player.payoff_new,
            session_payoff=player.session_payoff, wait_timeout=Group.wait_timeout_seconds
        )




class Results(Page):
    pass

    @staticmethod
    def is_displayed(player):
        return player.round_number == Group.total_rounds

    @staticmethod
    def js_vars(player: Player):
        return dict(
            is_buyer=player.is_buyer, total_rounds=Group.total_rounds,
            inducement=ast.literal_eval(player.inducement), period_payoffs=[p.payoff_new for p in player.in_all_rounds()],
            session_payoffs=[p.session_payoff for p in player.in_all_rounds()],
        )

page_sequence = [WaitToStart, Trading, MyWaitPage, Results]
