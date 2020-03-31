from network_components import Sender, Receiver, Scrubber, OLAD_ROADM
import simpy
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

def run_olad_sim(sim_steps, max_throughput, trust_ratio, victim_throughput=10, legit_throughput=7, scrubber_throughput=40, verbose=False):
    sim_results = {}
    for i in range(max_throughput):
        env = simpy.Environment()

        victim = Receiver(env, 'victim', victim_throughput, analyze=True, verbose=verbose)
        scrubber = Scrubber(env, 'scrubber', scrubber_throughput, victim, analyze=True, verbose=verbose)
        olad_roadm = OLAD_ROADM('OLAD', trust_ratio, scrubber, victim, verbose=verbose)

        sender1 = Sender(env, 'legitimate', legit_throughput, evil=False, dest=olad_roadm, verbose=verbose)
        sender2 = Sender(env, 'attacker', i, evil=True, dest=olad_roadm, verbose=verbose)

        print(f'Running scrubber + O-LAD sim: {victim_throughput}Gbps victim capacity, '
              f'{scrubber_throughput}Gbps scrubber capacity, '
              f'{legit_throughput}Gbps legit throughput, {trust_ratio*100}% trust, {i}Gbps volume attack')
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

    max_throughput = 301
    sim_steps = 100
    trust_ratio = 0.3
    x_vals = [i for i in range(max_throughput)]

    # SIM PARAMS HERE
    y_vals = run_olad_sim(sim_steps, max_throughput, trust_ratio, scrubber_throughput=120)

    fig, ax = plt.subplots()

    y1_scrubber = y_vals['scrubber']
    y2_legit = y_vals['OLAD']
    y3_sum = []
    for i in x_vals:
        y3_sum.append(y1_scrubber[i] + y2_legit[i])


    ax.plot(x_vals, y1_scrubber, '^g-', label='Scrubber', markevery=10, ms=11)
    ax.plot(x_vals, y2_legit, 'Db-', label='Trusted', markevery=10, ms=11)
    ax.plot(x_vals, y3_sum, 'sr-', label='Sum', markevery=10, ms=11)

    ax.set_xticks(np.arange(0,max_throughput, step=max_throughput//10))
    ax.set_yticks(np.arange(0,11, step=2))

    ax.set_title('DDoS Attack - With Scrubber + O-LAD')
    ax.set_xlabel('Attack Strength (Gbps)')
    ax.set_ylabel('Throughput (Gbps)')

    plt.legend(loc='upper right', bbox_to_anchor=(1, 1.1), ncol=3)
    plt.grid()
    plt.show()