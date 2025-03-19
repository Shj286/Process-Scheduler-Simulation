#!/usr/bin/env python3
"""
Process Scheduler Simulation - Main Simulation Script

This script simulates different process scheduling algorithms and compares
their performance using various metrics.
"""
import argparse
import time
import random
import os
from colorama import init, Fore, Style

from scheduler.process import Process
from scheduler.algorithms.fcfs import FCFSScheduler
from scheduler.algorithms.rr import RRScheduler
from scheduler.algorithms.rr_priority import RRPriorityScheduler
from scheduler.algorithms.sjn import SJNScheduler, SRTFScheduler
from scheduler.algorithms.mlfq import MLFQScheduler
from analysis.metrics import PerformanceAnalyzer


def create_random_processes(n=10, seed=None, max_arrival=20, max_burst=20, max_priority=10):
    """
    Create a list of random processes for simulation.
    
    Args:
        n (int): Number of processes to create
        seed (int, optional): Random seed for reproducibility
        max_arrival (int): Maximum arrival time
        max_burst (int): Maximum burst time
        max_priority (int): Maximum priority
        
    Returns:
        list: List of Process objects
    """
    if seed is not None:
        random.seed(seed)
        
    processes = []
    for i in range(n):
        arrival = random.randint(0, max_arrival)
        burst = random.randint(1, max_burst)
        priority = random.randint(1, max_priority)
        
        processes.append(Process(
            name=f"P{i+1}",
            arrival_time=arrival,
            burst_time=burst,
            priority=priority
        ))
    
    return processes


def create_controlled_processes():
    """
    Create a list of processes with specific characteristics for demonstration.
    
    Returns:
        list: List of Process objects
    """
    return [
        Process(name="P1", arrival_time=0, burst_time=10, priority=3),
        Process(name="P2", arrival_time=2, burst_time=6, priority=5),
        Process(name="P3", arrival_time=4, burst_time=12, priority=1),
        Process(name="P4", arrival_time=6, burst_time=4, priority=4),
        Process(name="P5", arrival_time=8, burst_time=8, priority=2)
    ]


def run_all_schedulers(processes, debug=False):
    """
    Run all scheduling algorithms on the given processes.
    
    Args:
        processes (list): List of Process objects
        debug (bool): Whether to print debug information
        
    Returns:
        PerformanceAnalyzer: An analyzer with results from all schedulers
    """
    analyzer = PerformanceAnalyzer()
    
    # Define schedulers to run
    schedulers = [
        FCFSScheduler(),
        RRScheduler(time_quantum=2),
        RRPriorityScheduler(time_quantum=2),
        SJNScheduler(),
        SRTFScheduler(),
        MLFQScheduler(num_queues=3, base_quantum=2, boost_interval=50)
    ]
    
    # Run each scheduler
    for scheduler in schedulers:
        print(f"\n{Fore.YELLOW}Running {scheduler.name} scheduler...{Style.RESET_ALL}")
        
        # Add a copy of the processes to the scheduler
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
        stats = scheduler.run(debug=debug)
        elapsed = time.time() - start_time
        
        print(f"Simulation completed in {elapsed:.4f} seconds.")
        
        # Add results to analyzer
        analyzer.add_result(scheduler.name, stats)
    
    return analyzer


def main():
    """Main function to run the simulation."""
    init()  # Initialize colorama
    
    # Set up command-line arguments
    parser = argparse.ArgumentParser(description="Process Scheduler Simulation")
    parser.add_argument("--algorithm", type=str, default="all",
                       choices=["all", "fcfs", "rr", "rr_priority", "sjn", "srtf", "mlfq"],
                       help="Scheduling algorithm to run")
    parser.add_argument("--processes", type=int, default=5,
                       help="Number of random processes to create")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed for reproducibility")
    parser.add_argument("--controlled", action="store_true",
                       help="Use a controlled set of processes instead of random ones")
    parser.add_argument("--debug", action="store_true",
                       help="Print debug information")
    parser.add_argument("--report", action="store_true",
                       help="Generate performance reports and charts")
    parser.add_argument("--output-dir", type=str, default="results",
                       help="Directory to save results in")
    
    args = parser.parse_args()
    
    # Create processes
    if args.controlled:
        processes = create_controlled_processes()
        print(f"\n{Fore.CYAN}Using controlled set of {len(processes)} processes.{Style.RESET_ALL}")
    else:
        processes = create_random_processes(n=args.processes, seed=args.seed)
        print(f"\n{Fore.CYAN}Created {len(processes)} random processes (seed={args.seed}).{Style.RESET_ALL}")
    
    # Print process information
    print("\nProcess details:")
    for p in processes:
        print(f"  {p.name}: arrival={p.arrival_time}ms, burst={p.burst_time}ms, priority={p.priority}")
    
    # Run simulations
    if args.algorithm == "all":
        analyzer = run_all_schedulers(processes, debug=args.debug)
    else:
        # Run a specific scheduler
        analyzer = PerformanceAnalyzer()
        
        if args.algorithm == "fcfs":
            scheduler = FCFSScheduler()
        elif args.algorithm == "rr":
            scheduler = RRScheduler(time_quantum=2)
        elif args.algorithm == "rr_priority":
            scheduler = RRPriorityScheduler(time_quantum=2)
        elif args.algorithm == "sjn":
            scheduler = SJNScheduler()
        elif args.algorithm == "srtf":
            scheduler = SRTFScheduler()
        elif args.algorithm == "mlfq":
            scheduler = MLFQScheduler(num_queues=3, base_quantum=2, boost_interval=50)
        
        print(f"\n{Fore.YELLOW}Running {scheduler.name} scheduler...{Style.RESET_ALL}")
        scheduler.add_processes(processes)
        stats = scheduler.run(debug=args.debug)
        analyzer.add_result(scheduler.name, stats)
    
    # Print summary results
    analyzer.print_summary()
    
    # Generate detailed reports if requested
    if args.report:
        # Create output directory if needed
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
            
        print(f"\n{Fore.GREEN}Generating detailed performance reports...{Style.RESET_ALL}")
        
        # Print detailed results for each scheduler
        for name in analyzer.results.keys():
            analyzer.print_detailed_results(name)
            
        # Generate plots
        analyzer.plot_all_metrics(directory=args.output_dir)
        
        print(f"\nResults saved to {args.output_dir}/ directory.")


if __name__ == "__main__":
    main() 