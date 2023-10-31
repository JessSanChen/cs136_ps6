#!/usr/bin/env python

import sys

from gsp import GSP
from util import argmax_index
from util import argmax_index, shuffled, mean, stddev
from stats import Stats



class G41budget:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value / 2


    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)
        other_bids = [a_id_b for a_id_b in prev_round.bids if a_id_b[0] != self.id]

        clicks = prev_round.clicks
        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)
            
        info = list(map(compute, list(range(len(clicks)))))
#        sys.stdout.write("slot info: %s\n" % info)
        return info


    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """
        # TODO: Fill this in
        utilities = []   # Change this

        prev_round = history.round(t-1)
        # other_bids = [a_id_b for a_id_b in prev_round.bids if a_id_b[0] != self.id]
        clicks = prev_round.clicks
        bids = prev_round.bids 

        # print("reserve: ", reserve)

        # extract bids from previous round; omit own bid; use reserve price; sort
        bids_only = [bid for agent_id, bid in bids if agent_id != self.id]
        bids_only.append(reserve) # append reserve price
        bids_only = sorted(bids_only, reverse=True) # sort bids in descending order

        # for each slot, calculate utilities
        #### IS IT GUARANTEED THAT WE'RE USING THE RIGHT BID VALUES PER SLOT??
        ## we're finding the WINNING bid, not the payment. so bids_only[j], NOT j+1
        utilities = [clicks[j] * (self.value - bids_only[j]) for j in range(len(clicks))]
        
        return utilities

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i =  argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[i]

    def bid(self, t, history, reserve):
        # The Balanced bidding strategy (BB) is the strategy for a player j that, given
        # bids b_{-j},
        # - targets the slot s*_j which maximizes his utility, that is,
        # s*_j = argmax_s {clicks_s (v_j - t_s(j))}.
        # - chooses his bid b' for the next round so as to
        # satisfy the following equation:
        # clicks_{s*_j} (v_j - t_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
        # (p_x is the price/click in slot x)
        # If s*_j is the top slot, bid the value v_j

        prev_round = history.round(t-1)
        (slot, min_bid, max_bid) = self.target_slot(t, history, reserve)

        # TODO: Fill this in.
        bid = 0  # change this

        clicks = prev_round.clicks
        bids = prev_round.bids

        # extract bids from previous round; omit own bid; use reserve price; sort
        bids_only = [bid for agent_id, bid in bids if agent_id != self.id]
        bids_only.append(reserve) # append reserve price
        bids_only = sorted(bids_only, reverse=True) # sort bids in descending order

        # price of target slot
        price_js = bids_only[slot] #### again, NOT slot+1

        # try not to bid when prices are high
        # take average of same slot from multiple previous rounds?
        if t > 5:
            five_prev_rounds = [history.round(t-r-1) for r in range(5)]
            five_bids = [prev.bids for prev in five_prev_rounds]
            slot_bids = []
            for prev_bids in five_bids:
                prev_bids_only = [bid for agent_id, bid in prev_bids if agent_id != self.id]
                prev_bids_only.append(reserve) # append reserve price
                prev_bids_only = sorted(prev_bids_only, reverse=True) # sort bids in descending order
                slot_bids.append(prev_bids_only[slot])
            m = mean(slot_bids)
            std = stddev(slot_bids)
            if t < 44: # be budget conserving
                if price_js > m + std:
                    return 0
                elif price_js < m - 1.5*std:
                    return self.value
            else: # bid everything
                return self.value 

        # not expecting to win
        if price_js >= self.value: 
            bid = self.value
            # bid = self.value - (clicks[slot]*(self.value - price_js))/clicks[slot-1]
        else:
            # not going for top
            if slot > 0:
                bid = self.value - (clicks[slot]*(self.value - price_js))/clicks[slot-1]
            elif slot == 0: # going for the top
                bid = self.value
            else:
                return IndexError("Invalid target slot")
        
        return bid

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


