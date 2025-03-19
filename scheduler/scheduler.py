"""
Base Scheduler implementation that defines the interface for all scheduler algorithms.
"""
from abc import ABC, abstractmethod
import time
from .process import Process, ProcessState


class Scheduler(ABC):
    """
    Abstract base class for all scheduling algorithms.
    Defines the common interface and provides basic functionality.
    """
    
    def __init__(self, name="Generic Scheduler"):
        """
        Initialize a new scheduler.
        
        Args:
            name (str): Name of the scheduler algorithm
        """
        self.name = name
        self.processes = []
        self.ready_queue = []
        self.current_process = None
        self.time = 0
        self.context_switch_overhead = 0.001  # 1ms overhead for context switching
        self.total_idle_time = 0
        self.last_context_switch_time = 0
        
    def add_process(self, process):
        """
        Add a new process to the list of processes managed by this scheduler.
        
        Args:
            process (Process): The process to add
        """
        self.processes.append(process)
        
    def add_processes(self, processes):
        """
        Add multiple processes to the scheduler.
        
        Args:
            processes (list): List of Process objects to add
        """
        self.processes.extend(processes)
        
    def reset(self):
        """Reset the scheduler to its initial state."""
        for process in self.processes:
            process.remaining_time = process.burst_time
            process.state = ProcessState.NEW
            process.start_time = None
            process.finish_time = None
            process.waiting_time = 0
            process.turnaround_time = 0
            process.response_time = None
            process.context_switches = 0
            process.execution_history = []
            
        self.ready_queue = []
        self.current_process = None
        self.time = 0
        self.total_idle_time = 0
        self.last_context_switch_time = 0
        
    @abstractmethod
    def schedule(self):
        """
        Core scheduling function that decides which process to run next.
        Must be implemented by subclasses.
        
        Returns:
            Process: The next process to run, or None if no process is ready
        """
        pass
    
    @abstractmethod
    def add_to_ready_queue(self, process):
        """
        Add a process to the ready queue according to the scheduling policy.
        Must be implemented by subclasses.
        
        Args:
            process (Process): The process to add to the ready queue
        """
        pass
        
    def check_arrivals(self, current_time):
        """
        Check for new process arrivals at the current time and add them to the ready queue.
        
        Args:
            current_time (float): The current simulation time
            
        Returns:
            int: Number of new processes that arrived
        """
        arrivals = 0
        for process in self.processes:
            if (process.state == ProcessState.NEW and 
                process.arrival_time <= current_time):
                process.activate(current_time)
                self.add_to_ready_queue(process)
                arrivals += 1
                
        return arrivals
    
    def tick(self, elapsed_time):
        """
        Update simulation time and process states.
        
        Args:
            elapsed_time (float): Amount of time to advance simulation
        """
        self.time += elapsed_time
    
    def context_switch(self, from_process, to_process):
        """
        Perform a context switch from one process to another.
        
        Args:
            from_process (Process): Process being switched out (can be None)
            to_process (Process): Process being switched in (can be None)
            
        Returns:
            float: The overhead time due to the context switch
        """
        if from_process is not None:
            from_process.preempt()
            
        # Update simulation time with context switch overhead
        self.tick(self.context_switch_overhead)
        self.last_context_switch_time = self.time
        
        self.current_process = to_process
        
        return self.context_switch_overhead
    
    def run(self, until_time=None, debug=False):
        """
        Run the simulation until all processes are complete or until a specified time.
        
        Args:
            until_time (float, optional): Time to run the simulation until
            debug (bool, optional): Whether to print debug information
            
        Returns:
            dict: Statistics about the run
        """
        self.time = 0
        active_processes = len(self.processes)
        
        while active_processes > 0:
            if until_time is not None and self.time >= until_time:
                break
                
            # Check for new arrivals
            self.check_arrivals(self.time)
            
            # Get the next process to run
            next_process = self.schedule()
            
            if next_process is None:
                # CPU is idle, advance time to next arrival
                next_arrival = float('inf')
                for p in self.processes:
                    if p.state == ProcessState.NEW and p.arrival_time < next_arrival:
                        next_arrival = p.arrival_time
                
                if next_arrival == float('inf'):
                    # No more processes to arrive, we're done
                    break
                    
                idle_time = next_arrival - self.time
                self.total_idle_time += idle_time
                self.time = next_arrival
                
                if debug:
                    print(f"CPU idle for {idle_time}ms, advancing to {self.time}ms")
                    
                continue
                
            # Perform context switch if needed
            if self.current_process != next_process:
                switch_overhead = self.context_switch(self.current_process, next_process)
                if debug and switch_overhead > 0:
                    print(f"Context switch: {self.current_process} -> {next_process}, "
                          f"overhead: {switch_overhead}ms")
            
            # Execute the selected process according to algorithm-specific rules
            # This will be implemented by subclasses
            self.execute_process(next_process, debug)
            
            # Count active processes
            active_processes = 0
            for p in self.processes:
                if p.state != ProcessState.TERMINATED:
                    active_processes += 1
        
        # Calculate statistics
        return self.calculate_statistics()
    
    @abstractmethod
    def execute_process(self, process, debug=False):
        """
        Execute the given process according to the scheduling algorithm's rules.
        Must be implemented by subclasses.
        
        Args:
            process (Process): The process to execute
            debug (bool): Whether to print debug information
        """
        pass
    
    def calculate_statistics(self):
        """
        Calculate performance statistics for the simulation.
        
        Returns:
            dict: A dictionary containing various performance metrics
        """
        if not self.processes:
            return {}
            
        total_turnaround = 0
        total_waiting = 0
        total_response = 0
        total_burst = 0
        total_context_switches = 0
        
        process_metrics = []
        
        for p in self.processes:
            # Ensure metrics are calculated for all processes
            metrics = p.calculate_metrics(self.time)
            process_metrics.append(metrics)
            
            total_turnaround += metrics['turnaround_time']
            total_waiting += metrics['waiting_time']
            if metrics['response_time'] is not None:
                total_response += metrics['response_time']
            total_burst += p.burst_time
            total_context_switches += p.context_switches
            
        n = len(self.processes)
        completed = sum(1 for p in self.processes if p.state == ProcessState.TERMINATED)
        
        stats = {
            'scheduler_name': self.name,
            'processes': process_metrics,
            'total_processes': n,
            'completed_processes': completed,
            'avg_turnaround_time': total_turnaround / n if n > 0 else 0,
            'avg_waiting_time': total_waiting / n if n > 0 else 0,
            'avg_response_time': total_response / n if n > 0 else 0,
            'throughput': completed / self.time if self.time > 0 else 0,
            'cpu_utilization': 1.0 - (self.total_idle_time / self.time) if self.time > 0 else 0,
            'total_execution_time': self.time,
            'total_context_switches': total_context_switches
        }
        
        return stats 