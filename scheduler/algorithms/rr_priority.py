"""
Round Robin with Priority scheduling algorithm implementation.
"""
from ..scheduler import Scheduler


class RRPriorityScheduler(Scheduler):
    """
    Round Robin with Priority scheduler implementation.
    
    Each process is executed for a fixed time quantum, but processes with
    higher priority are scheduled first. Within the same priority level,
    processes are scheduled in Round Robin fashion.
    """
    
    def __init__(self, time_quantum=2):
        """
        Initialize the RR with Priority scheduler.
        
        Args:
            time_quantum (int): The time slice allocated to each process
        """
        super().__init__(name="Round Robin with Priority")
        self.time_quantum = time_quantum
        # We'll maintain separate queues for each priority level
        self.priority_queues = {}
        
    def add_process(self, process):
        """
        Add a new process to the scheduler.
        
        Args:
            process (Process): The process to add
        """
        super().add_process(process)
        
        # Initialize queue for this priority if it doesn't exist
        if process.priority not in self.priority_queues:
            self.priority_queues[process.priority] = []
        
    def reset(self):
        """Reset the scheduler to its initial state."""
        super().reset()
        self.priority_queues = {}
        for process in self.processes:
            if process.priority not in self.priority_queues:
                self.priority_queues[process.priority] = []
        
    def add_to_ready_queue(self, process):
        """
        Add a process to the appropriate priority queue.
        
        Args:
            process (Process): The process to add to the queue
        """
        # Add to the appropriate priority queue
        if process.priority not in self.priority_queues:
            self.priority_queues[process.priority] = []
            
        self.priority_queues[process.priority].append(process)
        self.ready_queue.append(process)  # Also add to main ready queue for tracking
        
    def get_highest_priority_process(self):
        """
        Get the process with the highest priority from the ready queues.
        
        Returns:
            Process: The highest priority process, or None if all queues are empty
        """
        # Sort priorities in descending order (higher value = higher priority)
        priorities = sorted(self.priority_queues.keys(), reverse=True)
        
        for priority in priorities:
            if self.priority_queues[priority]:
                return self.priority_queues[priority][0]
                
        return None
        
    def schedule(self):
        """
        Select the next process to run using RR with Priority policy.
        
        Returns:
            Process: The next process to run, or None if all queues are empty
        """
        return self.get_highest_priority_process()
        
    def execute_process(self, process, debug=False):
        """
        Execute the process for the time quantum or until completion.
        
        Args:
            process (Process): The process to execute
            debug (bool): Whether to print debug information
        """
        # Remove the process from the ready queue and priority queue
        self.ready_queue.remove(process)
        self.priority_queues[process.priority].remove(process)
        
        # Execute for time quantum or until completion
        execution_time = process.execute(self.time_quantum, current_time=self.time)
        
        if debug:
            if process.remaining_time > 0:
                print(f"Executing {process.name} (priority {process.priority}) for {execution_time}ms "
                      f"(preempted, {process.remaining_time}ms remaining)")
            else:
                print(f"Executing {process.name} (priority {process.priority}) for {execution_time}ms "
                      f"(completed)")
                
        # Update simulation time
        self.tick(execution_time)
        
        # If the process is not finished, add it back to the end of its priority queue
        if process.state != process.state.TERMINATED:
            self.add_to_ready_queue(process) 