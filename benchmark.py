#!/usr/bin/env python3
"""
Process Scheduler Benchmark Script

This script runs predefined benchmarks to compare the performance
of different scheduling algorithms under various workload patterns.
"""
import time
import os
import numpy as np
import matplotlib.pyplot as plt
from colorama import init, Fore, Style
import argparse

from scheduler.process import Process
from scheduler.algorithms import (
    FCFSScheduler,
    RRScheduler,
    RRPriorityScheduler,
    SJNScheduler, 
    SRTFScheduler,
    MLFQScheduler
)
from analysis.metrics import PerformanceAnalyzer


def create_benchmark_io_bound():
    """
    Create a benchmark with mostly short, IO-bound processes.
    
    Returns:
        list: List of Process objects
    """
    processes = [
        Process(name="P1", arrival_time=0, burst_time=2, priority=3),   # Short
        Process(name="P2", arrival_time=1, burst_time=1, priority=5),   # Very short
        Process(name="P3", arrival_time=2, burst_time=3, priority=2),   # Short
        Process(name="P4", arrival_time=3, burst_time=1, priority=4),   # Very short
        Process(name="P5", arrival_time=4, burst_time=2, priority=1),   # Short
        Process(name="P6", arrival_time=5, burst_time=15, priority=3),  # One long process
        Process(name="P7", arrival_time=6, burst_time=1, priority=5),   # Very short
        Process(name="P8", arrival_time=7, burst_time=2, priority=4),   # Short
        Process(name="P9", arrival_time=8, burst_time=3, priority=2),   # Short
        Process(name="P10", arrival_time=9, burst_time=1, priority=1),  # Very short
    ]
    return processes


def create_benchmark_cpu_bound():
    """
    Create a benchmark with mostly long, CPU-bound processes.
    
    Returns:
        list: List of Process objects
    """
    processes = [
        Process(name="P1", arrival_time=0, burst_time=10, priority=3),  # Long
        Process(name="P2", arrival_time=2, burst_time=15, priority=5),  # Very long
        Process(name="P3", arrival_time=4, burst_time=8, priority=2),   # Medium
        Process(name="P4", arrival_time=6, burst_time=20, priority=4),  # Very long
        Process(name="P5", arrival_time=8, burst_time=3, priority=1),   # Short (exception)
        Process(name="P6", arrival_time=10, burst_time=12, priority=3), # Long
        Process(name="P7", arrival_time=12, burst_time=2, priority=5),  # Short (exception)
        Process(name="P8", arrival_time=14, burst_time=18, priority=4), # Very long
        Process(name="P9", arrival_time=16, burst_time=9, priority=2),  # Medium
        Process(name="P10", arrival_time=18, burst_time=14, priority=1), # Long
    ]
    return processes


def create_benchmark_mixed():
    """
    Create a benchmark with a mix of processes.
    
    Returns:
        list: List of Process objects
    """
    processes = [
        Process(name="P1", arrival_time=0, burst_time=8, priority=3),   # Medium
        Process(name="P2", arrival_time=1, burst_time=2, priority=5),   # Short
        Process(name="P3", arrival_time=3, burst_time=15, priority=2),  # Long
        Process(name="P4", arrival_time=5, burst_time=3, priority=4),   # Short
        Process(name="P5", arrival_time=6, burst_time=10, priority=1),  # Medium
        Process(name="P6", arrival_time=8, burst_time=1, priority=3),   # Very short
        Process(name="P7", arrival_time=9, burst_time=12, priority=5),  # Long
        Process(name="P8", arrival_time=10, burst_time=5, priority=4),  # Medium
        Process(name="P9", arrival_time=12, burst_time=4, priority=2),  # Short
        Process(name="P10", arrival_time=14, burst_time=20, priority=1), # Very long
    ]
    return processes


def create_benchmark_arrival_burst():
    """
    Create a benchmark where burst time correlates with arrival time.
    Early arrivals have long bursts, late arrivals have short bursts.
    
    Returns:
        list: List of Process objects
    """
    processes = [
        Process(name="P1", arrival_time=0, burst_time=20, priority=3),  # Early, long
        Process(name="P2", arrival_time=2, burst_time=18, priority=5),  # Early, long
        Process(name="P3", arrival_time=4, burst_time=16, priority=2),  # Early, long
        Process(name="P4", arrival_time=6, burst_time=14, priority=4),  # Mid, medium
        Process(name="P5", arrival_time=8, burst_time=12, priority=1),  # Mid, medium
        Process(name="P6", arrival_time=10, burst_time=10, priority=3), # Mid, medium
        Process(name="P7", arrival_time=12, burst_time=8, priority=5),  # Late, short
        Process(name="P8", arrival_time=14, burst_time=6, priority=4),  # Late, short
        Process(name="P9", arrival_time=16, burst_time=4, priority=2),  # Late, short
        Process(name="P10", arrival_time=18, burst_time=2, priority=1), # Late, short
    ]
    return processes


def create_benchmark_priority():
    """
    Create a benchmark to test priority handling.
    High priority processes arrive after low priority ones.
    
    Returns:
        list: List of Process objects
    """
    processes = [
        Process(name="P1", arrival_time=0, burst_time=10, priority=1),  # Low priority
        Process(name="P2", arrival_time=2, burst_time=8, priority=2),   # Low priority
        Process(name="P3", arrival_time=4, burst_time=6, priority=1),   # Low priority
        Process(name="P4", arrival_time=6, burst_time=10, priority=3),  # Medium priority
        Process(name="P5", arrival_time=8, burst_time=8, priority=3),   # Medium priority
        Process(name="P6", arrival_time=10, burst_time=6, priority=2),  # Low priority
        Process(name="P7", arrival_time=12, burst_time=10, priority=5), # High priority
        Process(name="P8", arrival_time=14, burst_time=8, priority=5),  # High priority
        Process(name="P9", arrival_time=16, burst_time=6, priority=4),  # High priority
        Process(name="P10", arrival_time=18, burst_time=4, priority=4), # High priority
    ]
    return processes


def run_benchmark(benchmark_name, process_creator, output_dir):
    """
    Run all schedulers on a benchmark and generate comparison metrics.
    
    Args:
        benchmark_name (str): Name of the benchmark
        process_creator (function): Function that creates the processes
        output_dir (str): Directory to save results
        
    Returns:
        dict: Dictionary with results by scheduler
    """
    processes = process_creator()
    
    print(f"\n{Fore.CYAN}====== BENCHMARK: {benchmark_name} ======{Style.RESET_ALL}")
    print(f"\nProcesses in this benchmark:")
    for p in processes:
        print(f"  {p.name}: arrival={p.arrival_time}ms, burst={p.burst_time}ms, priority={p.priority}")
        
    # Create all schedulers
    schedulers = [
        FCFSScheduler(),
        RRScheduler(time_quantum=2),
        RRPriorityScheduler(time_quantum=2),
        SJNScheduler(),
        SRTFScheduler(),
        MLFQScheduler(num_queues=3, base_quantum=2, boost_interval=50)
    ]
    
    # Create analyzer for this benchmark
    analyzer = PerformanceAnalyzer()
    
    # Run each scheduler
    for scheduler in schedulers:
        print(f"\n{Fore.YELLOW}Running {scheduler.name}...{Style.RESET_ALL}")
        
        # Create a copy of the processes for this scheduler
        process_copies = []
        for p in processes:
            process_copies.append(Process(
                name=p.name,
                arrival_time=p.arrival_time,
                burst_time=p.burst_time,
                priority=p.priority
            ))
            
        scheduler.add_processes(process_copies)
        
        # Run the simulation
        start_time = time.time()
        stats = scheduler.run(debug=False)
        elapsed = time.time() - start_time
        
        print(f"Simulation completed in {elapsed:.4f} seconds.")
        analyzer.add_result(scheduler.name, stats)
    
    # Print summary results
    analyzer.print_summary()
    
    # Generate detailed reports and plots
    benchmark_dir = os.path.join(output_dir, benchmark_name.lower().replace(' ', '_'))
    if not os.path.exists(benchmark_dir):
        os.makedirs(benchmark_dir)
        
    # Save plots for this benchmark
    analyzer.plot_all_metrics(directory=benchmark_dir)
    
    return analyzer.results


def plot_benchmark_comparison(benchmark_results, output_dir):
    """
    Create comparison plots across all benchmarks.
    
    Args:
        benchmark_results (dict): Dictionary with results from all benchmarks
        output_dir (str): Directory to save the comparison plots
    """
    metrics = {
        'avg_waiting_time': 'Average Waiting Time (ms)',
        'avg_turnaround_time': 'Average Turnaround Time (ms)',
        'avg_response_time': 'Average Response Time (ms)',
        'throughput': 'Throughput (processes/ms)',
        'cpu_utilization': 'CPU Utilization (%)'
    }
    
    schedulers = [
        'First Come First Served',
        'Round Robin',
        'Round Robin with Priority',
        'Shortest Job Next',
        'Shortest Remaining Time First',
        'Multi-Level Feedback Queue'
    ]
    
    # Create comparison directory
    comparison_dir = os.path.join(output_dir, 'comparison')
    if not os.path.exists(comparison_dir):
        os.makedirs(comparison_dir)
    
    # For each metric, create a grouped bar chart comparing all benchmarks
    for metric_key, metric_name in metrics.items():
        plt.figure(figsize=(14, 8))
        
        # Set up bar positions
        num_benchmarks = len(benchmark_results)
        bar_width = 0.12
        index = np.arange(len(schedulers))
        
        # Plot each benchmark as a group of bars
        for i, (benchmark_name, results) in enumerate(benchmark_results.items()):
            values = []
            for scheduler in schedulers:
                if scheduler in results and metric_key in results[scheduler]:
                    if metric_key == 'cpu_utilization':
                        # Convert to percentage for better readability
                        values.append(results[scheduler][metric_key] * 100)
                    else:
                        values.append(results[scheduler][metric_key])
                else:
                    values.append(0)
            
            # Create offset for this benchmark's group of bars
            offset = i - num_benchmarks/2 + 0.5
            
            # Plot the bars for this benchmark
            plt.bar(index + offset * bar_width, values, bar_width,
                   label=benchmark_name)
        
        # Labels and title
        plt.xlabel('Scheduling Algorithm')
        plt.ylabel(metric_name)
        plt.title(f'Comparison of {metric_name} Across Different Workloads')
        plt.xticks(index, [s.split()[-1] for s in schedulers], rotation=30)
        plt.legend(loc='best')
        plt.tight_layout()
        
        # Save plot
        plt.savefig(os.path.join(comparison_dir, f'{metric_key}_comparison.png'))
        plt.close()
    
    print(f"\n{Fore.GREEN}Cross-benchmark comparison charts saved to {comparison_dir}{Style.RESET_ALL}")


def main():
    """Run all benchmarks and generate comparison metrics."""
    init()  # Initialize colorama
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process Scheduler Benchmarks")
    parser.add_argument("--output-dir", type=str, default="benchmark_results",
                       help="Directory to save benchmark results")
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Define benchmarks to run
    benchmarks = {
        "IO-Bound Workload": create_benchmark_io_bound,
        "CPU-Bound Workload": create_benchmark_cpu_bound,
        "Mixed Workload": create_benchmark_mixed,
        "Arrival-Burst Correlation": create_benchmark_arrival_burst,
        "Priority Test": create_benchmark_priority
    }
    
    # Run all benchmarks
    benchmark_results = {}
    for name, creator in benchmarks.items():
        benchmark_results[name] = run_benchmark(name, creator, args.output_dir)
        
    # Generate cross-benchmark comparison plots
    plot_benchmark_comparison(benchmark_results, args.output_dir)
    
    print(f"\n{Fore.GREEN}All benchmarks completed. Results saved to {args.output_dir}{Style.RESET_ALL}")


if __name__ == "__main__":
    main() 