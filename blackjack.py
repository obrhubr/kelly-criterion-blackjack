from enum import Enum
import numpy as np

# Enum containing the possible moves a player can make
class Move(Enum):
	HIT = 0
	STAND = 1
	SPLIT = 2

class Outcome(Enum):
	PLAYER_BUST = 0
	DEALER_BUST = 1
	PLAYER_BJ = 2
	DEALER_BJ = 3
	PUSH = 4
	DEALER_HIGH = 5
	PLAYER_HIGH = 6

# Class to track outcomes
class Scoreboard:
	def __init__(self):
		self.player_busts = 0
		self.dealer_busts = 0
		self.player_bjs = 0
		self.dealer_bjs = 0
		self.pushes = 0
		self.dealer_highs = 0
		self.player_highs = 0

		self.total = 0
		return

	# Enable adding two scores together
	def __add__(self, other):
		self.player_busts += other.player_busts
		self.dealer_busts += other.dealer_busts
		self.player_bjs += other.player_bjs
		self.dealer_bjs += other.dealer_bjs
		self.pushes += other.pushes
		self.dealer_highs += other.dealer_highs
		self.player_highs += other.player_highs
		
		self.total += other.total

		return self
	
	def __str__(self):
		output = f"Played a total of {self.total} hands.\n"
		output += f"	{self.player_busts} player busts.\n"
		output += f"	{self.dealer_busts} dealer busts.\n"
		output += f"	{self.player_bjs} player bjs.\n"
		output += f"	{self.dealer_bjs} dealer bjs.\n"
		output += f"	{self.pushes} pushes.\n"
		output += f"	{self.dealer_highs} dealer highs.\n"
		output += f"	{self.player_highs} player highs.\n"
		return output
	
	# Add an outcome to the scores
	def add(self, outcome):
		if outcome == Outcome.PLAYER_BUST:
			self.player_busts += 1
		elif outcome == Outcome.DEALER_BUST:
			self.dealer_busts += 1
		elif outcome == Outcome.PLAYER_BJ:
			self.player_bjs += 1
		elif outcome == Outcome.DEALER_BJ:
			self.dealer_bjs += 1
		elif outcome == Outcome.PUSH:
			self.pushes += 1
		elif outcome == Outcome.DEALER_HIGH:
			self.dealer_highs += 1
		elif outcome == Outcome.PLAYER_HIGH:
			self.player_highs += 1

		self.total += 1
		return
	
	def probabilities(self):
		return {
			"player_busts": self.player_busts / self.total,
			"dealer_busts": self.dealer_busts / self.total,
			"player_bjs": self.player_bjs / self.total,
			"dealer_bjs": self.dealer_bjs / self.total,
			"pushes": self.pushes / self.total,
			"dealer_highs": self.dealer_highs / self.total,
			"player_highs": self.player_highs / self.total,
		}
	
	def gains(self):
		probabilities = self.probabilities()
		return {
			"0": probabilities["player_busts"] + probabilities["dealer_bjs"] + probabilities["dealer_highs"],
			"1": probabilities["pushes"],
			"2": probabilities["dealer_busts"] + probabilities["player_highs"],
			"2.5": probabilities["player_bjs"]
		}


class BlackJack:
	def __init__(self, true_count = 0, decks = 2, depletion = 0.25):
		self.deck = self.create_deck(true_count, decks)
		self.initial_length = len(self.deck)
		self.depletion = depletion

		self.outcomes = Scoreboard()

		return
	
	# Create an `n` deck (52 cards each) stack with the specified true count
	def create_deck(self, true_count: int, decks: int):
		if true_count < -16 * decks or true_count > 20 * decks:
			raise ValueError(f"True count must not exceed {20 * decks} of decks or be lower than {true_count < -16} decks for {decks} decks.")

		card_counts = {
			1: 4,   # Aces
			2: 4,   # Twos
			3: 4,   # Threes
			4: 4,   # Fours
			5: 4,   # Fives
			6: 4,   # Sixes
			7: 4,   # Sevens
			8: 4,   # Eights
			9: 4,   # Nines
			10: 16  # Tens (including J, Q, K)
		}

		# Adjust for true count
		if true_count != 0:
			# Define high and low cards
			high_cards, low_cards = [10, 1], list(range(2, 7))

			# Set card type to add and remove from in order to change the true count of the deck
			adjust_cards = high_cards if true_count > 0 else low_cards
			to_remove_cards = low_cards if true_count > 0 else high_cards
			
			# Adjust number of cards in deck based on true count
			# Leave neutral cards untouched
			# Loop until required number of cards has been removed
			removed = 0
			while removed <= abs(true_count):
				removal_card = np.random.choice(to_remove_cards)
				# Only remove from card type if it still exists
				if card_counts[removal_card] > 0:
					card_counts[removal_card] -= 1
					
					# Add card
					card_counts[np.random.choice(adjust_cards)] += 1
					
					# Increase counter of removed cards
					removed += 1
		
		# Adjust for the number of decks
		for card in card_counts:
			card_counts[card] *= decks

		# Create a list of cards
		deck = []
		for card, count in card_counts.items():
			deck += [card] * count
		
		np.random.shuffle(deck)
		
		return deck
	
	# Helper function for debugging deck generation
	def deck_stats(self):
		unique, counts = np.unique(self.deck, return_counts=True)
		occurences = dict(zip(unique, counts))
		print(f"Creating a deck with {len(self.deck)} cards.")
		for key in occurences:
			print(f"Card {key}: {occurences[key]}")
		return

	# Calculate  the soft (highest without busting) score of a hand
	def score(self, hand):
		hand_value = sum(hand)
		
		# Count the number of Aces in the hand
		num_aces = sum(x == 1 for x in hand)
		
		# Try to convert some Aces from 1 to 11 without busting (going over 21)
		while num_aces > 0 and hand_value + 10 <= 21:
			hand_value += 10
			num_aces -= 1
		
		return hand_value
	
	# Optimal player strategy (ported from online guides)
	def move(self, score: int, hand: list, dealer_hand: list):
		# If hand has exactly two cards with the same value, consider split
		if len(hand) == 2 and hand[0] == hand[1]:
			if hand[0] == 1:  # Pair of Aces
				return Move.SPLIT # Always split Aces
			elif hand[0] == 9 and dealer_hand[0] in [2, 3, 4, 5, 6, 8, 9]:
				return Move.SPLIT # Split 9s if dealer shows 2-6, 8-9
			elif hand[0] == 8:  # Pair of 8s
				return Move.SPLIT # Always split 8s
			elif hand[0] == 7 and dealer_hand[0] in [2, 3, 4, 5, 6, 7]:
				return Move.SPLIT # Split 7s if dealer shows 2-7
			elif hand[0] == 6 and dealer_hand[0] in [3, 4, 5, 6]:
				return Move.SPLIT # Split 6s if dealer shows 3-6
			elif hand[0] == 3 and dealer_hand[0] in [4, 5, 6, 7]:
				return Move.SPLIT # Split 3s if dealer shows 4-7
			elif hand[0] == 2 and dealer_hand[0] in [4, 5, 6, 7]:
				return Move.SPLIT # Split 2s if dealer shows 4-7
		
		# Soft hands (Ace + X where X is any card except Ace)
		if 1 in hand:
			if 13 <= score <= 17:
				return Move.HIT
			elif score == 18 and dealer_hand[0] in [9, 10, 1]:
				return Move.HIT
		
		# Hard totals
		if score <= 11:
			return Move.HIT
		if score <= 16 and dealer_hand[0] in [7, 8, 9, 10, 1]:
			return Move.HIT
		if score == 12 and dealer_hand[0] in [2, 3]:
			return Move.HIT

		# Stand by default
		return Move.STAND
	
	def get_cards(self, n):
		# Pop the first n cards from the deck
		cards = self.deck[0:n]
		del self.deck[0:n]
		return cards
	
	# Play a single hand of blackjack
	def play_hand(self):
		player_hand, dealer_hand = self.get_cards(2), self.get_cards(1)
		player_score = self.score(player_hand)

		# Check for a blackjack by the player
		if player_score == 21:
			# Draw a card for the dealer
			dealer_hand += self.get_cards(1)

			# End game in win or push depending on dealer's card
			if self.score(dealer_hand) == 21:
				return Outcome.PUSH
			
			return Outcome.PLAYER_BJ
		
		# Determine if the player hits/stands/splits
		while True:
			assert len(dealer_hand) == 1, "Dealer shouldn't have drawn more than 1 card before players turn"
			move = self.move(player_score, player_hand, dealer_hand)

			# Continue until the player stands
			if move == Move.STAND:
				break

			# If player splits, reset hand and continue on only 1
			if move == Move.SPLIT:
				assert len(player_hand) == 2, "Player can't split more than two cards."
				# Continue playing with half the hand
				# TODO: Properly handle splitting
				player_hand = player_hand[0:1]
				player_score = self.score(player_hand)
				continue

			# Draw next card
			player_hand += self.get_cards(1)
			player_score = self.score(player_hand)

			# Check for player busting
			if player_score > 21:
				return Outcome.PLAYER_BUST

		# Determine if the dealer hits/stands
		# Dealer stands on soft 17
		dealer_score = self.score(dealer_hand)
		while dealer_score < 17:
			# Add to hand
			dealer_hand += self.get_cards(1)
			dealer_score = self.score(dealer_hand)

			# Check if dealer busts
			if dealer_score > 21:
				return Outcome.DEALER_BUST
			
			# Check for dealer blackjack
			if dealer_score == 21 and len(dealer_hand) == 2:
				return Outcome.DEALER_BJ

		# Determine winner by higher score
		if dealer_score > player_score:
			return Outcome.DEALER_HIGH
		elif player_score > dealer_score:
			return Outcome.PLAYER_HIGH
		
		# If dealer and player have an equal score, push
		return Outcome.PUSH
		
	def play(self):
		# While still more than x% of cards on the deck, continue playing
		while len(self.deck) > self.initial_length * self.depletion:
			outcome = self.play_hand()
			self.outcomes.add(outcome)
		return