import simpy
import random

class Packet():
    """
    Smallest unit of data passed between network components
    """

    def __init__(self, id, size, evil, src, dest, t_start):
        """
        Packet constructor

        Args:
            id (int): Identifier
            size (int): Size of packet 
            evil (bool): Evil bit - indicates if packet has evil intent (RFC3514)
            src: Source object
            dest: Destination object
        """
        self.id = id
        self.size = size
        self.src = src
        self.dest = dest
        self.t_start = t_start
        self.t_end = None

    def __repr__(self):
        return (f'<{type(self).__name__} id={self.id} size={self.size} src={self.src.id} dest={self.dest.id}>')


class Sender():
    """
    Sends packets at rate to dest

    Note:
        Must set dest attribute before starting
    """

    def __init__(self, env, id, rate, evil, dest=None, verbose=False):
        """
        Sender constructor

        Args:
            env (simpy.Environment): Simpy environment
            id: Identifier
            rate (int): Number of UNITS (per second) to generate
            evil (bool): Indicates if sender has evil intent
            dest (Receiver): Identifier of destination. Defaults to None.
        """
        self.env = env
        self.id = id
        self.rate = rate
        self.evil = evil
        self.dest = dest
        self.verbose = verbose

        self.action = env.process(self.run())
        self.num_sent = 0
    
    def __repr__(self):
        return (f'<{type(self).__name__} id={self.id} dest={self.dest.id} rate={self.rate}>')

    def run(self):
        """
        Begin generating packets and sending them to dest

        Raises:
            ReferenceError: If dest is not set
        """

        if (self.dest == None):
            raise ReferenceError('dest must be set to a Receiver')
        if (self.rate == 0):
            # send packet size 0 to gather flow info
            packet = Packet(self.num_sent, 0, self.evil, self, self.dest, self.env.now)
            self.dest.handoff(packet)
            return

        while True:
            yield self.env.timeout(1/self.rate)
            if self.verbose:
                print(f'{type(self).__name__} {self.id} sending packet to {self.dest.id} at {self.env.now}')
            packet = Packet(self.num_sent, 1, self.evil, self, self.dest, self.env.now)
            self.num_sent += 1
            self.dest.handoff(packet)


class Receiver():
    """
    Receives packets via handoff(), queues them, and processes them at Rate.
    Collects measurments based on flows where flow=(source, dest)
    """

    def __init__(self, env, id, rate, analyze=False, verbose=False):
        self.env = env
        self.id = id
        self.rate = rate
        self.analyze = analyze
        self.verbose = verbose

        self.flow_data = {}
        self.num_received = 0
        self.queue = simpy.Store(env)
        self.action = env.process(self.run())

    def __repr__(self):
        return (f'<{type(self).__name__} id={self.id}>')
    

    def handoff(self, packet):
        """
        Called by Sender to queue a packet
        """
        self.num_received += 1

        if self.verbose:
            print(f'{type(self).__name__} {self.id} queueing packet from {packet.src.id} at {self.env.now}')
        self.queue.put(packet)

    def run(self):
        while True:

            packet = (yield self.queue.get())
            flow = (packet.src, packet.dest)

            if (packet.size !=0):
                yield self.env.timeout(1/self.rate)

            if self.verbose:
                print(f'{type(self).__name__} {self.id} ending packet from {packet.src.id} at {self.env.now}')

            packet.t_end = self.env.now

            if self.analyze:
                if flow not in self.flow_data:
                    self.flow_data[flow] = {'wait_times': [],
                                       'last_arrival': None,
                                       'inter_arrivals': []}


                t_wait = (packet.t_end - packet.t_start) # per packet wait time
                self.flow_data[flow]['wait_times'].append(t_wait)

                if self.flow_data[flow]['last_arrival'] != None:
                    t_inter_arrival = self.env.now - self.flow_data[flow]['last_arrival']
                    self.flow_data[flow]['inter_arrivals'].append(t_inter_arrival)

                self.flow_data[flow]['last_arrival'] = self.env.now


class Scrubber(Receiver):
    """
    Description of Scrubber
    """

    def __init__(self, env, id, rate, dest=None, analyze=False, verbose=False):
        self.dest = dest
        self.evil = False
        super().__init__(env, id, rate, analyze, verbose)

    def run(self):
        while True:

            packet = (yield self.queue.get())
            flow = (packet.src, packet.dest)

            if (packet.size !=0):
                yield self.env.timeout(1/self.rate)

            if self.verbose:
                print(f'{type(self).__name__} {self.id} ending packet from {packet.src.id} at {self.env.now}')

            packet.t_end = self.env.now

            if self.analyze:
                if flow not in self.flow_data:
                    self.flow_data[flow] = {'wait_times': [],
                                       'last_arrival': None,
                                       'inter_arrivals': []}


                t_wait = (packet.t_end - packet.t_start) # per packet wait time
                self.flow_data[flow]['wait_times'].append(t_wait)

                if self.flow_data[flow]['last_arrival'] != None:
                    t_inter_arrival = self.env.now - self.flow_data[flow]['last_arrival']
                    self.flow_data[flow]['inter_arrivals'].append(t_inter_arrival)

                self.flow_data[flow]['last_arrival'] = self.env.now
            
            if not packet.src.evil:
                packet.src = self
                self.dest.handoff(packet)


class OLAD_ROADM():
    """
    Description of OLAD_ROADM
    """
    def __init__(self, id, trust_ratio, scrubber=None, dest=None, verbose=False):
        # self.env = env
        self.id = id
        self.trust_ratio = trust_ratio
        self.scrubber = scrubber
        self.dest = dest
        self.verbose = verbose

        self.evil = False
        self.num_received = 0
        # self.action = env.process(self.run())

    def handoff(self, packet):
        if packet.src.evil:
            self.scrubber.handoff(packet)
        else:
            # r = random.random()
            # if r < self.trust_ratio:
            #     self.dest.handoff(packet)
            # else:
            #     self.scrubber.handoff(packet)
            magic_number = round(self.trust_ratio * 10)
            if (self.num_received % 10) < magic_number:
                packet.src = self
                self.dest.handoff(packet)
            else:
                self.scrubber.handoff(packet)
            self.num_received += 1
