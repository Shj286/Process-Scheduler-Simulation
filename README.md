# Process Scheduler Simulation

This project simulates different process scheduling algorithms to understand how they affect system performance. Instead of modifying the actual Linux kernel, this simulator allows you to experiment with different scheduling algorithms and analyze their performance characteristics.

## Scheduling Algorithms Implemented

The following scheduling algorithms are implemented in this simulation:

### 1. First Come First Served (FCFS)
- Non-preemptive scheduling algorithm
- Processes are executed in the order they arrive
- Simple, but can lead to the "convoy effect" where short processes wait behind long ones

### 2. Round Robin (RR)
- Preemptive scheduling algorithm
- Each process is given a fixed time slice (quantum)
- When time slice expires, the process is preempted and moved to the back of the ready queue
- Good for time-sharing systems and ensuring fairness

### 3. Round Robin with Priority
- Combines Round Robin with priority scheduling
- Processes with higher priority are scheduled first
- Within the same priority level, Round Robin is used
- Balances importance (priority) with fairness

### 4. Shortest Job Next (SJN)
- Non-preemptive scheduling algorithm
- Chooses the process with the shortest burst time to execute next
- Optimal for minimizing average waiting time
- Requires knowledge of burst times in advance

### 5. Shortest Remaining Time First (SRTF)
- Preemptive version of SJN
- Preempts the current process if a new process arrives with a shorter remaining time
- Optimal for minimizing average turnaround time
- Higher overhead due to frequent context switches

### 6. Multi-Level Feedback Queue (MLFQ)
- Advanced scheduling algorithm used in many real operating systems
- Uses multiple priority queues with different time quanta
- New processes start in the highest priority queue
- Processes are demoted to lower queues if they use their entire time quantum
- Periodic boosting prevents starvation of long-running processes

## Project Structure

```
Process-Scheduler-Simulation/
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── scheduler/              # Core scheduler implementation
│   ├── __init__.py
│   ├── process.py          # Process class definition
│   ├── scheduler.py        # Base scheduler class
│   └── algorithms/         # Implementation of scheduling algorithms
│       ├── __init__.py
│       ├── fcfs.py         # First Come First Served
│       ├── rr.py           # Round Robin
│       ├── rr_priority.py  # Round Robin with Priority
│       ├── sjn.py          # Shortest Job Next and SRTF
│       └── mlfq.py         # Multi-Level Feedback Queue
├── simulation.py           # Main simulation runner
└── analysis/               # Performance analysis tools
    ├── __init__.py
    └── metrics.py          # Performance metrics calculator
```

## Setup

1. Ensure you have Python 3.7+ installed
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Simulation

Run a basic simulation with the default settings:
```
python simulation.py
```

This will simulate all scheduling algorithms with a small set of processes and show a comparison of their performance.

### Specific Algorithm

To run a specific scheduling algorithm:
```
python simulation.py --algorithm rr_priority
```

Available options: `fcfs`, `rr`, `rr_priority`, `sjn`, `srtf`, `mlfq`

### Random vs. Controlled Processes

By default, the simulation creates a small set of predefined processes for consistent comparison. To use random processes:
```
python simulation.py --processes 10 --seed 42
```

To use the predefined controlled set of processes:
```
python simulation.py --controlled
```

### Debug Mode

To see detailed execution steps:
```
python simulation.py --debug
```

### Performance Reports

To generate detailed performance reports and charts:
```
python simulation.py --algorithm all --report
```

Charts will be saved to the `results/` directory (configurable with `--output-dir`).

## Performance Metrics

The simulation calculates and reports the following performance metrics:

1. **Turnaround Time**: Time from process submission to completion
2. **Waiting Time**: Time spent waiting in the ready queue
3. **Response Time**: Time from submission to first execution
4. **Throughput**: Number of processes completed per unit time
5. **CPU Utilization**: Percentage of time the CPU is busy
6. **Context Switches**: Number of times the CPU switches between processes

## Benchmarking

The project includes a comprehensive benchmarking system to compare scheduling algorithms across different workload patterns:

```
python benchmark.py
```

This will run all scheduling algorithms against the following workload patterns:

1. **IO-Bound Workload**: Mostly short processes with a few long ones
2. **CPU-Bound Workload**: Mostly long-running processes with a few short ones
3. **Mixed Workload**: A balanced mix of short and long processes
4. **Arrival-Burst Correlation**: Early arrivals have long bursts, late arrivals have short bursts
5. **Priority Test**: High priority processes arrive after low priority ones

The benchmark script generates detailed performance metrics and graphs for each workload pattern, as well as cross-benchmark comparisons. Results are saved to the `benchmark_results/` directory by default.

```
python benchmark.py --output-dir my_benchmark_results
```

### Benchmark Output

For each benchmark and metric, the script generates:
- Individual algorithm performance charts
- Side-by-side algorithm comparisons for each workload
- Cross-workload comparison charts for each metric

This helps visualize which algorithms perform best for specific types of workloads.

## Learning Outcomes

Working with this simulation helps you understand:

- The strengths and weaknesses of different scheduling algorithms
- How scheduling decisions affect system performance
- Trade-offs between response time, throughput, and fairness
- The impact of process characteristics on scheduler performance
- How modern operating systems handle process scheduling

## Extending the Simulation

The modular design of this project makes it easy to extend:

1. To add a new scheduling algorithm, create a new class that inherits from `Scheduler`
2. Implement the required methods: `schedule()`, `add_to_ready_queue()`, and `execute_process()`
3. Update the imports in `scheduler/algorithms/__init__.py`
4. Add the new algorithm to the `run_all_schedulers()` function in `simulation.py`
5. Add it to the command-line options in `main()`

## License

This project is open source and available under the MIT License.