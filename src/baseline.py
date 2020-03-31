from network_components import Receiver, Sender
import simpy
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

def run_baseline_sim(sim_steps, max_throughput, victim_throughput=10, legit_throughput=7, verbose=False):
    sim_results = {}
    for i in range(max_throughput):
        env = simpy.Environment()

        victim = Receiver(env, 'victim', victim_throughput, analyze=True, verbose=verbose)

        sender1 = Sender(env, 'trusted', legit_throughput, evil=False, dest=victim, verbose=verbose)
        sender2 = Sender(env, 'attacker', i, evil=True, dest=victim, verbose=verbose)

        print(f'Running baseline sim: {victim_throughput}Gbps victim capacity, '
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
    y_vals = run_baseline_sim(sim_steps, max_throughput)

    fig, ax = plt.subplots()


    y1 = y_vals['trusted']
    y2 = y_vals['attacker']


    ax.plot(x_vals, y1, 'Db-', label='Legitimate', markevery=10, ms=11)
    ax.plot(x_vals, y2, '*r-', label='Attacker', markevery=10, ms=11)

    ax.set_xticks(np.arange(0,101, step=10))
    ax.set_yticks(np.arange(0,11, step=2))

    ax.set_title('DDoS Attack - No Defense (Baseline)')
    ax.set_xlabel('Attack Strength (Gbps)')
    ax.set_ylabel('Throughput (Gbps)')

    plt.legend(loc='upper right', bbox_to_anchor=(1, 1.1), ncol=2)
    plt.grid()
    plt.show()
