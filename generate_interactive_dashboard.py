"""
Business Agent 2.0 - Interactive Dashboard Generator
Creates interactive HTML dashboards using Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json


# Color scheme matching the system
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
        
        'data_sources': {
            'RSS Feeds': 450,
            'Reddit': 280,
            'Web Scraping': 320,
            'Twitter': 120
        },
        
        'lead_scores': np.random.normal(6.5, 1.5, 100),
        
        'processing_times': {
            'Retrieve': np.random.gamma(2, 1.5, 100),
            'Qualify': np.random.gamma(3, 1.2, 100),
            'Enrich': np.random.gamma(4, 2, 100),
            'Draft Email': np.random.gamma(2.5, 1, 100),
            'Create Task': np.random.gamma(2, 0.8, 100)
        },
        
        'success_rates': {
            'Data Ingestion': 98.5,
            'Lead Qualification': 94.2,
            'Email Enrichment': 87.3,
            'Task Creation': 99.1,
            'Overall Pipeline': 85.7
        },
        
        'mcp_stats': {
            'Ingestion Server': {'calls': 1250, 'avg_time': 2.3, 'errors': 12},
            'Enrichment Server': {'calls': 890, 'avg_time': 3.8, 'errors': 45},
            'Task Management Server': {'calls': 670, 'avg_time': 1.9, 'errors': 8}
        },
        
        'api_usage': {
            'Hunter.io': 450,
            'Clearbit': 230,
            'Trello': 380,
            'Notion': 145,
            'Discord': 290
        }
    }
    
    return data


def create_main_dashboard(data):
    """Create main interactive dashboard"""
    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=(
            'Lead Processing Trends', 'Conversion Rate', 'Data Source Distribution',
            'Processing Times by Stage', 'Success Rates', 'Lead Quality Distribution',
            'MCP Server Calls', 'API Usage', 'Tasks & Emails'
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}, {"type": "pie"}],
            [{"type": "bar"}, {"type": "bar"}, {"type": "histogram"}],
            [{"type": "bar"}, {"type": "pie"}, {"secondary_y": False}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # 1. Lead Processing Trends
    fig.add_trace(
        go.Scatter(x=data['dates'], y=data['leads_processed'],
                  mode='lines+markers', name='Processed',
                  line=dict(color=COLORS['agent'], width=2),
                  marker=dict(size=6)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=data['dates'], y=data['leads_qualified'],
                  mode='lines+markers', name='Qualified',
                  line=dict(color=COLORS['success'], width=2),
                  marker=dict(size=6)),
        row=1, col=1
    )
    
    # 2. Conversion Rate
    conversion_rate = (np.array(data['leads_qualified']) / np.array(data['leads_processed'])) * 100
    fig.add_trace(
        go.Scatter(x=data['dates'], y=conversion_rate,
                  mode='lines+markers', name='Conversion',
                  line=dict(color=COLORS['enrichment'], width=3),
                  marker=dict(size=6),
                  fill='tozeroy'),
        row=1, col=2
    )
    
    # 3. Data Source Distribution
    fig.add_trace(
        go.Pie(labels=list(data['data_sources'].keys()),
               values=list(data['data_sources'].values()),
               marker=dict(colors=[COLORS['ingestion'], COLORS['enrichment'], 
                                  COLORS['task_mgmt'], COLORS['warning']]),
               name='Sources'),
        row=1, col=3
    )
    
    # 4. Processing Times
    stages = list(data['processing_times'].keys())
    avg_times = [np.mean(data['processing_times'][stage]) for stage in stages]
    colors_list = [COLORS['ingestion'], COLORS['agent'], COLORS['enrichment'], 
                   COLORS['mcp_client'], COLORS['task_mgmt']]
    
    fig.add_trace(
        go.Bar(x=stages, y=avg_times,
               marker=dict(color=colors_list),
               name='Avg Time',
               text=[f'{t:.2f}s' for t in avg_times],
               textposition='outside'),
        row=2, col=1
    )
    
    # 5. Success Rates
    components = list(data['success_rates'].keys())
    rates = list(data['success_rates'].values())
    colors_success = [COLORS['success'] if r >= 95 else COLORS['warning'] if r >= 90 
                     else COLORS['error'] for r in rates]
    
    fig.add_trace(
        go.Bar(y=components, x=rates, orientation='h',
               marker=dict(color=colors_success),
               name='Success Rate',
               text=[f'{r:.1f}%' for r in rates],
               textposition='outside'),
        row=2, col=2
    )
    
    # 6. Lead Quality Distribution
    scores = np.clip(data['lead_scores'], 1, 10)
    fig.add_trace(
        go.Histogram(x=scores, nbinsx=20,
                    marker=dict(color=COLORS['agent']),
                    name='Scores'),
        row=2, col=3
    )
    
    # 7. MCP Server Calls
    servers = list(data['mcp_stats'].keys())
    calls = [data['mcp_stats'][s]['calls'] for s in servers]
    colors_mcp = [COLORS['ingestion'], COLORS['enrichment'], COLORS['task_mgmt']]
    
    fig.add_trace(
        go.Bar(x=[s.split()[0] for s in servers], y=calls,
               marker=dict(color=colors_mcp),
               name='Calls',
               text=calls,
               textposition='outside'),
        row=3, col=1
    )
    
    # 8. API Usage
    fig.add_trace(
        go.Pie(labels=list(data['api_usage'].keys()),
               values=list(data['api_usage'].values()),
               marker=dict(colors=[COLORS['enrichment'], COLORS['warning'], 
                                  COLORS['task_mgmt'], COLORS['mcp_client'], COLORS['agent']]),
               name='APIs'),
        row=3, col=2
    )
    
    # 9. Tasks & Emails
    fig.add_trace(
        go.Scatter(x=data['dates'], y=data['tasks_created'],
                  mode='lines+markers', name='Tasks',
                  line=dict(color=COLORS['task_mgmt'], width=2),
                  marker=dict(size=6)),
        row=3, col=3
    )
    fig.add_trace(
        go.Scatter(x=data['dates'], y=data['emails_sent'],
                  mode='lines+markers', name='Emails',
                  line=dict(color=COLORS['mcp_client'], width=2),
                  marker=dict(size=6)),
        row=3, col=3
    )
    
    # Update layout
    fig.update_layout(
        title_text="Business Agent 2.0 - Interactive Dashboard",
        title_font_size=24,
        showlegend=True,
        height=1200,
        template='plotly_white'
    )
    
    return fig


def create_lead_analysis_dashboard(data):
    """Create detailed lead analysis dashboard"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Lead Processing Over Time',
            'Lead Quality Score Distribution',
            'Qualification Funnel',
            'Success vs Rejection Reasons'
        ),
        specs=[
            [{"secondary_y": True}, {"type": "box"}],
            [{"type": "funnel"}, {"type": "bar"}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.15
    )
    
    # 1. Lead Processing with conversion rate (dual axis)
    fig.add_trace(
        go.Bar(x=data['dates'], y=data['leads_processed'],
               name='Processed', marker_color=COLORS['agent']),
        row=1, col=1, secondary_y=False
    )
    fig.add_trace(
        go.Bar(x=data['dates'], y=data['leads_qualified'],
               name='Qualified', marker_color=COLORS['success']),
        row=1, col=1, secondary_y=False
    )
    
    conversion_rate = (np.array(data['leads_qualified']) / np.array(data['leads_processed'])) * 100
    fig.add_trace(
        go.Scatter(x=data['dates'], y=conversion_rate,
                  name='Conversion %', mode='lines+markers',
                  line=dict(color=COLORS['enrichment'], width=3)),
        row=1, col=1, secondary_y=True
    )
    
    # 2. Lead Quality Box Plot
    scores = np.clip(data['lead_scores'], 1, 10)
    fig.add_trace(
        go.Box(y=scores, name='All Leads',
               marker_color=COLORS['agent'],
               boxmean='sd'),
        row=1, col=2
    )
    
    # 3. Funnel Chart
    total_leads = sum(data['leads_processed'])
    qualified = sum(data['leads_qualified'])
    enriched = int(qualified * 0.85)  # Assuming 85% successfully enriched
    tasks = sum(data['tasks_created'])
    
    fig.add_trace(
        go.Funnel(
            y=['Leads Retrieved', 'Qualified (>7)', 'Enriched', 'Tasks Created'],
            x=[total_leads, qualified, enriched, tasks],
            textinfo='value+percent initial',
            marker=dict(color=[COLORS['ingestion'], COLORS['success'], 
                              COLORS['enrichment'], COLORS['task_mgmt']])
        ),
        row=2, col=1
    )
    
    # 4. Rejection vs Success
    categories = ['Qualified', 'Low Score', 'No Data', 'Enrichment Failed']
    values = [qualified, total_leads - qualified - 50, 30, 20]
    colors_cat = [COLORS['success'], COLORS['error'], COLORS['warning'], COLORS['error']]
    
    fig.add_trace(
        go.Bar(x=categories, y=values,
               marker=dict(color=colors_cat),
               text=values, textposition='outside'),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text="Lead Analysis Dashboard",
        title_font_size=24,
        showlegend=True,
        height=900,
        template='plotly_white'
    )
    
    fig.update_yaxes(title_text="Count", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Conversion %", row=1, col=1, secondary_y=True)
    
    return fig


def create_performance_dashboard(data):
    """Create performance metrics dashboard"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Workflow Stage Processing Times',
            'MCP Server Performance',
            'Success Rate Heatmap',
            'System Health Score'
        ),
        specs=[
            [{"type": "box"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "indicator"}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )
    
    # 1. Processing Times Box Plot
    stages = list(data['processing_times'].keys())
    for i, stage in enumerate(stages):
        colors_list = [COLORS['ingestion'], COLORS['agent'], COLORS['enrichment'], 
                      COLORS['mcp_client'], COLORS['task_mgmt']]
        fig.add_trace(
            go.Box(y=data['processing_times'][stage],
                   name=stage,
                   marker_color=colors_list[i]),
            row=1, col=1
        )
    
    # 2. MCP Server Performance (calls, response time, errors)
    servers = list(data['mcp_stats'].keys())
    for i, metric in enumerate(['calls', 'avg_time', 'errors']):
        values = [data['mcp_stats'][s][metric] for s in servers]
        fig.add_trace(
            go.Bar(x=[s.split()[0] for s in servers],
                   y=values,
                   name=metric.replace('_', ' ').title(),
                   text=values,
                   textposition='outside'),
            row=1, col=2
        )
    
    # 3. Success Rates
    components = list(data['success_rates'].keys())
    rates = list(data['success_rates'].values())
    colors_success = [COLORS['success'] if r >= 95 else COLORS['warning'] if r >= 90 
                     else COLORS['error'] for r in rates]
    
    fig.add_trace(
        go.Bar(y=components, x=rates, orientation='h',
               marker=dict(color=colors_success),
               text=[f'{r:.1f}%' for r in rates],
               textposition='outside'),
        row=2, col=1
    )
    
    # 4. System Health Indicator
    health_score = np.mean(rates)
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=health_score,
            title={'text': "System Health"},
            delta={'reference': 95, 'increasing': {'color': COLORS['success']}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': COLORS['agent']},
                'steps': [
                    {'range': [0, 85], 'color': COLORS['error']},
                    {'range': [85, 95], 'color': COLORS['warning']},
                    {'range': [95, 100], 'color': COLORS['success']}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text="Performance Metrics Dashboard",
        title_font_size=24,
        showlegend=True,
        height=900,
        template='plotly_white'
    )
    
    return fig


def save_dashboards(data, output_dir):
    """Save all interactive dashboards"""
    print("🎨 Creating interactive dashboards...")
    
    # Main Dashboard
    fig1 = create_main_dashboard(data)
    fig1.write_html(output_dir / 'interactive_main_dashboard.html')
    print("✅ Generated: interactive_main_dashboard.html")
    
    # Lead Analysis Dashboard
    fig2 = create_lead_analysis_dashboard(data)
    fig2.write_html(output_dir / 'interactive_lead_analysis.html')
    print("✅ Generated: interactive_lead_analysis.html")
    
    # Performance Dashboard
    fig3 = create_performance_dashboard(data)
    fig3.write_html(output_dir / 'interactive_performance_dashboard.html')
    print("✅ Generated: interactive_performance_dashboard.html")


def main():
    """Main function"""
    print("=" * 60)
    print("Business Agent 2.0 - Interactive Dashboard Generator")
    print("=" * 60)
    print()
    
    # Create output directory
    output_dir = Path("graphs_output")
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Output directory: {output_dir.absolute()}")
    print()
    
    # Generate sample data
    print("📊 Generating sample data...")
    data = generate_sample_data()
    print("✅ Sample data generated")
    print()
    
    # Save all dashboards
    save_dashboards(data, output_dir)
    
    print()
    print("=" * 60)
    print("✅ All interactive dashboards generated!")
    print(f"📂 Location: {output_dir.absolute()}")
    print("=" * 60)
    print()
    print("Generated files:")
    print("  1. interactive_main_dashboard.html - Main overview dashboard")
    print("  2. interactive_lead_analysis.html - Detailed lead analytics")
    print("  3. interactive_performance_dashboard.html - Performance metrics")
    print()
    print("💡 Open these HTML files in your browser for interactive exploration!")


if __name__ == "__main__":
    main()
