"""
Round Robin (RR) scheduling algorithm implementation.
"""
from ..scheduler import Scheduler


class RRScheduler(Scheduler):
    """
    Round Robin scheduler implementation.
    
    Each process is executed for a fixed time quantum in a circular order.
    If a process doesn't complete in its time quantum, it is preempted and
    added back to the end of the ready queue.
    """
    
    def __init__(self, time_quantum=2):
        """
        Initialize the RR scheduler.
        
        Args:
            time_quantum (int): The time slice allocated to each process
        """
        super().__init__(name="Round Robin")
        self.time_quantum = time_quantum
        
    def add_to_ready_queue(self, process):
        """
        Add a process to the ready queue (append to end).
        
        Args:
            process (Process): The process to add to the queue
        """
        self.ready_queue.append(process)
        
    def schedule(self):
        """
        Select the next process to run using RR policy.
        
        Returns:
            Process: The next process to run, or None if the queue is empty
        """
        if not self.ready_queue:
            return None
            
        # In RR, we select the process at the front of the queue
        return self.ready_queue[0]
        
    def execute_process(self, process, debug=False):
        """
        Execute the process for the time quantum or until completion.
        
        Args:
            process (Process): The process to execute
            debug (bool): Whether to print debug information
        """
        # Remove the process from the ready queue
        self.ready_queue.remove(process)
        
        # Execute for time quantum or until completion
        execution_time = process.execute(self.time_quantum)
        
        if debug:
            if process.remaining_time > 0:
                print(f"Executing {process.name} for {execution_time}ms (preempted, "
                      f"{process.remaining_time}ms remaining)")
            else:
                print(f"Executing {process.name} for {execution_time}ms (completed)")
                
        # Update simulation time
        self.time += execution_time
        
        # If the process is not finished, add it back to the end of the queue
        if process.state != process.state.TERMINATED:
            self.add_to_ready_queue(process) 