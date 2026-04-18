"""
Business Agent 2.0 - Graph Generator
Generates various visualizations for system metrics and analytics
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
COLORS = {
    'agent': '#4A90E2',
    'mcp_client': '#7B68EE',
    'ingestion': '#50C878',
    'enrichment': '#FFB347',
    'task_mgmt': '#FF6B6B',
    'storage': '#9B59B6',
    'success': '#27AE60',
    'warning': '#F39C12',
    'error': '#E74C3C'
}


def create_output_dir():
    """Create output directory for graphs"""
    output_dir = Path("graphs_output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def generate_sample_data():
    """Generate sample data for visualizations"""
    np.random.seed(42)
    
    # Time series data for last 30 days
    dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
    
    data = {
        'dates': dates,
        'leads_processed': np.random.randint(10, 50, 30),
        'leads_qualified': np.random.randint(3, 20, 30),
        'tasks_created': np.random.randint(2, 15, 30),
        'emails_sent': np.random.randint(1, 12, 30),
        
        # Data source distribution
        'data_sources': {
            'RSS Feeds': 450,
            'Reddit': 280,
            'Web Scraping': 320,
            'Twitter': 120
        },
        
        # Lead quality scores
        'lead_scores': np.random.normal(6.5, 1.5, 100),
        
        # Processing times (seconds)
        'processing_times': {
            'Retrieve': np.random.gamma(2, 1.5, 100),
            'Qualify': np.random.gamma(3, 1.2, 100),
            'Enrich': np.random.gamma(4, 2, 100),
            'Draft Email': np.random.gamma(2.5, 1, 100),
            'Create Task': np.random.gamma(2, 0.8, 100)
        },
        
        # Success rates
        'success_rates': {
            'Data Ingestion': 98.5,
            'Lead Qualification': 94.2,
            'Email Enrichment': 87.3,
            'Task Creation': 99.1,
            'Overall Pipeline': 85.7
        },
        
        # MCP Server statistics
        'mcp_stats': {
            'Ingestion Server': {'calls': 1250, 'avg_time': 2.3, 'errors': 12},
            'Enrichment Server': {'calls': 890, 'avg_time': 3.8, 'errors': 45},
            'Task Management Server': {'calls': 670, 'avg_time': 1.9, 'errors': 8}
        },
        
        # API usage
        'api_usage': {
            'Hunter.io': 450,
            'Clearbit': 230,
            'Trello': 380,
            'Notion': 145,
            'Discord': 290
        }
    }
    
    return data


def plot_lead_processing_trends(data, output_dir):
    """Generate lead processing trends over time"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Lead Processing Trends (Last 30 Days)', fontsize=16, fontweight='bold')
    
    dates = data['dates']
    
    # Plot 1: Leads Processed vs Qualified
    ax1 = axes[0, 0]
    ax1.plot(dates, data['leads_processed'], marker='o', linewidth=2, 
             label='Processed', color=COLORS['agent'])
    ax1.plot(dates, data['leads_qualified'], marker='s', linewidth=2, 
             label='Qualified (Score >7)', color=COLORS['success'])
    ax1.fill_between(dates, data['leads_qualified'], alpha=0.3, color=COLORS['success'])
    ax1.set_title('Leads Processed vs Qualified', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Count')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Plot 2: Conversion Rate
    ax2 = axes[0, 1]
    conversion_rate = (data['leads_qualified'] / data['leads_processed']) * 100
    ax2.plot(dates, conversion_rate, marker='D', linewidth=2.5, 
             color=COLORS['enrichment'], label='Conversion Rate')
    ax2.axhline(y=conversion_rate.mean(), color='red', linestyle='--', 
                label=f'Average: {conversion_rate.mean():.1f}%')
    ax2.set_title('Lead Qualification Rate', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Conversion Rate (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Plot 3: Tasks Created
    ax3 = axes[1, 0]
    ax3.bar(dates, data['tasks_created'], color=COLORS['task_mgmt'], alpha=0.7, label='Tasks')
    ax3.set_title('Tasks Created Daily', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Tasks Created')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Plot 4: Emails Sent
    ax4 = axes[1, 1]
    ax4.bar(dates, data['emails_sent'], color=COLORS['mcp_client'], alpha=0.7, label='Emails')
    ax4.set_title('Outreach Emails Sent', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Date')
    ax4.set_ylabel('Emails Sent')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'lead_processing_trends.png', dpi=300, bbox_inches='tight')
    print(f"✅ Generated: lead_processing_trends.png")
    plt.close()


def plot_data_source_distribution(data, output_dir):
    """Generate data source distribution pie chart"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Data Source Analytics', fontsize=16, fontweight='bold')
    
    sources = list(data['data_sources'].keys())
    counts = list(data['data_sources'].values())
    colors = [COLORS['ingestion'], COLORS['enrichment'], COLORS['task_mgmt'], COLORS['warning']]
    
    # Pie chart
    wedges, texts, autotexts = ax1.pie(counts, labels=sources, autopct='%1.1f%%',
                                         colors=colors, startangle=90,
                                         textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax1.set_title('Document Sources Distribution', fontsize=12, fontweight='bold', pad=20)
    
    # Bar chart
    bars = ax2.barh(sources, counts, color=colors, alpha=0.8)
    ax2.set_title('Documents by Source', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Number of Documents')
    ax2.grid(True, alpha=0.3, axis='x')
    
    # Add value labels on bars
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax2.text(count + 10, i, str(count), va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'data_source_distribution.png', dpi=300, bbox_inches='tight')
    print(f"✅ Generated: data_source_distribution.png")
    plt.close()


def plot_lead_quality_distribution(data, output_dir):
    """Generate lead quality score distribution"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Lead Quality Analysis', fontsize=16, fontweight='bold')
    
    scores = np.clip(data['lead_scores'], 1, 10)
    
    # Histogram
    n, bins, patches = ax1.hist(scores, bins=20, edgecolor='black', alpha=0.7)
    
    # Color code by quality threshold
    for i, patch in enumerate(patches):
        if bins[i] > 7:
            patch.set_facecolor(COLORS['success'])
        elif bins[i] > 5:
            patch.set_facecolor(COLORS['warning'])
        else:
            patch.set_facecolor(COLORS['error'])
    
    ax1.axvline(x=7, color='red', linestyle='--', linewidth=2, label='Qualification Threshold')
    ax1.set_title('Lead Score Distribution', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Lead Quality Score (1-10)')
    ax1.set_ylabel('Frequency')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Box plot
    bp = ax2.boxplot([scores], vert=True, patch_artist=True,
                      labels=['All Leads'],
                      boxprops=dict(facecolor=COLORS['agent'], alpha=0.7),
                      medianprops=dict(color='red', linewidth=2),
                      whiskerprops=dict(linewidth=1.5),
                      capprops=dict(linewidth=1.5))
    ax2.axhline(y=7, color='red', linestyle='--', linewidth=2, label='Threshold')
    ax2.set_title('Lead Score Statistics', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Lead Quality Score')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add statistics text
    stats_text = f"Mean: {scores.mean():.2f}\nMedian: {np.median(scores):.2f}\n"
    stats_text += f"Qualified: {(scores > 7).sum()}/{len(scores)} ({(scores > 7).sum()/len(scores)*100:.1f}%)"
    ax2.text(1.15, 5, stats_text, fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'lead_quality_distribution.png', dpi=300, bbox_inches='tight')
    print(f"✅ Generated: lead_quality_distribution.png")
    plt.close()


def plot_processing_times(data, output_dir):
    """Generate processing time analysis"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Workflow Processing Time Analysis', fontsize=16, fontweight='bold')
    
    stages = list(data['processing_times'].keys())
    times_data = [data['processing_times'][stage] for stage in stages]
    colors_list = [COLORS['ingestion'], COLORS['agent'], COLORS['enrichment'], 
                   COLORS['mcp_client'], COLORS['task_mgmt']]
    
    # Box plot
    bp = ax1.boxplot(times_data, labels=stages, patch_artist=True,
                      showmeans=True, meanline=True)
    
    for patch, color in zip(bp['boxes'], colors_list):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax1.set_title('Processing Time by Stage', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Time (seconds)')
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Average times bar chart
    avg_times = [np.mean(times) for times in times_data]
    bars = ax2.bar(range(len(stages)), avg_times, color=colors_list, alpha=0.8)
    ax2.set_xticks(range(len(stages)))
    ax2.set_xticklabels(stages, rotation=45, ha='right')
    ax2.set_title('Average Processing Time by Stage', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Average Time (seconds)')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, time in zip(bars, avg_times):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{time:.2f}s', ha='center', va='bottom', fontweight='bold')
    
    # Add total pipeline time
    total_time = sum(avg_times)
    ax2.text(0.5, 0.95, f'Total Pipeline: {total_time:.2f}s',
             transform=ax2.transAxes, ha='center', va='top',
             fontsize=11, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'processing_times.png', dpi=300, bbox_inches='tight')
    print(f"✅ Generated: processing_times.png")
    plt.close()


def plot_success_rates(data, output_dir):
    """Generate success rate dashboard"""
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.suptitle('System Success Rates', fontsize=16, fontweight='bold')
    
    components = list(data['success_rates'].keys())
    rates = list(data['success_rates'].values())
    
    # Create horizontal bar chart
    bars = ax.barh(components, rates, color=[
        COLORS['success'] if r >= 95 else COLORS['warning'] if r >= 90 else COLORS['error']
        for r in rates
    ], alpha=0.8)
    
    # Add percentage labels
    for i, (bar, rate) in enumerate(zip(bars, rates)):
        ax.text(rate + 1, i, f'{rate:.1f}%', va='center', fontweight='bold', fontsize=11)
    
    # Add threshold lines
    ax.axvline(x=95, color='green', linestyle='--', linewidth=1.5, alpha=0.5, label='Target: 95%')
    ax.axvline(x=90, color='orange', linestyle='--', linewidth=1.5, alpha=0.5, label='Warning: 90%')
    
    ax.set_xlim(0, 105)
    ax.set_xlabel('Success Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Component-wise Success Rates', fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'success_rates.png', dpi=300, bbox_inches='tight')
    print(f"✅ Generated: success_rates.png")
    plt.close()


def plot_mcp_server_stats(data, output_dir):
    """Generate MCP server statistics"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('MCP Server Performance Metrics', fontsize=16, fontweight='bold')
    
    servers = list(data['mcp_stats'].keys())
    calls = [data['mcp_stats'][s]['calls'] for s in servers]
    avg_times = [data['mcp_stats'][s]['avg_time'] for s in servers]
    errors = [data['mcp_stats'][s]['errors'] for s in servers]
    
    colors_list = [COLORS['ingestion'], COLORS['enrichment'], COLORS['task_mgmt']]
    
    # API Calls
    bars1 = axes[0].bar(servers, calls, color=colors_list, alpha=0.8)
    axes[0].set_title('Total API Calls', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Number of Calls')
    axes[0].grid(True, alpha=0.3, axis='y')
    plt.setp(axes[0].xaxis.get_majorticklabels(), rotation=45, ha='right')
    for bar, call in zip(bars1, calls):
        height = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2., height,
                    f'{call}', ha='center', va='bottom', fontweight='bold')
    
    # Average Response Time
    bars2 = axes[1].bar(servers, avg_times, color=colors_list, alpha=0.8)
    axes[1].set_title('Average Response Time', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Time (seconds)')
    axes[1].grid(True, alpha=0.3, axis='y')
    plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45, ha='right')
    for bar, time in zip(bars2, avg_times):
        height = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width()/2., height,
                    f'{time:.1f}s', ha='center', va='bottom', fontweight='bold')
    
    # Error Counts
    bars3 = axes[2].bar(servers, errors, color=colors_list, alpha=0.8)
    axes[2].set_title('Error Count', fontsize=12, fontweight='bold')
    axes[2].set_ylabel('Number of Errors')
    axes[2].grid(True, alpha=0.3, axis='y')
    plt.setp(axes[2].xaxis.get_majorticklabels(), rotation=45, ha='right')
    for bar, error in zip(bars3, errors):
        height = bar.get_height()
        axes[2].text(bar.get_x() + bar.get_width()/2., height,
                    f'{error}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'mcp_server_stats.png', dpi=300, bbox_inches='tight')
    print(f"✅ Generated: mcp_server_stats.png")
    plt.close()


def plot_api_usage(data, output_dir):
    """Generate API usage statistics"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('External API Usage Statistics', fontsize=16, fontweight='bold')
    
    apis = list(data['api_usage'].keys())
    usage = list(data['api_usage'].values())
    colors_list = [COLORS['enrichment'], COLORS['warning'], COLORS['task_mgmt'], 
                   COLORS['mcp_client'], COLORS['agent']]
    
    # Horizontal bar chart
    bars = ax1.barh(apis, usage, color=colors_list, alpha=0.8)
    ax1.set_title('API Call Distribution', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Number of Calls')
    ax1.grid(True, alpha=0.3, axis='x')
    
    for bar, count in zip(bars, usage):
        width = bar.get_width()
        ax1.text(width + 10, bar.get_y() + bar.get_height()/2.,
                f'{count}', ha='left', va='center', fontweight='bold')
    
    # Pie chart
    wedges, texts, autotexts = ax2.pie(usage, labels=apis, autopct='%1.1f%%',
                                         colors=colors_list, startangle=90,
                                         textprops={'fontsize': 10, 'fontweight': 'bold'})
    ax2.set_title('API Usage Share', fontsize=12, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'api_usage.png', dpi=300, bbox_inches='tight')
    print(f"✅ Generated: api_usage.png")
    plt.close()


def create_dashboard_summary(data, output_dir):
    """Create a comprehensive dashboard summary"""
    fig = plt.figure(figsize=(20, 12))
    fig.suptitle('Business Agent 2.0 - System Dashboard', fontsize=20, fontweight='bold')
    
    # Create grid
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Key Metrics (top-left)
    ax1 = fig.add_subplot(gs[0, 0])
    metrics = {
        'Total Leads': sum(data['leads_processed']),
        'Qualified': sum(data['leads_qualified']),
        'Tasks Created': sum(data['tasks_created']),
        'Success Rate': data['success_rates']['Overall Pipeline']
    }
    ax1.axis('off')
    y_pos = 0.9
    ax1.text(0.5, y_pos, 'KEY METRICS', ha='center', fontsize=14, fontweight='bold',
             transform=ax1.transAxes)
    y_pos -= 0.15
    for metric, value in metrics.items():
        if isinstance(value, float):
            text = f"{metric}: {value:.1f}%"
        else:
            text = f"{metric}: {value:,}"
        ax1.text(0.1, y_pos, text, fontsize=11, transform=ax1.transAxes,
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        y_pos -= 0.15
    
    # 2. Leads trend (top-middle and top-right)
    ax2 = fig.add_subplot(gs[0, 1:])
    ax2.plot(data['dates'][-14:], data['leads_processed'][-14:], 
             marker='o', label='Processed', linewidth=2, color=COLORS['agent'])
    ax2.plot(data['dates'][-14:], data['leads_qualified'][-14:], 
             marker='s', label='Qualified', linewidth=2, color=COLORS['success'])
    ax2.set_title('Recent Lead Activity (14 Days)', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 3. Data sources (middle-left)
    ax3 = fig.add_subplot(gs[1, 0])
    sources = list(data['data_sources'].keys())
    counts = list(data['data_sources'].values())
    colors = [COLORS['ingestion'], COLORS['enrichment'], COLORS['task_mgmt'], COLORS['warning']]
    ax3.pie(counts, labels=sources, autopct='%1.0f%%', colors=colors, startangle=90)
    ax3.set_title('Data Sources', fontweight='bold')
    
    # 4. Processing times (middle-center)
    ax4 = fig.add_subplot(gs[1, 1])
    stages = list(data['processing_times'].keys())
    avg_times = [np.mean(data['processing_times'][stage]) for stage in stages]
    colors_list = [COLORS['ingestion'], COLORS['agent'], COLORS['enrichment'], 
                   COLORS['mcp_client'], COLORS['task_mgmt']]
    bars = ax4.bar(range(len(stages)), avg_times, color=colors_list, alpha=0.8)
    ax4.set_xticks(range(len(stages)))
    ax4.set_xticklabels([s.split()[0] for s in stages], rotation=45, ha='right')
    ax4.set_title('Avg Processing Time', fontweight='bold')
    ax4.set_ylabel('Seconds')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. Success rates (middle-right)
    ax5 = fig.add_subplot(gs[1, 2])
    components = list(data['success_rates'].keys())
    rates = list(data['success_rates'].values())
    bars = ax5.barh(components, rates, color=[
        COLORS['success'] if r >= 95 else COLORS['warning'] if r >= 90 else COLORS['error']
        for r in rates
    ], alpha=0.8)
    ax5.set_xlim(0, 105)
    ax5.set_title('Success Rates', fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='x')
    plt.setp(ax5.yaxis.get_majorticklabels(), fontsize=8)
    
    # 6. MCP Server calls (bottom-left)
    ax6 = fig.add_subplot(gs[2, 0])
    servers = list(data['mcp_stats'].keys())
    calls = [data['mcp_stats'][s]['calls'] for s in servers]
    colors_mcp = [COLORS['ingestion'], COLORS['enrichment'], COLORS['task_mgmt']]
    ax6.bar([s.split()[0] for s in servers], calls, color=colors_mcp, alpha=0.8)
    ax6.set_title('MCP Server Calls', fontweight='bold')
    ax6.set_ylabel('Calls')
    ax6.grid(True, alpha=0.3, axis='y')
    
    # 7. API Usage (bottom-center)
    ax7 = fig.add_subplot(gs[2, 1])
    apis = list(data['api_usage'].keys())
    usage = list(data['api_usage'].values())
    colors_api = [COLORS['enrichment'], COLORS['warning'], COLORS['task_mgmt'], 
                  COLORS['mcp_client'], COLORS['agent']]
    ax7.pie(usage, labels=apis, autopct='%1.0f%%', colors=colors_api, startangle=90)
    ax7.set_title('API Usage', fontweight='bold')
    
    # 8. Lead quality (bottom-right)
    ax8 = fig.add_subplot(gs[2, 2])
    scores = np.clip(data['lead_scores'], 1, 10)
    n, bins, patches = ax8.hist(scores, bins=15, edgecolor='black', alpha=0.7)
    for i, patch in enumerate(patches):
        if bins[i] > 7:
            patch.set_facecolor(COLORS['success'])
        elif bins[i] > 5:
            patch.set_facecolor(COLORS['warning'])
        else:
            patch.set_facecolor(COLORS['error'])
    ax8.axvline(x=7, color='red', linestyle='--', linewidth=2)
    ax8.set_title('Lead Quality Scores', fontweight='bold')
    ax8.set_xlabel('Score')
    ax8.grid(True, alpha=0.3, axis='y')
    
    plt.savefig(output_dir / 'dashboard_summary.png', dpi=300, bbox_inches='tight')
    print(f"✅ Generated: dashboard_summary.png")
    plt.close()


def main():
    """Main function to generate all graphs"""
    print("=" * 60)
    print("Business Agent 2.0 - Graph Generator")
    print("=" * 60)
    print()
    
    # Create output directory
    output_dir = create_output_dir()
    print(f"📁 Output directory: {output_dir.absolute()}")
    print()
    
    # Generate sample data
    print("📊 Generating sample data...")
    data = generate_sample_data()
    print("✅ Sample data generated")
    print()
    
    # Generate all graphs
    print("🎨 Generating visualizations...")
    print()
    
    plot_lead_processing_trends(data, output_dir)
    plot_data_source_distribution(data, output_dir)
    plot_lead_quality_distribution(data, output_dir)
    plot_processing_times(data, output_dir)
    plot_success_rates(data, output_dir)
    plot_mcp_server_stats(data, output_dir)
    plot_api_usage(data, output_dir)
    create_dashboard_summary(data, output_dir)
    
    print()
    print("=" * 60)
    print(f"✅ All graphs generated successfully!")
    print(f"📂 Location: {output_dir.absolute()}")
    print("=" * 60)
    print()
    print("Generated files:")
    print("  1. lead_processing_trends.png - Daily lead metrics")
    print("  2. data_source_distribution.png - Data source analytics")
    print("  3. lead_quality_distribution.png - Lead score analysis")
    print("  4. processing_times.png - Workflow timing")
    print("  5. success_rates.png - Component success rates")
    print("  6. mcp_server_stats.png - MCP server performance")
    print("  7. api_usage.png - External API statistics")
    print("  8. dashboard_summary.png - Complete dashboard")


if __name__ == "__main__":
    main()
