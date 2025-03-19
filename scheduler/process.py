"""
Process class for the scheduler simulation.
"""
from enum import Enum


class ProcessState(Enum):
    """Enum representing the possible states of a process."""
    NEW = 0
    READY = 1
    RUNNING = 2
    WAITING = 3
    TERMINATED = 4


class Process:
    """
    Represents a process in the system with all its relevant attributes
    for scheduling decisions.
    """
    id_counter = 0

    def __init__(self, name=None, arrival_time=0, burst_time=0, priority=0):
        """
        Initialize a new process with the given attributes.

        Args:
            name (str, optional): Name of the process. If None, a name will be generated.
            arrival_time (int, optional): Time when the process arrives in the system.
            burst_time (int, optional): Total CPU time required by the process.
            priority (int, optional): Priority of the process (higher value = higher priority).
        """
        Process.id_counter += 1
        self.pid = Process.id_counter
        self.name = name if name else f"P{self.pid}"
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.state = ProcessState.NEW
        
        # Tracking metrics
        self.start_time = None  # First time the process starts execution
        self.finish_time = None  # Time when the process completes
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = None
        self.context_switches = 0
        
        # For round robin
        self.last_execution_time = 0
        self.execution_history = []
        
        # For accurate waiting time tracking
        self.time_in_ready_queue = 0
        self.last_state_change_time = arrival_time

    def execute(self, time_slice=None, current_time=0):
        """
        Execute the process for the specified time slice or until completion.

        Args:
            time_slice (int, optional): Maximum time to execute. If None, run to completion.
            current_time (float): Current simulation time

        Returns:
            int: Actual time executed
        """
        if self.state != ProcessState.RUNNING:
            # First update time spent in previous state
            self.update_state(ProcessState.RUNNING, current_time)
            
            if self.response_time is None:
                if self.start_time is None:
                    self.start_time = current_time
                # Ensure response time is never negative
                self.response_time = max(0, current_time - self.arrival_time)
                
        if time_slice is None or time_slice >= self.remaining_time:
            executed_time = self.remaining_time
            self.remaining_time = 0
            self.update_state(ProcessState.TERMINATED, current_time + executed_time)
            self.finish_time = current_time + executed_time
        else:
            executed_time = time_slice
            self.remaining_time -= time_slice
            
        self.execution_history.append((current_time, executed_time))
        return executed_time
    
    def preempt(self):
        """
        Preempt the process, moving it from RUNNING to READY state.
        
        Returns:
            bool: True if preemption was successful, False otherwise
        """
        if self.state == ProcessState.RUNNING:
            self.update_state(ProcessState.READY, self.last_state_change_time + 
                              (self.execution_history[-1][0] + self.execution_history[-1][1] - 
                               self.last_state_change_time))
            self.context_switches += 1
            return True
        return False
    
    def activate(self, current_time=0):
        """
        Activate the process, setting its state to READY if it's NEW.
        
        Args:
            current_time (float): Current simulation time
            
        Returns:
            bool: True if activation was successful, False otherwise
        """
        if self.state == ProcessState.NEW:
            self.state = ProcessState.READY
            if self.start_time is None:
                self.start_time = current_time
            self.last_state_change_time = current_time
            return True
        return False
    
    def update_state(self, new_state, current_time):
        """
        Update the process state and track time spent in states.
        
        Args:
            new_state (ProcessState): The new state for the process
            current_time (float): Current simulation time
        """
        # Track time spent in READY state for waiting time calculation
        if self.state == ProcessState.READY:
            self.time_in_ready_queue += (current_time - self.last_state_change_time)
        
        self.state = new_state
        self.last_state_change_time = current_time
    
    def calculate_metrics(self, current_time):
        """
        Calculate performance metrics for this process.
        
        Args:
            current_time (float): Current simulation time
            
        Returns:
            dict: Dictionary with calculated metrics
        """
        # Final update of state time if process is still in READY state
        if self.state == ProcessState.READY:
            self.time_in_ready_queue += (current_time - self.last_state_change_time)
            self.last_state_change_time = current_time
            
        if self.finish_time is None:
            # Process not finished yet
            self.finish_time = current_time
            
        if self.start_time is None:
            # Process never started
            self.start_time = current_time
            
        # Ensure turnaround time is never negative
        self.turnaround_time = max(0, self.finish_time - self.arrival_time)
        
        # Use the explicitly tracked waiting time
        self.waiting_time = self.time_in_ready_queue
        
        return {
            'pid': self.pid,
            'name': self.name,
            'burst_time': self.burst_time,
            'priority': self.priority,
            'waiting_time': self.waiting_time,
            'turnaround_time': self.turnaround_time,
            'response_time': self.response_time,
            'context_switches': self.context_switches
        }
    
    def __repr__(self):
        return (f"Process(pid={self.pid}, name={self.name}, burst={self.burst_time}, "
                f"remaining={self.remaining_time}, priority={self.priority}, state={self.state.name})") 