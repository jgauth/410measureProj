from network_components import Sender, Receiver, Scrubber
import simpy
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

def run_scrubbing_sim(sim_steps, max_throughput, victim_throughput=10, legit_throughput=7, scrubber_throughput=40, verbose=False):
    sim_results = {}
    for i in range(max_throughput):
        env = simpy.Environment()

        victim = Receiver(env, 'victim', victim_throughput, analyze=True, verbose=verbose)
        scrubber = Scrubber(env, 'scrubber', scrubber_throughput, victim, analyze=True, verbose=verbose)

        sender1 = Sender(env, 'trusted', legit_throughput, evil=False, dest=scrubber, verbose=verbose)
        sender2 = Sender(env, 'attacker', i, evil=True, dest=scrubber, verbose=verbose)

        print(f'Running scrubber sim: {victim_throughput}Gbps victim capacity, '
              f'{scrubber_throughput}Gbps scrubber capacity, '
              f'{legit_throughput}Gbps legit throughput, {i}Gbps volume attack')
        env.run(until=sim_steps)

        for flow in victim.flow_data:
            src = flow[0].id
            if src not in sim_results:
                sim_results[src] = []

            # inter arrival times
            inter_arrival_times = victim.flow_data[flow]['inter_arrivals']
            if len(inter_arrival_times) == 0:
                effective_rate = 0
            else:
                avg_inter_arrival = sum(inter_arrival_times) / len(inter_arrival_times)
                effective_rate = round(1/avg_inter_arrival, 4)
            
            sim_results[src].append(effective_rate)
    
    return sim_results


if __name__ == '__main__':

    max_throughput = 101
    sim_steps = 80
    x_vals = [i for i in range(max_throughput)]
    y_vals = run_scrubbing_sim(sim_steps, max_throughput)

    fig, ax = plt.subplots()

    y1 = y_vals['scrubber']

    ax.plot(x_vals, y1, '^g-', label='Legitimate', markevery=10, ms=11)

    ax.set_xticks(np.arange(0,101, step=10))
    ax.set_yticks(np.arange(0,11, step=2))

    ax.set_title('DDoS Attack - With Scrubber')
    ax.set_xlabel('Attack Strength (Gbps)')
    ax.set_ylabel('Throughput (Gbps)')

    plt.legend(loc='upper right', bbox_to_anchor=(1, 1.1), ncol=1)
    plt.grid()
    plt.show()