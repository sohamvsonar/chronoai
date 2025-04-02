import matplotlib.pyplot as plt

# --- Sample benchmark results (in seconds) ---
duration_without = 229.57   # e.g., benchmark without logging
duration_with = 186.86      # e.g., benchmark with logging

# --- Data for the graph ---
labels = ['Without ChronoLog Logging', 'With ChronoLog Logging']
times = [duration_without, duration_with]

# --- Create the bar chart ---
plt.figure(figsize=(8, 6))
bars = plt.bar(labels, times, color=['tomato', 'gold'], edgecolor='black')

plt.xlabel('Logging Mode', fontsize=14)
plt.ylabel('Duration (seconds)', fontsize=14)
plt.title('Benchmark of Internal LLM \n with and without ChronoLog logging', fontsize=16, fontweight='bold')

plt.figtext(0.5, 0.01, "100 iterations of prompts and responses", ha="center", fontsize=12)

# Annotate bars with the actual duration values
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.2, f'{yval:.2f}', ha='center', va='bottom', fontsize=12)

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout(rect=[0, 0.03, 1, 1])  # Adjust layout to make room for the figtext

# Save the graph as a PNG image and display it
plt.savefig("graphs/internal_benchmark_comparison.png")
plt.show()
