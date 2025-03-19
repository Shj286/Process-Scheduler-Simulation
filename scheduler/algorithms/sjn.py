"""
Shortest Job Next (SJN) scheduling algorithm implementation.
"""
from ..scheduler import Scheduler


class SJNScheduler(Scheduler):
    """
    Shortest Job Next scheduler implementation.
    
    Selects the process with the shortest remaining burst time.
    This is a non-preemptive algorithm - once a process starts running,
    it runs until completion.
    """
    
    def __init__(self):
        """Initialize the SJN scheduler."""
        super().__init__(name="Shortest Job Next")
        
    def add_to_ready_queue(self, process):
        """
        Add a process to the ready queue.
        
        Args:
            process (Process): The process to add to the queue
        """
        self.ready_queue.append(process)
        
    def schedule(self):
        """
        Select the next process to run using SJN policy.
        
        Returns:
            Process: The process with the shortest burst time, or None if queue is empty
        """
        if not self.ready_queue:
            return None
            
        # Find the process with the shortest remaining time
        shortest_process = min(self.ready_queue, key=lambda p: p.remaining_time)
        return shortest_process
        
    def execute_process(self, process, debug=False):
        """
        Execute the process until completion (SJN is non-preemptive).
        
        Args:
            process (Process): The process to execute
            debug (bool): Whether to print debug information
        """
        # Remove the process from the ready queue
        self.ready_queue.remove(process)
        
        # Execute until completion
        execution_time = process.execute()
        
        if debug:
            print(f"Executing {process.name} for {execution_time}ms (until completion)")
            
        # Update simulation time
        self.time += execution_time


class SRTFScheduler(Scheduler):
    """
    Shortest Remaining Time First scheduler implementation.
    
    This is the preemptive version of SJN. It selects the process with the shortest
    remaining time and preempts the current process if a new process with a shorter
    remaining time arrives.
    """
    
    def __init__(self, time_slice=1):
        """
        Initialize the SRTF scheduler.
        
        Args:
            time_slice (int): The maximum time a process can run before checking for preemption
        """
        super().__init__(name="Shortest Remaining Time First")
        self.time_slice = time_slice
        
    def add_to_ready_queue(self, process):
        """
        Add a process to the ready queue.
        
        Args:
            process (Process): The process to add to the queue
        """
        self.ready_queue.append(process)
        
    def schedule(self):
        """
        Select the next process to run using SRTF policy.
        
        Returns:
            Process: The process with the shortest remaining time, or None if queue is empty
        """
        if not self.ready_queue:
            return None
            
        # Find the process with the shortest remaining time
        shortest_process = min(self.ready_queue, key=lambda p: p.remaining_time)
        return shortest_process
        
    def execute_process(self, process, debug=False):
        """
        Execute the process for a time slice or until completion.
        
        Args:
            process (Process): The process to execute
            debug (bool): Whether to print debug information
        """
        # Remove the process from the ready queue
        self.ready_queue.remove(process)
        
        # Execute for time slice or until completion
        execution_time = process.execute(self.time_slice)
        
        if debug:
            if process.remaining_time > 0:
                print(f"Executing {process.name} for {execution_time}ms "
                      f"(preempted, {process.remaining_time}ms remaining)")
            else:
                print(f"Executing {process.name} for {execution_time}ms (completed)")
                
        # Update simulation time
        self.time += execution_time
        
        # If the process is not finished, add it back to the ready queue
        if process.state != process.state.TERMINATED:
            self.add_to_ready_queue(process) 