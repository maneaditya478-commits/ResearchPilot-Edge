"""
ResearchPilot Edge - Modern UI Design System
Provides clean CSS stylesheets, badges, metric cards, and responsive scientific styling.
"""

CUSTOM_CSS = """
<style>
    /* Global Typography & Palette */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        padding-left: 2.2rem;
        padding-right: 2.2rem;
        max-width: 1380px;
    }

    /* Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0b192c 0%, #1e3e62 50%, #000000 100%);
        border: 1px solid #2d4f7c;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        color: #ffffff;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }
    .hero-title {
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-tagline {
        font-size: 14px;
        color: #93c5fd;
        margin-bottom: 12px;
        font-weight: 400;
    }
    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }
    .badge {
        font-size: 11px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    .badge-offline {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .badge-snapdragon {
        background: rgba(225, 29, 72, 0.15);
        color: #f43f5e;
        border: 1px solid rgba(225, 29, 72, 0.4);
    }
    .badge-backend {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.4);
    }
    .badge-privacy {
        background: rgba(168, 85, 247, 0.15);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.4);
    }

    /* Metric Cards */
    .metric-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 16px 20px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .metric-card:hover {
        border-color: #3b82f6;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 500;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #f9fafb;
    }
    .metric-sub {
        font-size: 11px;
        color: #6b7280;
        margin-top: 4px;
    }

    /* Citation Card */
    .citation-card {
        background: #182234;
        border-left: 3px solid #3b82f6;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-top: 10px;
        margin-bottom: 8px;
        font-size: 13px;
        color: #e2e8f0;
    }
    .citation-header {
        font-weight: 600;
        color: #60a5fa;
        font-size: 12px;
        margin-bottom: 4px;
        display: flex;
        justify-content: space-between;
    }
    .citation-snippet {
        font-style: italic;
        color: #cbd5e1;
    }

    /* Summary Card Section */
    .summary-section {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .summary-heading {
        font-size: 14px;
        font-weight: 600;
        color: #38bdf8;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .summary-body {
        font-size: 14px;
        line-height: 1.6;
        color: #f1f5f9;
    }

    /* Custom Streamlit adjustments */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #1f2937;
        border-radius: 8px;
        background: #0b1120;
    }
</style>
"""
