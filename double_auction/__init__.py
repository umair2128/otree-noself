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
    min_induced_price = 20 # The lower threshold for the first 'step' of seller's induced value
    num_units = 5 # 'units' here is confusing. Actually, this determines the total number of 'steps' on a subject's demand/supply curve (each step can have multiple units at that particular induced value)
    eq_units_per_player = 4 # To get theoretical predictions, this specifies the number of 'steps' for which it is optimal for a subject to trade (In aggregation, this helps in giving the point of vertical intersection of the market demand and supply curves)




class Subsession(BaseSubsession):
    pass

def creating_session(subsession: Subsession):
    if subsession.round_number == 1: # Assigning values to session-level variables, i.e., variables which take on values once which are assigned at the beginning of the experiment
        session = subsession.session

        session.starting_price = random.randint(Constants.min_induced_price, Constants.min_induced_price + 10) # Randomly generates the the lowest induced value for the seller which is within 10 ECUs of 'min_induced_price'
        session.ending_price = session.starting_price + Constants.eq_units_per_player*8 - 2 # Given the variable above and the 'eq_units_per_player' variable, this sets the maximum induced value for the buyer which ensures, theoretically, that the vertical intersection between the supply and demand curves takes place at an aggregate quantity such that at this equilibrium level, everyone trades 'eq_units_per_player'

        session.total_rounds = int(subsession.session.config['num_rounds']) # To make total number of rounds configurable by the teacher, these are picked up from session configs
        session.timeout_seconds = int(subsession.session.config['timeout_seconds']) # The amount of time per trade in each round is also configurable

        # The 'presets_template' is used to generate a nested list (iterated over, first, the number of 'steps' of induced values, and second, over the number of rounds in the experiment). This list will first be populated by induced values and endowed quantities at each induced value, and later, it will be populated by user data, as the experiment progresses
        # The entries in each index of each indiviudal list are as follows: 0.induced value (assinged later), 1.quantity endowed (by default, it is increasing over the number of 'steps'), 2.quantity sold/purchased, 3.quantity available, 4.order type (will be populated by either 'limit' or 'market'), 5.price, 6.unit profit, 7.total profit
        session.presets_template = [[[0, i+1, 0, i+1, 'NA' , 0, 0, 0] for i in range(Constants.num_units)] for j in range(session.total_rounds)]

        # There are two types each of sellers and buyers. Each buyer/seller is assigned to one of these types. The difference between these types is that at each 'step', type 2 sellers' induced value is 2 ECUs higher than type 1 sellers and type 2 buyers' induced value is 2 ECUs lower than type 1 buyers (This doesn't disturb the predicted equilibrium quantity)
        session.seller_type1_presets = copy.deepcopy(session.presets_template)
        session.seller_type2_presets = copy.deepcopy(session.presets_template)
        session.buyer_type1_presets = copy.deepcopy(session.presets_template)
        session.buyer_type2_presets = copy.deepcopy(session.presets_template)

        # The comment just above this explains the following block of code
        for i in range (session.total_rounds):
            for j in range(Constants.num_units):
                session.seller_type1_presets[i][j][0] = session.starting_price + 6*i + 4*j
                session.seller_type2_presets[i][j][0] = session.starting_price + 6*i + 4*j + 2
                session.buyer_type1_presets[i][j][0] = session.ending_price + 6*i - 4*j
                session.buyer_type2_presets[i][j][0] = session.ending_price + 6*i - 4*j - 2

        # The following block of code assigns values to variables at the participant level (instead of player level) to ensure that the beginning-of-round values for these variables don't change across rounds or sub-sessions
        for player in subsession.get_players():
            participant = player.participant
            participant.id_in_group = player.id_in_group

            participant.is_buyer = participant.id_in_group % 2 != 0 # Ensures equal distribution of even-numbered participants into buyers and sellers
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

    # I couldn't figure how to reference session level variables in the 'live_method' below, that's why, at the beginning of each round, I am using group level variables to pick these up
    Group.total_rounds = subsession.session.total_rounds
    Group.timeout_seconds = subsession.session.timeout_seconds
    Group.wait_timeout_seconds = int(subsession.session.config['wait_timeout_seconds'])

    # The following block of code ensures that at the beginning of each round/sub-session, the session-wide participant variables are copied for each player
    for player in subsession.get_players():
        participant = player.participant
        player.current_offer = 0
        player.id_in_group = participant.id_in_group
        player.id_by_role = participant.id_by_role
        player.is_buyer = participant.is_buyer
        player.type = participant.type
        player.inducement = participant.inducement




class Group(BaseGroup):
    start_timestamp = models.IntegerField() # Captures the time at which all players arrive and the experiment begins
    total_rounds = models.IntegerField()
    timeout_seconds = models.IntegerField()
    wait_timeout_seconds = models.IntegerField()



class Player(BasePlayer):
    is_buyer = models.BooleanField()
    id_by_role = models.IntegerField()
    type = models.IntegerField() # Used to distinguish between type 1 and type 2 buyers/sellers
    inducement = models.LongStringField()
    current_offer = models.FloatField(initial=0) # Records the ECU amount of the standing offer for buyer/seller
    current_quant = models.IntegerField(initial=0) # Records the quantity offered for purchase/sale at the current/standing offer
    order_type = models.StringField() # Records whether it is a 'limit' or a 'market' order
    session_payoff = models.FloatField()




class Transaction(ExtraModel):
    group = models.Link(Group)
    buyer = models.Link(Player)
    seller = models.Link(Player)
    price = models.FloatField() # Records the price at which a trade takes place
    seconds = models.IntegerField(doc="Timestamp (seconds since beginning of trading)") # Will be used later to plot transactions

def find_match_new(buyers, sellers, offer_type, bids_new, asks_new): # This method is used to determine the buyer and the seller for each trade
    if offer_type == 'bid': # 'bid' here is a place-holder for limit/market order from a buyer
        for buyer in buyers:
            for seller in sellers:
                if seller.current_offer == min(asks_new):
                    return [buyer, seller, buyer.order_type, seller.order_type, offer_type]
    else:
        for seller in sellers:
            for buyer in buyers:
                if buyer.current_offer == max(bids_new):
                    return [buyer, seller, buyer.order_type, seller.order_type, offer_type]

def live_method(player: Player, data): # Whenever a buyer or a seller submits a limit or a market order, this method is called
    group = player.group
    players = group.get_players()
    buyers = [p for p in players if p.is_buyer] # The list of players assigned the role of a buyer
    sellers = [p for p in players if not p.is_buyer] # The list of players assigned the role of a seller
    news = [] # Used to populate the 'Messages' div on the Trading page after a trade has taken place (messages pertaining to market orders are also reflected here)
    event = None # Used to populate the 'Messages' div on the Trading page after a player submits a limit order (i.e. a bid or an ask)

    bids_new = [] # Stores the list of all outstanding bid prices
    asks_new = [] # Stores the list of all outstanding ask prices

    # Data will be sent here (and some other data will be sent back) whenever a player submits a limit order (i.e. clicks on the 'Bid'/'Ask' button) or a market order (i.e. clicks on the'Buy'/'Sell' button)
    if data:
        # The following block of code determines whether a limit or a market order was placed
        if data['market_order'] != "":
            type_of_order = 'market'
        else:
            type_of_order = 'limit'

        player.order_type = type_of_order

        if type_of_order == 'limit': # If a limit order is received then capture the information on the bid/ask price as well as the quantity demanded/offered at that price
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

        for p in buyers: # The following block of code basically appends the bid price submitted by the buyer to the outstanding bids list as many times as the quantity demanded at that price
            if p.current_quant != 0:
                for i in range(p.current_quant):
                    if p.current_offer != 0: # Ensures that market orders are not reflected in outstanding bids list
                        bids_new.append(p.current_offer)

        bids_new.sort()

        for p in sellers: # The following block of code basically appends the ask price submitted by the seller to the outstanding asks list as many times as the quantity offered for sale at that price
            if p.current_quant != 0:
                for i in range(p.current_quant):
                    if p.current_offer != 0: # Ensures that market orders are not reflected in outstanding asks list
                        asks_new.append(p.current_offer)

        asks_new.sort()

        #The following three variables are used to record the time on the countdown timer when a buyer/seller submits a limit order (i.e. bid/ask)
        event_sec = Group.timeout_seconds + group.start_timestamp - time.time()
        event_min,event_sec = divmod(event_sec, 60)
        time_event = str(int(event_min)) + ":" + str(int(event_sec))

        event = dict(id_sender=player.id_in_group, time_event=time_event,
                     offer_amt=player.current_offer, offer_qt=player.current_quant,order_type=type_of_order)

        total_units = 0 # This variable records the total number of units traded per each completed trade for a given seller/buyer pair

        for i in range(player.current_quant): # Potential trades are checked for at a unit by unit level as one of the buyer/seller pair could be different for a multi-unit offer
            match_new = [] # Clears existing matches/trades

            if type_of_order == 'limit':
                if player.is_buyer and len(asks_new) > 0: # A match could be found for a given bid if there are any outstanding asks
                    if player.current_offer > min(asks_new): # Furthermore, trade can occur only if a given bid exceeds the minimum outstanding ask price
                        match_new = find_match_new(buyers=[player], sellers=sellers, offer_type='bid', bids_new=bids_new,
                                                   asks_new=asks_new)
                elif not player.is_buyer and len(bids_new) > 0: # A match could be found for a given ask if there are any outstanding bids
                    if player.current_offer < max(bids_new): # Furthermore, trade can occur only if a given ask price is below the maximum outstanding bid
                        match_new = find_match_new(buyers=buyers, sellers=[player], offer_type='ask', bids_new=bids_new,
                                                   asks_new=asks_new)
            else:
                if player.is_buyer and len(asks_new) > 0: # In the case of market order from a buyer, check if there are any outstanding asks and then use the find_match_new method to complete the trade at the minimum outstanding ask price
                    match_new = find_match_new(buyers=[player], sellers=sellers, offer_type='bid', bids_new=bids_new,
                                               asks_new=asks_new)
                elif not player.is_buyer and len(bids_new) > 0: # In the case of market order from a seller, check if there are any outstanding bids and then use the find_match_new method to complete the trade at the maximum outstanding bid
                    match_new = find_match_new(buyers=buyers, sellers=[player], offer_type='ask', bids_new=bids_new,
                                               asks_new=asks_new)

            if match_new != []: # If a match is found, that is, if a trade occurs, then the following block is executed
                [buyer, seller, buyer_order_type, seller_order_type, last_offer_type] = match_new # Receives the data sent by the math_new method after a match has been found
                if last_offer_type == 'bid': # If trade occurred after a buyer submitted a bid that was higher than the lowest ask price in the queue, then the trade price is that ask price. If trade occurred after a buyer submitted a market order then the trade price is the lowest ask price in the queue
                    price = seller.current_offer
                    asks_new.remove(seller.current_offer) # As the trade has occurred, so the ask price needs to be deleted from the list of outstanding ask prices
                    if type_of_order == 'limit':
                        bids_new.remove(buyer.current_offer) # In the case of a completed limit order, the bid price also needs to be deleted from the list of outstanding bids
                else: # If trade occurred after a seller submitted an ask that was lower than the highest bid in the queue, then the trade price is that bid. If trade occurred after a seller submitted a market order then the trade price is the highest bid price in the queue
                    price = buyer.current_offer
                    bids_new.remove(buyer.current_offer) # As the trade has occurred, so the bid price needs to be deleted from the list of outstanding bids
                    if type_of_order == 'limit':
                        asks_new.remove(seller.current_offer) # In the case of a completed limit order, the ask price also needs to be deleted from the list of outstanding asks

                # The following two nested lists copy buyers and sellers data which is later updated to reflect completed trade(s)
                buyer_inducement = ast.literal_eval(buyer.inducement)
                seller_inducement = ast.literal_eval(seller.inducement)

                for i in range(len(buyer_inducement[buyer.round_number - 1])): # Iterates over the copied data of the buyer for the round in question
                    if buyer_inducement[buyer.round_number - 1][i][2] < buyer_inducement[buyer.round_number - 1][i][1]: # Check if quantity bought at the ith step of induced values for the given round is less than quantity endowed (implying that not all units endowed at this step have been bought yet), othwerwise go to the next step of induced values
                        if buyer_inducement[buyer.round_number - 1][i][5] == 0 or buyer_inducement[buyer.round_number - 1][i][5] == price: # If either no units have been bought yet at the ith step of induced values or if the price at which previous units were bought is the same as that for the current unit bought, then we just need to update data on this step
                            buyer_inducement[buyer.round_number - 1][i][2] = buyer_inducement[buyer.round_number - 1][i][2] + 1 # As an additional unit has beeen bought at ith step of induced values at the same price as previous unit(s), then reflect this change by adding 1 to the number of units bought (if there weren't any prior trades at this step of induced values then just 1 will appear here)
                            buyer_inducement[buyer.round_number - 1][i][3] = buyer_inducement[buyer.round_number - 1][i][3] - 1 # Similar logic to the comment above, reduce 1 from the number of units available
                            buyer_inducement[buyer.round_number - 1][i][4] = buyer_order_type # Whether the buyer placed a limit or a market order which lead to the sale of this unit
                            buyer_inducement[buyer.round_number - 1][i][5] = float(price) # The price at which trade took place
                            buyer_inducement[buyer.round_number - 1][i][6] = buyer_inducement[buyer.round_number - 1][i][0] - float(price) # Unit profit is simply induced value at the step minus the price paid
                            buyer_inducement[buyer.round_number - 1][i][7] = buyer_inducement[buyer.round_number - 1][i][7] + buyer_inducement[buyer.round_number - 1][i][6] # Total profit is simply the existing total profit at this step (if there have been any prior trades) plus the unit profit as an additional unit was bought at this step (If there weren't any prior trades at this step, then it's just the unit profit)
                            buyer.payoff += buyer_inducement[buyer.round_number - 1][i][7]
                            buyer.session_payoff += buyer_inducement[buyer.round_number - 1][i][7]
                            break
                        else:
                            buyer_inducement[buyer.round_number - 1].append([buyer_inducement[buyer.round_number - 1][i][0],
                                                                             buyer_inducement[buyer.round_number - 1][i][3],
                                                                             1,
                                                                             buyer_inducement[buyer.round_number - 1][i][3] - 1,
                                                                             buyer_order_type,
                                                                             float(price),
                                                                             buyer_inducement[buyer.round_number - 1][i][0] - float(price),
                                                                             buyer_inducement[buyer.round_number - 1][i][0] - float(price)
                                                                             ])
                            buyer_inducement[buyer.round_number - 1][i][1] = buyer_inducement[buyer.round_number - 1][i][2]
                            buyer_inducement[buyer.round_number - 1][i][3] = 0
                            buyer.payoff += buyer_inducement[buyer.round_number - 1][i][0] - float(price)
                            buyer.session_payoff += buyer_inducement[buyer.round_number - 1][i][0] - float(price)
                            break

                buyer_inducement[buyer.round_number - 1] = sorted(sorted(buyer_inducement[buyer.round_number - 1], key=lambda x: x[3]), key=lambda x:x[0], reverse=True)

                buyer.inducement = str(copy.deepcopy(buyer_inducement))

                for i in range(len(seller_inducement[seller.round_number - 1])):
                    if seller_inducement[seller.round_number - 1][i][2] < seller_inducement[seller.round_number - 1][i][1]:
                        if seller_inducement[seller.round_number - 1][i][5] == 0 or seller_inducement[seller.round_number - 1][i][5] == price:
                            seller_inducement[seller.round_number - 1][i][2] = seller_inducement[seller.round_number - 1][i][2] + 1
                            seller_inducement[seller.round_number - 1][i][3] = seller_inducement[seller.round_number - 1][i][3] - 1
                            seller_inducement[seller.round_number - 1][i][4] = seller_order_type
                            seller_inducement[seller.round_number - 1][i][5] = float(price)
                            seller_inducement[seller.round_number - 1][i][6] = float(price) - seller_inducement[seller.round_number - 1][i][0]
                            seller_inducement[seller.round_number - 1][i][7] = seller_inducement[seller.round_number - 1][i][7] + seller_inducement[seller.round_number - 1][i][6]
                            seller.payoff += seller_inducement[seller.round_number - 1][i][7]
                            seller.session_payoff += seller_inducement[seller.round_number - 1][i][7]
                            break
                        else:
                            seller_inducement[seller.round_number - 1].append([seller_inducement[seller.round_number - 1][i][0],
                                                                             seller_inducement[seller.round_number - 1][i][3],
                                                                             1,
                                                                             seller_inducement[seller.round_number - 1][i][3] - 1,
                                                                             seller_order_type,
                                                                             float(price),
                                                                             float(price) - seller_inducement[seller.round_number - 1][i][0],
                                                                             float(price) - seller_inducement[seller.round_number - 1][i][0]
                                                                             ])
                            seller_inducement[seller.round_number - 1][i][1] = seller_inducement[seller.round_number - 1][i][2]
                            seller_inducement[seller.round_number - 1][i][3] = 0
                            seller.payoff += float(price) - seller_inducement[seller.round_number - 1][i][0]
                            seller.session_payoff += float(price) - seller_inducement[seller.round_number - 1][i][0]
                            break

                seller_inducement[seller.round_number - 1] = sorted(sorted(seller_inducement[seller.round_number - 1], key=lambda x: x[3]), key=lambda x:x[0])

                seller.inducement = str(copy.deepcopy(seller_inducement))

                tx_sec = Group.timeout_seconds + group.start_timestamp - time.time()
                tx_min, tx_sec = divmod(tx_sec, 60)
                time_tx = str(int(tx_min)) + ":" + str(int(tx_sec))

                Transaction.create(
                    group=group,
                    buyer=buyer,
                    seller=seller,
                    price=price,
                    seconds=time.time() - group.start_timestamp,
                )

                total_units += 1

                if buyer.current_quant != 0:
                    buyer.current_quant = buyer.current_quant - 1
                else:
                    buyer.current_quant = 0

                if seller.current_quant != 0:
                    seller.current_quant = seller.current_quant - 1
                else:
                    seller.current_quant = 0

                if buyer.current_quant == 0 or seller.current_quant == 0:
                    if news == []:
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
                        news.append([
                            buyer.id_in_group,
                            seller.id_in_group,
                            price,
                            total_units - news[0][3],
                            time_tx,
                            buyer_order_type,
                            seller_order_type,
                            last_offer_type
                        ])

                if buyer.current_quant == 0:
                    buyer.current_offer = 0
                    buyer.order_type = ''

                if seller.current_quant == 0:
                    seller.current_offer = 0
                    seller.order_type = ''

            if (player.is_buyer and len(asks_new)==0) or (not player.is_buyer and len(bids_new)==0):
                break


        highcharts_series = [[tx.seconds, tx.price] for tx in Transaction.filter(group=group)]

        bids_new.sort()
        asks_new.sort()

        bids_freq = sorted([[float(x), bids_new.count(x)] for x in set(bids_new)], key=lambda x: x[0], reverse=True)
        asks_freq = sorted([[float(x), asks_new.count(x)] for x in set(asks_new)], key=lambda x: x[0], reverse=True)

        return {
            p.id_in_group: dict(
                bids=bids_freq,
                asks=asks_freq,
                highcharts_series=highcharts_series,
                current_offer=p.current_offer,
                current_quant=p.current_quant,
                inducement=ast.literal_eval(p.inducement),
                news=news,
                event=event,
                payoff=p.payoff,
                session_payoff=p.session_payoff,
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
        player_inducement = ast.literal_eval(player.inducement)
        if player.round_number > 1:
            for i in range(player.round_number):
                player_inducement[i] = ast.literal_eval(player.in_round(i + 1).inducement)[i]
        player.inducement = str(copy.deepcopy(player_inducement))

        if player.round_number > 1:
            player.session_payoff = player.in_round(player.round_number - 1).session_payoff
        else:
            player.session_payoff = 0

        return dict(
            id_in_group=player.id_in_group, is_buyer=player.is_buyer, id_by_role=player.id_by_role,
            type=player.type, cur_round=player.round_number, total_rounds=Group.total_rounds,
            inducement=ast.literal_eval(player.inducement), session_payoff=player.session_payoff,
        )

    @staticmethod
    def get_timeout_seconds(player: Player):
        #group = player.group
        return Group.timeout_seconds
        #return Group.timeout_seconds + group.start_timestamp - time.time()


class MyWaitPage(Page):
    pass

    @staticmethod
    def get_timeout_seconds(player):
        timeout = Group.wait_timeout_seconds
        return timeout

    @staticmethod
    def js_vars(player: Player):
        return dict(
            is_buyer=player.is_buyer, cur_round=player.round_number, total_rounds=Group.total_rounds, period_payoff=float(player.payoff),
            session_payoff=player.session_payoff, wait_timeout=Group.wait_timeout_seconds
        )



class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == Group.total_rounds


page_sequence = [WaitToStart, Trading, MyWaitPage, Results]
