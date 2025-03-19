"""
Performance metrics calculation and visualization for process scheduling algorithms.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate
from colorama import Fore, Style


class PerformanceAnalyzer:
    """
    Analyzes and visualizes scheduling algorithm performance.
    """
    
    def __init__(self):
        """Initialize the performance analyzer."""
        self.results = {}
        
    def add_result(self, scheduler_name, stats):
        """
        Add a simulation result for analysis.
        
        Args:
            scheduler_name (str): Name of the scheduler algorithm
            stats (dict): Statistics generated by the scheduler's run
        """
        self.results[scheduler_name] = stats
        
    def print_summary(self):
        """Print a summary of all scheduler results for comparison."""
        if not self.results:
            print("No results to analyze.")
            return
            
        # Collect data for comparison
        data = []
        headers = ["Scheduler", "Avg. Turnaround", "Avg. Waiting", 
                  "Avg. Response", "Throughput", "CPU Utilization", 
                  "Context Switches"]
        
        for name, stats in self.results.items():
            row = [
                name,
                f"{stats['avg_turnaround_time']:.2f}ms",
                f"{stats['avg_waiting_time']:.2f}ms",
                f"{stats['avg_response_time']:.2f}ms",
                f"{stats['throughput']:.2f} proc/ms",
                f"{stats['cpu_utilization']*100:.2f}%",
                stats['total_context_switches']
            ]
            data.append(row)
            
        print("\n" + Fore.CYAN + "=" * 80)
        print("SCHEDULER PERFORMANCE COMPARISON")
        print("=" * 80 + Style.RESET_ALL)
        print(tabulate(data, headers=headers, tablefmt="grid"))
        
    def print_detailed_results(self, scheduler_name):
        """
        Print detailed results for a specific scheduler.
        
        Args:
            scheduler_name (str): Name of the scheduler to analyze
        """
        if scheduler_name not in self.results:
            print(f"No results found for scheduler: {scheduler_name}")
            return
            
        stats = self.results[scheduler_name]
        process_metrics = stats['processes']
        
        print("\n" + Fore.GREEN + "=" * 80)
        print(f"DETAILED RESULTS FOR {scheduler_name.upper()}")
        print("=" * 80 + Style.RESET_ALL)
        
        # Print overall statistics
        print(f"\nTotal Processes: {stats['total_processes']}")
        print(f"Completed Processes: {stats['completed_processes']}")
        print(f"Total Execution Time: {stats['total_execution_time']:.2f}ms")
        print(f"CPU Utilization: {stats['cpu_utilization']*100:.2f}%")
        print(f"Average Turnaround Time: {stats['avg_turnaround_time']:.2f}ms")
        print(f"Average Waiting Time: {stats['avg_waiting_time']:.2f}ms")
        print(f"Average Response Time: {stats['avg_response_time']:.2f}ms")
        print(f"Throughput: {stats['throughput']:.4f} processes/ms")
        print(f"Total Context Switches: {stats['total_context_switches']}")
        
        # Print per-process metrics
        print("\nPER-PROCESS METRICS:")
        
        # Create a DataFrame for better display
        df = pd.DataFrame(process_metrics)
        # Convert time fields to milliseconds with 2 decimal places
        for field in ['waiting_time', 'turnaround_time', 'response_time']:
            if field in df.columns:
                df[field] = df[field].apply(lambda x: f"{x:.2f}ms" if x is not None else "N/A")
                
        print(tabulate(df, headers='keys', tablefmt='grid'))
        
    def plot_comparison(self, metric='avg_waiting_time', title=None, file_path=None):
        """
        Plot a comparison of schedulers based on a specific metric.
        
        Args:
            metric (str): The metric to compare ('avg_waiting_time', 'avg_turnaround_time', etc.)
            title (str, optional): Plot title
            file_path (str, optional): File path to save the plot
        """
        if not self.results:
            print("No results to plot.")
            return
            
        # Extract the metric values for each scheduler
        names = []
        values = []
        
        for name, stats in self.results.items():
            if metric in stats:
                names.append(name)
                values.append(stats[metric])
                
        if not names:
            print(f"Metric '{metric}' not found in results.")
            return
            
        # Create the bar chart
        plt.figure(figsize=(10, 6))
        bars = plt.bar(names, values, color='skyblue')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom')
        
        # Add labels and title
        metric_name = metric.replace('_', ' ').title()
        plt.ylabel(metric_name)
        plt.xlabel('Scheduling Algorithm')
        
        if title:
            plt.title(title)
        else:
            plt.title(f'Comparison of {metric_name} Across Schedulers')
            
        plt.xticks(rotation=30)
        plt.tight_layout()
        
        if file_path:
            plt.savefig(file_path)
            
        plt.show()
        
    def plot_all_metrics(self, directory=None):
        """
        Plot comparisons for all key metrics.
        
        Args:
            directory (str, optional): Directory to save the plots
        """
        # Define the metrics to plot
        metrics = [
            ('avg_waiting_time', 'Average Waiting Time (ms)'),
            ('avg_turnaround_time', 'Average Turnaround Time (ms)'),
            ('avg_response_time', 'Average Response Time (ms)'),
            ('throughput', 'Throughput (processes/ms)'),
            ('cpu_utilization', 'CPU Utilization'),
            ('total_context_switches', 'Context Switches')
        ]
        
        for metric, title in metrics:
            file_path = None
            if directory:
                file_path = f"{directory}/{metric}_comparison.png"
                
            self.plot_comparison(metric, title, file_path)
            
    def plot_gantt_chart(self, scheduler_name, file_path=None):
        """
        Create a Gantt chart showing the execution timeline.
        
        This is a simple visualization and would need process execution history data
        that's not fully implemented in the current simulation.
        
        Args:
            scheduler_name (str): Name of the scheduler to visualize
            file_path (str, optional): File path to save the plot
        """
        if scheduler_name not in self.results:
            print(f"No results found for scheduler: {scheduler_name}")
            return
            
        stats = self.results[scheduler_name]
        process_metrics = stats['processes']
        
        # Note: This is a simplified Gantt chart and would need more detailed
        # execution timing data for a complete representation
        plt.figure(figsize=(12, 6))
        
        # Sort processes by arrival time for better visualization
        sorted_processes = sorted(process_metrics, key=lambda p: p['pid'])
        
        for i, p in enumerate(sorted_processes):
            plt.barh(i, p['burst_time'], left=p['waiting_time'], color='skyblue')
            plt.text(p['waiting_time'] + p['burst_time']/2, i, 
                    f"P{p['pid']}", ha='center', va='center')
            
        plt.xlabel('Time (ms)')
        plt.yticks(range(len(sorted_processes)), [f"Process {p['pid']}" for p in sorted_processes])
        plt.title(f'Simplified Process Timeline for {scheduler_name}')
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        if file_path:
            plt.savefig(file_path)
            
        plt.show() 