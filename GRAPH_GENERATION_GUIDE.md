# Graph Generation Guide

This guide explains how to generate visualizations for your Business Agent 2.0 system.

## Overview

Two graph generation tools are available:

1. **Static Graphs** (`generate_graphs.py`) - PNG images using Matplotlib
2. **Interactive Dashboards** (`generate_interactive_dashboard.py`) - HTML dashboards using Plotly

## Installation

Install the required packages:

```bash
pip install matplotlib plotly pandas numpy
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Generate Static Graphs

Run the static graph generator:

```bash
python generate_graphs.py
```

### Generated Static Graphs

The script creates 8 PNG files in `graphs_output/`:

| File | Description |
|------|-------------|
| `lead_processing_trends.png` | 30-day trends of leads processed, qualified, tasks, and emails |
| `data_source_distribution.png` | Pie chart and bar chart of data sources (RSS, Reddit, Web, Twitter) |
| `lead_quality_distribution.png` | Histogram and box plot of lead quality scores |
| `processing_times.png` | Box plots and bar charts of workflow stage timings |
| `success_rates.png` | Horizontal bar chart of component success rates |
| `mcp_server_stats.png` | MCP server calls, response times, and error counts |
| `api_usage.png` | External API usage statistics (Hunter.io, Trello, etc.) |
| `dashboard_summary.png` | Comprehensive 8-panel dashboard overview |

### Example: Static Graphs

```python
from generate_graphs import generate_sample_data, plot_lead_processing_trends, create_output_dir

# Create output directory
output_dir = create_output_dir()

# Generate data
data = generate_sample_data()

# Generate specific graph
plot_lead_processing_trends(data, output_dir)
```

## Generate Interactive Dashboards

Run the interactive dashboard generator:

```bash
python generate_interactive_dashboard.py
```

### Generated Interactive Dashboards

The script creates 3 HTML files in `graphs_output/`:

| File | Description |
|------|-------------|
| `interactive_main_dashboard.html` | 9-panel overview with all key metrics |
| `interactive_lead_analysis.html` | Detailed lead qualification analysis with funnel |
| `interactive_performance_dashboard.html` | Performance metrics with health indicator |

### Features of Interactive Dashboards

- ✨ **Hover tooltips** - Detailed information on hover
- 🔍 **Zoom & Pan** - Interactive exploration
- 📥 **Export** - Download as PNG or SVG
- 🎯 **Select & Filter** - Click legend items to toggle visibility
- 📱 **Responsive** - Works on desktop and mobile

### Open in Browser

Simply double-click any HTML file or:

```bash
# Windows
start graphs_output\interactive_main_dashboard.html

# Mac/Linux
open graphs_output/interactive_main_dashboard.html
```

## Using Real Data

### Replace Sample Data

Both scripts use `generate_sample_data()` which creates synthetic data. To use real data:

#### Option 1: Modify the data structure

```python
# Your custom data
real_data = {
    'dates': [...],  # List of datetime objects
    'leads_processed': [...],  # List of integers
    'leads_qualified': [...],  # List of integers
    # ... other metrics
}

# Use with existing functions
plot_lead_processing_trends(real_data, output_dir)
```

#### Option 2: Load from database/file

```python
import json
from datetime import datetime

# Load from Qdrant or your database
def load_real_data():
    # Connect to Qdrant
    from qdrant_client import QdrantClient
    client = QdrantClient("localhost", port=6333)
    
    # Query your metrics
    # ... your data fetching logic
    
    return {
        'dates': dates,
        'leads_processed': processed,
        # ... your real metrics
    }

# Use real data
data = load_real_data()
create_main_dashboard(data).write_html('my_dashboard.html')
```

#### Option 3: Load from CSV

```python
import pandas as pd

# Load from CSV
df = pd.read_csv('metrics.csv')
df['date'] = pd.to_datetime(df['date'])

data = {
    'dates': df['date'].tolist(),
    'leads_processed': df['processed'].tolist(),
    'leads_qualified': df['qualified'].tolist(),
    # ... map your columns
}
```

## Customization

### Change Colors

Edit the `COLORS` dictionary in either script:

```python
COLORS = {
    'agent': '#4A90E2',      # Blue
    'mcp_client': '#7B68EE',  # Purple
    'ingestion': '#50C878',   # Green
    'enrichment': '#FFB347',  # Orange
    'task_mgmt': '#FF6B6B',   # Red
    'storage': '#9B59B6',     # Purple
    'success': '#27AE60',     # Green
    'warning': '#F39C12',     # Orange
    'error': '#E74C3C'        # Red
}
```

### Add New Graphs

#### Static Graph Example

```python
def plot_my_custom_metric(data, output_dir):
    """Generate custom metric visualization"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Your plotting code
    ax.plot(data['dates'], data['my_metric'])
    ax.set_title('My Custom Metric')
    
    plt.savefig(output_dir / 'my_custom_metric.png', dpi=300)
    plt.close()
```

#### Interactive Graph Example

```python
import plotly.graph_objects as go

def create_my_dashboard(data):
    """Create custom interactive dashboard"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['dates'],
        y=data['my_metric'],
        mode='lines+markers',
        name='My Metric'
    ))
    
    fig.update_layout(title='My Custom Dashboard')
    
    return fig

# Save it
fig = create_my_dashboard(data)
fig.write_html('my_dashboard.html')
```

## Integration with Agent

### Log Metrics During Runtime

Create a metrics logger in your agent:

```python
import json
from datetime import datetime
from pathlib import Path

class MetricsLogger:
    def __init__(self, log_file='metrics.json'):
        self.log_file = Path(log_file)
        self.metrics = self.load_metrics()
    
    def load_metrics(self):
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return {'dates': [], 'leads_processed': [], 'leads_qualified': []}
    
    def log(self, **kwargs):
        """Log metrics: logger.log(leads_processed=10, leads_qualified=7)"""
        self.metrics['dates'].append(datetime.now().isoformat())
        for key, value in kwargs.items():
            if key not in self.metrics:
                self.metrics[key] = []
            self.metrics[key].append(value)
        self.save_metrics()
    
    def save_metrics(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)

# Use in your agent
logger = MetricsLogger()

# After processing leads
logger.log(
    leads_processed=25,
    leads_qualified=12,
    tasks_created=8,
    emails_sent=6
)
```

### Generate Graphs from Logged Metrics

```python
from generate_graphs import create_dashboard_summary
from generate_interactive_dashboard import create_main_dashboard
import json
from datetime import datetime

# Load logged metrics
with open('metrics.json', 'r') as f:
    metrics = json.load(f)

# Convert dates
metrics['dates'] = [datetime.fromisoformat(d) for d in metrics['dates']]

# Generate visualizations
create_dashboard_summary(metrics, Path('graphs_output'))
create_main_dashboard(metrics).write_html('live_dashboard.html')
```

## Scheduled Graph Generation

### Generate Graphs Daily

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from generate_graphs import main as generate_static
from generate_interactive_dashboard import main as generate_interactive

def daily_report():
    """Generate daily graphs"""
    print(f"Generating daily report at {datetime.now()}")
    generate_static()
    generate_interactive()

scheduler = BlockingScheduler()
scheduler.add_job(daily_report, 'cron', hour=23, minute=0)  # 11 PM daily
scheduler.start()
```

## Tips & Best Practices

### Performance

- **Large datasets**: Use aggregation before plotting (e.g., weekly averages instead of daily)
- **Many graphs**: Generate in parallel using multiprocessing
- **File size**: Use lower DPI (150-200) for web display, 300 for print

### Data Quality

- **Missing data**: Fill gaps with interpolation or mark as N/A
- **Outliers**: Use box plots to identify and handle outliers
- **Trends**: Apply moving averages for clearer trend visualization

### Presentation

- **Colors**: Use consistent color scheme across all graphs
- **Labels**: Always include axis labels and units
- **Titles**: Make titles descriptive and informative
- **Legends**: Position legends where they don't obscure data

## Example Workflow

1. **Run your agent** and log metrics
2. **Generate daily reports** with both static and interactive graphs
3. **Review dashboards** in browser for insights
4. **Export static images** for presentations or reports
5. **Share HTML dashboards** with stakeholders

```bash
# Daily workflow
python main.py  # Run agent
python generate_graphs.py  # Generate PNGs
python generate_interactive_dashboard.py  # Generate HTML
```

## Troubleshooting

### Import Errors

```bash
pip install --upgrade matplotlib plotly pandas numpy
```

### Display Issues

**Static graphs not showing:**
- Ensure output directory exists
- Check file permissions
- Verify matplotlib backend: `import matplotlib; matplotlib.use('Agg')`

**Interactive dashboards blank:**
- Open in modern browser (Chrome, Firefox, Edge)
- Check browser console for errors
- Ensure file size isn't too large (< 100MB)

### Memory Issues

For large datasets:

```python
# Sample data before plotting
import random
sampled_data = random.sample(large_dataset, 10000)

# Or use aggregation
df_daily = df.resample('D').mean()  # Daily averages
```

## Resources

- **Matplotlib Gallery**: https://matplotlib.org/stable/gallery/
- **Plotly Examples**: https://plotly.com/python/
- **Color Palettes**: https://colorbrewer2.org/

## Support

For issues or questions:
1. Check the generated sample data structure
2. Verify all required packages are installed
3. Review error messages for specific issues
4. Consult Matplotlib/Plotly documentation for customization
