import seaborn as sns
import numpy as np
from matplotlib import pyplot as plt

def kelly(f, p):
	g_0 = p["0"] * np.log(1 - f)
	g_1 = p["1"] * np.log(1 - f + f*1)
	g_2 = p["2"] * np.log(1 - f + f*2)
	g_25 = p["2.5"] * np.log(1 - f + f*2.5)
	growth_rate = g_0 + g_1 + g_2 + g_25 
	
	return growth_rate

def plot(probabilities, N = 1000):
	plt.figure(figsize=(12, 8))

	palette = sns.color_palette("coolwarm", len(probabilities.keys()))

	highest = 0
	highest_idx = 0

	idx = 0
	for count, p in probabilities.items():
		x = np.arange(0, 1, 1/N)
		y = kelly(x, p)

		# Determine highest growth rate
		if np.max(y) > highest:
			highest = np.max(y)
			highest_idx = np.argmax(y) / N

		sns.lineplot(x = x, y = y, label=f"True Count: {count}", color=palette[idx])

		idx += 1

	plt.axvline(x = highest_idx, color="green")
	plt.text(highest_idx - 0.02, 0.1, f'Fraction to invest: {round(highest, 4) * 100}%', rotation=90)

	# Customize the axes
	plt.xlim(0, 1)  # Set x-axis limits
	plt.ylim(-1, 0.5)  # Set y-axis limits
	plt.xticks(np.arange(0, 1.1, 0.2))  # Set x-ticks
	plt.yticks(np.arange(-1, 0.5, 0.5))  # Set y-ticks

	# Remove top and bottom spines
	plt.gca().spines['top'].set_visible(False)
	plt.gca().spines['bottom'].set_visible(False)

	# Show only left and right spines
	plt.gca().spines['left'].set_visible(True)
	plt.gca().spines['right'].set_visible(True)

	plt.axhline(y=0, color='k')

	plt.xlabel("Fraction to invest")
	plt.ylabel("Growth rate")
	plt.title('Growth rates at different invested fractions (comparing different true counts)')

	# Show the legend
	plt.legend()

	# Show the plot
	plt.grid(False)  # Disable grid
	plt.tight_layout()  # Adjust layout to fit labels
	plt.show()