import random
import string
import urllib.parse
import csv
import matplotlib.pyplot as plt
import numpy as np

# Function to generate a random fragment with custom mean and standard deviation
# (Same function as in the previous response)

# Parameters
n = 1000  # Number of iterations
min_length = 1
max_length = 100  # Maximum length set to 100 (1-100 range)
fuzzvalue = 0.1  # Adjust as needed

# Parameter set for the exponential distribution
scale = 20  # You can adjust this value to control the shape of the distribution

# Generate fragments and store their lengths using the exponential distribution
lengths = np.random.exponential(scale, n).round().astype(int)

lengths[lengths > max_length] = max_length

# Plot the distribution
plt.figure(figsize=(10, 6))
plt.hist(lengths, bins=1000, density=True, alpha=0.6, color='b', label="Exponential Distribution")

# Configure the plot
plt.title("Distribution of Fragment Lengths")
plt.xlabel("Length")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.show()