import html
import streamlit as st
from modules.config import CURRENCY


def money(value):
    return f"{CURRENCY} {value:,.2f}"


def number(value):
    return f"{value:,.0f}"


def safe_html(value):
    return html.escape(str(value))


def section_heading(title, description=""):
    st.markdown(
        f"""
        <div class="section-heading">{safe_html(title)}</div>
        <div class="section-description">{safe_html(description)}</div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, icon, footer, delay=0):
    st.markdown(
        f"""
        <div class="metric-card" style="animation-delay:{delay}s">
            <div class="metric-top" style="display:flex; justify-content:space-between; align-items:center;">
                <div class="metric-label">{safe_html(label)}</div>
                <div style="background:#E8F5F3; padding:6px 10px; border-radius:8px; font-weight:700;">{icon}</div>
            </div>
            <div class="metric-value">{safe_html(value)}</div>
            <div class="metric-footer">{safe_html(footer)}</div>
            <div class="metric-accent"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_figure(fig, height=380):
    fig.update_layout(
        height=height,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="DM Sans, sans-serif", color="#172B3A", size=13),
        legend=dict(
            font=dict(family="DM Sans, sans-serif", color="#172B3A", size=13),
            title=dict(font=dict(color="#172B3A", size=13)),
        ),
        margin=dict(l=20, r=35, t=40, b=30),
        hoverlabel=dict(bgcolor="#172B3A", font_color="#FFFFFF", font_size=13),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E5EBF0",
        zeroline=False,
        showline=True,
        linecolor="#CBD5E1",
        tickfont=dict(family="DM Sans, sans-serif", color="#172B3A", size=12),
        title_font=dict(family="DM Sans, sans-serif", color="#172B3A", size=13),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E5EBF0",
        zeroline=False,
        showline=True,
        linecolor="#CBD5E1",
        tickfont=dict(family="DM Sans, sans-serif", color="#172B3A", size=12),
        title_font=dict(family="DM Sans, sans-serif", color="#172B3A", size=13),
    )
    return fig