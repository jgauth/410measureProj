from baseline import run_baseline_sim
from scrubbing import run_scrubbing_sim
from olad import run_olad_sim
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

sim_steps = 100
max_throughput = 101

baseline_vals = run_baseline_sim(sim_steps, max_throughput, verbose=False)
scrubbing_vals = run_scrubbing_sim(sim_steps, max_throughput, verbose=False)
olad1_vals = run_olad_sim(sim_steps, max_throughput, 0.4, verbose=False)
olad2_vals = run_olad_sim(sim_steps, max_throughput, 0.8, verbose=False)

x_vals = [i for i in range(max_throughput)]

######################################################

fig, ax = plt.subplots()

y_baseline = baseline_vals['trusted']
y_attacker = baseline_vals['attacker']

ax.plot(x_vals, y_baseline, 'Db-', label='Legitimate', markevery=10, ms=15)
ax.plot(x_vals, y_attacker, '*r-', label='Attacker', markevery=10, ms=15)

ax.set_xticks(np.arange(0,101, step=10))
ax.set_yticks(np.arange(0,11, step=2))

# ax.set_title('DDoS Attack - No Defense (Baseline)')
ax.set_xlabel('Attack Strength (Gbps)')
ax.set_ylabel('Throughput (Gbps)')

plt.legend(loc='upper right', bbox_to_anchor=(1, 1.1), ncol=2)
plt.grid()
plt.show()

######################################################

fig, ax = plt.subplots()

y_baseline = baseline_vals['trusted']
y_scrubbing = scrubbing_vals['scrubber']

ax.plot(x_vals, y_baseline, 'Db-', label='Baseline', markevery=10, ms=15)
ax.plot(x_vals, y_scrubbing, '^g-', label='Legitimate', markevery=10, ms=15)

ax.set_xticks(np.arange(0,101, step=10))
ax.set_yticks(np.arange(0,11, step=2))

# ax.set_title('DDoS Attack - With Scrubber')
ax.set_xlabel('Attack Strength (Gbps)')
ax.set_ylabel('Throughput (Gbps)')

plt.legend(loc='upper right', bbox_to_anchor=(1, 1.1), ncol=2)
plt.grid()
plt.show()


######################################################

fig, ax = plt.subplots()

y_baseline = baseline_vals['trusted']

y1_scrubber = olad1_vals['scrubber']
y2_legit = olad1_vals['OLAD']
y3_sum = []
for i in x_vals:
    y3_sum.append(y1_scrubber[i] + y2_legit[i])

ax.plot(x_vals, y1_scrubber, '^g-', label='Scrubber', markevery=10, ms=15)
ax.plot(x_vals, y2_legit, 'Db-', label='Trusted', markevery=10, ms=15)
ax.plot(x_vals, y3_sum, 'sr-', label='Sum', markevery=10, ms=15)

ax.set_xticks(np.arange(0,101, step=10))
ax.set_yticks(np.arange(0,11, step=2))

# ax.set_title('DDoS Attack - With Scrubber + O-LAD (40% Trust)')
ax.set_xlabel('Attack Strength (Gbps)')
ax.set_ylabel('Throughput (Gbps)')

plt.legend(loc='upper right', bbox_to_anchor=(1, 1.1), ncol=3)
plt.grid()
plt.show()


######################################################

fig, ax = plt.subplots()

y_baseline = baseline_vals['trusted']

y1_scrubber = olad2_vals['scrubber']
y2_legit = olad2_vals['OLAD']
y3_sum = []
for i in x_vals:
    y3_sum.append(y1_scrubber[i] + y2_legit[i])

ax.plot(x_vals, y1_scrubber, '^g-', label='Scrubber', markevery=10, ms=15)
ax.plot(x_vals, y2_legit, 'Db-', label='Trusted', markevery=10, ms=15)
ax.plot(x_vals, y3_sum, 'sr-', label='Sum', markevery=10, ms=15)

ax.set_xticks(np.arange(0,101, step=10))
ax.set_yticks(np.arange(0,11, step=2))

# ax.set_title('DDoS Attack - With Scrubber + O-LAD (80% Trust)')
ax.set_xlabel('Attack Strength (Gbps)')
ax.set_ylabel('Throughput (Gbps)')

plt.legend(loc='upper right', bbox_to_anchor=(1, 1.1), ncol=3)
plt.grid()
plt.show()