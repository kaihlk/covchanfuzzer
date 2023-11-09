import random
import string
import urllib.parse
import csv
import numpy as np
import matplotlib.pyplot as plt

# Function to generate a random fragment with custom mean and standard deviation
def generate_random_fragment(min_length, max_length, mean, std_deviation, fuzzvalue):
    char_sets = {
        "letters_digits": string.ascii_letters + string.digits,
        "subdelimiters": "!$&'()*+,;=",
        "general_delimiters": ":/?#[]@"
    }
    chosen_set = random.choice(list(char_sets.keys()))
    sca1e=20
    # Generate a random length with a Gaussian distribution
    random_border = int(np.random.exponential(sca1e))
    #random_border = max(min_length, min(max_length, random_border))

    fragment = ''.join(random.choice(chosen_set) for _ in range(random_border))
    if random.random() < fuzzvalue:
        fragment = urllib.parse.quote(fragment)
    return len(fragment)

# Parameters
n = 1000  # Number of iterations
min_length = 1
max_length =  100  # 100 KB in bytes
fuzzvalue = 0.1  # Adjust as needed

# Parameter sets for mean and standard deviatidjust these values

# Generate fragments and store their lengths for each parameter set
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
plt.figure(figsize=(10, 6))

lengths = []
for _ in range(n):
    length = generate_random_fragment(min_length, max_length, mean=1, std_deviation=2, fuzzvalue=0.5)
    lengths.append(length)

plt.hist(lengths, bins=1000, density=True, alpha=0.6)

# Configure the plot
plt.title("Distribution of Fragment Lengths")
plt.xlabel("Length")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.show()
