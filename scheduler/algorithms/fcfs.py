"""
First Come First Served (FCFS) scheduling algorithm implementation.
"""
from ..scheduler import Scheduler


class FCFSScheduler(Scheduler):
    """
    First Come First Served scheduler implementation.
    
    This is a non-preemptive scheduler that executes processes in the
    order they arrive.
    """
    
    def __init__(self):
        """Initialize the FCFS scheduler."""
        super().__init__(name="First Come First Served")
        
    def add_to_ready_queue(self, process):
        """
        Add a process to the ready queue.
        
        Args:
            process (Process): The process to add to the queue
        """
        self.ready_queue.append(process)
        
    def schedule(self):
        """
        Select the next process to run based on FCFS policy.
        
        Returns:
            Process: The earliest arrived process, or None if queue is empty
        """
        if not self.ready_queue:
            return None
            
        # Return the first process in the queue (earliest arrival)
        return self.ready_queue[0]
        
    def execute_process(self, process, debug=False):
        """
        Execute the process until completion (FCFS is non-preemptive).
        
        Args:
            process (Process): The process to execute
            debug (bool): Whether to print debug information
        """
        # Remove the process from the ready queue
        self.ready_queue.remove(process)
        
        # Execute until completion
        execution_time = process.execute(time_slice=None, current_time=self.time)
        
        if debug:
            print(f"Executing {process.name} for {execution_time}ms (until completion)")
            
        # Update simulation time
        self.tick(execution_time) 