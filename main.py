from blackjack import BlackJack, Scoreboard
from visualise import plot

# How many decks to shuffle and at which % of cards remaining to reshuffle
decks, depletion = 1, 0.25
# The true counts to simulate
lowest_count, highest_count, step = -16, 20, 4
# How many decks to simulate per true count
N = 1000

def play():
	# Loop through different true counts and compute probabilities
	probabilities = {}
	for count in range(lowest_count, highest_count, step):
		# Initialise emtpy scores
		outcomes = Scoreboard()

		# Play the games
		for _ in range(N):
			game = BlackJack(true_count=count, decks=decks, depletion=depletion)
			game.play()
			outcomes += game.outcomes

		print(f"True count: {count}.")
		print(f"Simulated {outcomes.total} hands.")

		# Store probabilities to draw later
		probabilities[count] = outcomes.gains()

	return probabilities

if __name__ == "__main__":
	probabilities = play()
	# Draw with matplotlib
	plot(probabilities)
