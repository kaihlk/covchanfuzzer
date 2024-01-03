import random
import string
import urllib.parse
import csv
import numpy as np
import matplotlib.pyplot as plt

# Function to generate a random fragment with custom mean and standard deviation
def generate_random_fragment(min_length, max_length, fuzzvalue, scale):
    char_sets = {
        "letters_digits": string.ascii_letters + string.digits,
        "subdelimiters": "!$&'()*+,;=",
        "general_delimiters": ":/?#[]@"
    }
    chosen_set = random.choice(list(char_sets.keys()))
    
   
    random_border = int(np.random.exponential(scale)*1024)
    #random_border = max(min_length, min(max_length, random_border))

    fragment = ''.join(random.choice(chosen_set) for _ in range(random_border))
    if random.random() < fuzzvalue:
        fragment = urllib.parse.quote(fragment)
    return len(fragment)

n = 100  # Number of iterations
min_length = 1
max_length = 100  # 100 KB in bytes
fuzzvalue = 0.1  # Adjust as needed



scales=[2,4,8]
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
plt.figure(figsize=(10, 6))

for scale, color in zip(scales, colors):
    lengths = [generate_random_fragment(min_length, max_length, fuzzvalue, scale) for _ in range(n)]
    plt.hist(lengths, bins=1024, density=True, alpha=0.6, label=f'Scale {scale}', color=color)

# Configure the plot
plt.title("Distribution of Fragment Lengths")
plt.xlabel("Length")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.show()