from otree.api import *
import time
import random
import math
import copy
import ast
from ast import literal_eval
import json

import settings


class Constants(BaseConstants):
    name_in_url = 'double_auction'
    players_per_group = None
    num_rounds = 1
    #items_per_seller = 3
    #valuation_min = cu(50)
    #valuation_max = cu(110)
    #production_costs_min = cu(10)
    #production_costs_max = cu(80)
    min_induced_price = 20
    num_units = 5
    eq_units_per_player = 5
    #min_price = 0
    #max_price = math.inf

class Subsession(BaseSubsession):
    pass

def creating_session(subsession: Subsession):
    players = subsession.get_players()

    Group.starting_price = random.randint(Constants.min_induced_price, Constants.min_induced_price + 10)
    Group.ending_price = Group.starting_price + Constants.eq_units_per_player*8 - 2

    Group.total_rounds = subsession.session.config['num_rounds']

    #tempp = []

    ##-##The entries in the list below are as follows: 0.induced value, 1.quantity endowed, 2.quantity sold/purchased, 3.quantity available, 4.order type, 5.price, 6.unit profit
    presets_template = [[[0, i+2, 0, i+2, 'NA' , 0, 0] for i in range(Constants.num_units)] for j in range(subsession.session.config['num_rounds'])]

    Group.seller_type1_presets = copy.deepcopy(presets_template)
    Group.seller_type2_presets = copy.deepcopy(presets_template)
    Group.buyer_type1_presets = copy.deepcopy(presets_template)
    Group.buyer_type2_presets = copy.deepcopy(presets_template)

    for i in range (subsession.session.config['num_rounds']):
        for j in range(Constants.num_units):
            Group.seller_type1_presets[i][j][0] = Group.starting_price + 6*i + 4*j
            Group.seller_type2_presets[i][j][0] = Group.starting_price + 6*i + 4*j + 2
            Group.buyer_type1_presets[i][j][0] = Group.ending_price + 6*i - 4*j
            Group.buyer_type2_presets[i][j][0] = Group.ending_price + 6*i - 4*j - 2

    #for i in range(subsession.round_number):
    # print('number of players: ', len(players))
    # print('number of rounds: ', subsession.session.config['num_rounds'])
    # print('starting price: ', Group.starting_price)
    # print('ending price: ', Group.ending_price)
    # print('presets template: ', presets_template)
    # print('seller 1 presets: ', Group.seller_type1_presets)
    # print('seller 2 presets: ', Group.seller_type2_presets)
    # print('buyer 1 presets: ', Group.buyer_type1_presets)
    # print('buyer 2 presets: ', Group.buyer_type2_presets)
    #print('round number: ', i)
    #print('starting price: ', Group.starting_price)
    #print('values: ', tempp)

    #Group.seller_type1_values = [[,0] for i in range(subsession.session.config['num_rounds'])]

    #print ('number of traders on one side of the market: ', len(players)/2, 'denominator: ', int((len(players)/2)//2))

    for p in players:
        # for more buyers, change the 2 to 3
        p.is_buyer = p.id_in_group % 2 != 0
        if p.is_buyer:
            p.id_by_role = int(p.id_in_group // 2) + 1
            if p.id_by_role % 2 != 0:
                p.type = 1
                p.inducement = str(copy.deepcopy(Group.buyer_type1_presets))
            else:
                p.type = 2
                p.inducement = str(copy.deepcopy(Group.buyer_type2_presets))
            #p.num_items = 0
            #p.break_even_point = random.randint(Constants.valuation_min, Constants.valuation_max)
        else:
            p.id_by_role = int(p.id_in_group / 2)
            if p.id_by_role % 2 != 0:
                p.type = 1
                p.inducement = str(copy.deepcopy(Group.seller_type1_presets))
            else:
                p.type = 2
                p.inducement = str(copy.deepcopy(Group.seller_type2_presets))
            #p.num_items = Constants.items_per_seller
            #p.break_even_point = random.randint(Constants.production_costs_min, Constants.production_costs_max)
            #p.current_offer = Constants.valuation_max + 1
        p.current_offer = 0

        #if len(players) > 2:
            #if math.ceil(p.id_by_role / int((len(players) / 2) // 2)) > 1:
                #p.type = 2
            #else:
                #p.type = 1
        #else:
            #p.type = 1

        #if p.is_buyer:
            #if p.type == 1:
                #p.inducement = str(copy.deepcopy(Group.buyer_type1_presets))
            #else:
                #p.inducement = str(copy.deepcopy(Group.buyer_type2_presets))
        #else:
            #if p.type == 1:
                #p.inducement = str(copy.deepcopy(Group.seller_type1_presets))
            #else:
                #p.inducement = str(copy.deepcopy(Group.seller_type2_presets))


        #print ('id in group: ', p.id_in_group, 'is buyer: ', p.is_buyer, 'id by role: ', p.id_by_role, 'inducement: ', p.inducement)


            #print('role: ', p.is_buyer, ' id by role: ', p.id_by_role, 'computed value: ', math.ceil(p.id_by_role/int((len(players)/2)//2)), 'p_type: ', p.type)


class Group(BaseGroup):
    start_timestamp = models.IntegerField()
    starting_price = models.FloatField()
    ending_price = models.FloatField()
    seller_type1_presets = models.StringField()
    seller_type2_presets = models.StringField()
    buyer_type1_presets = models.StringField()
    buyer_type2_presets = models.StringField()
    total_rounds = models.IntegerField()

class Player(BasePlayer):
    is_buyer = models.BooleanField()
    current_offer = models.FloatField(initial=0)
    current_quant = models.IntegerField(initial=0)
    order_type = models.StringField()
    #break_even_point = models.CurrencyField()
    #num_items = models.IntegerField()
    id_by_role = models.IntegerField()
    type = models.IntegerField()
    inducement = models.LongStringField()


class Transaction(ExtraModel):
    group = models.Link(Group)
    buyer = models.Link(Player)
    seller = models.Link(Player)
    price = models.FloatField()
    seconds = models.IntegerField(doc="Timestamp (seconds since beginning of trading)")


#def find_match(buyers, sellers):
    #for buyer in buyers:
        #for seller in sellers:
            #if seller.num_items > 0 and seller.current_offer <= buyer.current_offer:
                #return [buyer, seller]


def find_match_new(buyers, sellers, offer_type, bids_new, asks_new):
    if offer_type == 'bid':
        for buyer in buyers:
            for seller in sellers:
                if seller.current_offer == min(asks_new):
                    return [buyer, seller, buyer.order_type, seller.order_type, offer_type]
    else:
        for seller in sellers:
            for buyer in buyers:
                if buyer.current_offer == max(bids_new):
                    return [buyer, seller, buyer.order_type, seller.order_type, offer_type]



def live_method(player: Player, data):
    group = player.group
    players = group.get_players()
    buyers = [p for p in players if p.is_buyer]
    sellers = [p for p in players if not p.is_buyer]
    news = None
    event = None

    bids_new = []
    asks_new = []

    if data:
        #bids_new = sorted([p.current_offer for p in buyers if p.current_offer > 0], reverse=True)
        #asks_new = sorted([p.current_offer for p in sellers if p.current_offer > 0])

        if data['market_order'] != "":
            type_of_order = 'market'
        else:
            type_of_order = 'limit'

        player.order_type = type_of_order

        if type_of_order == 'limit':
            try:
                offer = float(data['limit_order'])
                quant = int(data['quant'])
            except Exception:
                #print('invalid message received:', data)
                return
            player.current_offer = offer
        else:
            try:
                quant = int(data['quant'])
            except Exception:
                return

        player.current_quant = quant

        for p in buyers:
            if p.current_quant != 0:
                for i in range(p.current_quant):
                    if p.current_offer != 0:
                        bids_new.append(p.current_offer)

        bids_new.sort()

        for p in sellers:
            if p.current_quant != 0:
                for i in range(p.current_quant):
                    if p.current_offer != 0:
                        asks_new.append(p.current_offer)

        asks_new.sort()

        #bids_new = sorted([p.current_offer for p in buyers if p.current_offer > 0], reverse=True)
        #asks_new = sorted([p.current_offer for p in sellers if p.current_offer > 0], reverse=True)

        match_new = []

        if type_of_order == 'limit':
            if player.is_buyer and len(asks_new) > 0:
                if player.current_offer > min(asks_new):
                    match_new = find_match_new(buyers=[player], sellers=sellers, offer_type='bid', bids_new=bids_new,
                                               asks_new=asks_new)
            elif not player.is_buyer and len(bids_new) > 0:
                if player.current_offer < max(bids_new):
                    match_new = find_match_new(buyers=buyers, sellers=[player], offer_type='ask', bids_new=bids_new,
                                               asks_new=asks_new)
        else:
            if player.is_buyer and len(asks_new) > 0:
                match_new = find_match_new(buyers=[player], sellers=sellers, offer_type='bid', bids_new=bids_new,
                                           asks_new=asks_new)
            elif not player.is_buyer and len(bids_new) > 0:
                match_new = find_match_new(buyers=buyers, sellers=[player], offer_type='ask', bids_new=bids_new,
                                           asks_new=asks_new)

        event = dict(id_sender=player.id_in_group, time_event=time.strftime('%H:%M'),
                     offer_amt=player.current_offer, offer_qt=player.current_quant,order_type=type_of_order)

        if match_new != []:
            [buyer, seller, buyer_order_type, seller_order_type, last_offer_type] = match_new
            if last_offer_type == 'bid':
                price = seller.current_offer
                asks_new.remove(seller.current_offer)
                if type_of_order == 'limit':
                    bids_new.remove(buyer.current_offer)
            else:
                price = buyer.current_offer
                bids_new.remove(buyer.current_offer)
                if type_of_order == 'limit':
                    asks_new.remove(seller.current_offer)

            buyer_inducement = ast.literal_eval(buyer.inducement)
            seller_inducement = ast.literal_eval(seller.inducement)

            for i in range(len(buyer_inducement[buyer.round_number - 1])):
                if buyer_inducement[buyer.round_number - 1][i][2] < buyer_inducement[buyer.round_number - 1][i][1]:
                    if buyer_inducement[buyer.round_number - 1][i][5] == 0 or buyer_inducement[buyer.round_number - 1][i][5] == price:
                        buyer_inducement[buyer.round_number - 1][i][2] = buyer_inducement[buyer.round_number - 1][i][2] + 1
                        buyer_inducement[buyer.round_number - 1][i][3] = buyer_inducement[buyer.round_number - 1][i][3] - 1
                        buyer_inducement[buyer.round_number - 1][i][4] = buyer_order_type
                        buyer_inducement[buyer.round_number - 1][i][5] = float(price)
                        buyer_inducement[buyer.round_number - 1][i][6] = buyer_inducement[buyer.round_number - 1][i][0] - float(price)
                        buyer.payoff += buyer_inducement[buyer.round_number - 1][i][6]
                        break
                    else:
                        buyer_inducement[buyer.round_number - 1].append([buyer_inducement[buyer.round_number - 1][i][0],
                                                                         buyer_inducement[buyer.round_number - 1][i][3],
                                                                         1,
                                                                         buyer_inducement[buyer.round_number - 1][i][3] - 1,
                                                                         buyer_order_type,
                                                                         float(price),
                                                                         buyer_inducement[buyer.round_number - 1][i][0] - float(price)
                                                                         ])
                        buyer_inducement[buyer.round_number - 1][i][1] = buyer_inducement[buyer.round_number - 1][i][2]
                        buyer_inducement[buyer.round_number - 1][i][3] = 0
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
                        seller.payoff += seller_inducement[seller.round_number - 1][i][6]
                        break
                    else:
                        seller_inducement[seller.round_number - 1].append([seller_inducement[seller.round_number - 1][i][0],
                                                                         seller_inducement[seller.round_number - 1][i][3],
                                                                         1,
                                                                         seller_inducement[seller.round_number - 1][i][3] - 1,
                                                                         seller_order_type,
                                                                         float(price),
                                                                         float(price) - seller_inducement[seller.round_number - 1][i][0]
                                                                         ])
                        seller_inducement[seller.round_number - 1][i][1] = seller_inducement[seller.round_number - 1][i][2]
                        seller_inducement[seller.round_number - 1][i][3] = 0
                        break

            seller_inducement[seller.round_number - 1] = sorted(sorted(seller_inducement[seller.round_number - 1], key=lambda x: x[3]), key=lambda x:x[0])

            seller.inducement = str(copy.deepcopy(seller_inducement))

            Transaction.create(
                group=group,
                buyer=buyer,
                seller=seller,
                price=price,
                seconds=int(time.time() - group.start_timestamp),
            )
            news = dict(buyer=buyer.id_in_group, seller=seller.id_in_group, price=price, time_tx=time.strftime('%H:%M'),
                        buyer_order_type=buyer_order_type, seller_order_type=seller_order_type, last_offer_type=last_offer_type)

            if buyer.current_quant != 0:
                buyer.current_quant = buyer.current_quant - 1

            if seller.current_quant != 0:
                seller.current_quant = seller.current_quant - 1

            if buyer.current_quant == 0:
                buyer.current_offer = 0
                buyer.order_type = ''

            if seller.current_quant == 0:
                seller.current_offer = 0
                seller.order_type = ''


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
                inducement=ast.literal_eval(p.inducement),
                news=news,
                event=event,
                payoff=p.payoff,
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
        return dict(
            id_in_group=player.id_in_group, is_buyer=player.is_buyer, id_by_role=player.id_by_role,
            type=player.type, cur_round=player.round_number, total_rounds=Group.total_rounds,
            inducement=ast.literal_eval(player.inducement)
        )

    @staticmethod
    def get_timeout_seconds(player: Player):
        import time

        group = player.group
        return 120 * 60 + group.start_timestamp - time.time()


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [WaitToStart, Trading, ResultsWaitPage, Results]
