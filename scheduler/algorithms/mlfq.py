"""
Multi-Level Feedback Queue (MLFQ) scheduling algorithm implementation.

MLFQ is a sophisticated scheduling algorithm that uses multiple priority queues and 
dynamically adjusts process priorities based on their behavior. It favors short,
interactive processes while preventing starvation of longer-running processes.
"""
from ..scheduler import Scheduler
from ..process import ProcessState


class MLFQScheduler(Scheduler):
    """
    Multi-Level Feedback Queue scheduler implementation.
    
    Features:
    - Multiple queues with different priorities and time quanta
    - Processes move between queues based on their behavior
    - Processes that use their entire time slice are demoted to lower priority queues
    - Periodic boosting prevents starvation of lower-priority processes
    """
    
    def __init__(self, num_queues=3, base_quantum=4, boost_interval=50):
        """
        Initialize the MLFQ scheduler.
        
        Args:
            num_queues (int): Number of priority queues
            base_quantum (int): Base time quantum for the highest priority queue
            boost_interval (int): Time interval between priority boosts
        """
        super().__init__(name="Multi-Level Feedback Queue")
        self.num_queues = num_queues
        self.queues = [[] for _ in range(num_queues)]
        self.quantum_for_queue = [base_quantum * (2**i) for i in range(num_queues)]
        self.boost_interval = boost_interval
        self.time_since_last_boost = 0
        
        # Track which queue each process belongs to
        self.process_queue_map = {}  # pid -> queue_level
        
    def reset(self):
        """Reset the scheduler to its initial state."""
        super().reset()
        self.queues = [[] for _ in range(self.num_queues)]
        self.process_queue_map = {}
        self.time_since_last_boost = 0
        
    def add_to_ready_queue(self, process):
        """
        Add a process to the appropriate queue.
        
        New processes always enter the highest priority queue.
        
        Args:
            process (Process): The process to add to the queue
        """
        # Add to the main ready queue for tracking
        self.ready_queue.append(process)
        
        # New processes go to the highest priority queue (queue 0)
        if process.pid not in self.process_queue_map:
            queue_level = 0
            self.process_queue_map[process.pid] = queue_level
        else:
            queue_level = self.process_queue_map[process.pid]
            
        self.queues[queue_level].append(process)
        
    def schedule(self):
        """
        Select the next process to run based on MLFQ policy.
        
        Returns:
            Process: The next process to run, or None if all queues are empty
        """
        # Check for priority boost
        if self.time_since_last_boost >= self.boost_interval:
            self._boost_priorities()
            
        # Find the first non-empty queue (highest priority first)
        for queue_level in range(self.num_queues):
            if self.queues[queue_level]:
                # Return the first process in this queue (FIFO within each queue)
                return self.queues[queue_level][0]
                
        return None
        
    def _boost_priorities(self):
        """
        Boost all processes to the highest priority queue to prevent starvation.
        """
        # Reset all processes to the highest priority queue
        for queue_level in range(1, self.num_queues):
            while self.queues[queue_level]:
                process = self.queues[queue_level].pop(0)
                self.process_queue_map[process.pid] = 0
                self.queues[0].append(process)
                
        self.time_since_last_boost = 0
        
    def demote_process(self, process):
        """
        Demote a process to a lower priority queue.
        
        Args:
            process (Process): Process to demote
            
        Returns:
            bool: True if the process was demoted, False if already at lowest priority
        """
        current_level = self.process_queue_map[process.pid]
        
        # If already at lowest priority, can't demote further
        if current_level >= self.num_queues - 1:
            return False
            
        # Demote to next lower queue
        new_level = current_level + 1
        self.process_queue_map[process.pid] = new_level
        
        return True
        
    def execute_process(self, process, debug=False):
        """
        Execute the process according to MLFQ rules.
        
        Args:
            process (Process): The process to execute
            debug (bool): Whether to print debug information
        """
        queue_level = self.process_queue_map[process.pid]
        quantum = self.quantum_for_queue[queue_level]
        
        # Remove from the current queue
        self.queues[queue_level].remove(process)
        self.ready_queue.remove(process)
        
        # Track time used by this process in its current time slice
        start_remaining = process.remaining_time
        
        # Execute for quantum or until completion
        execution_time = process.execute(quantum, current_time=self.time)
        
        # Update time since last boost
        self.time_since_last_boost += execution_time
        
        if debug:
            queue_info = f"[Q{queue_level}, quantum={quantum}ms]"
            if process.remaining_time > 0:
                print(f"Executing {process.name} {queue_info} for {execution_time}ms "
                      f"(preempted, {process.remaining_time}ms remaining)")
            else:
                print(f"Executing {process.name} {queue_info} for {execution_time}ms "
                      f"(completed)")
                
        # Update simulation time
        self.tick(execution_time)
        
        # If the process is not finished, determine its next queue
        if process.state != ProcessState.TERMINATED:
            # If process used its entire quantum, demote it
            time_used = start_remaining - process.remaining_time
            if time_used >= quantum:
                self.demote_process(process)
                
            # Add back to the appropriate queue
            self.add_to_ready_queue(process) 