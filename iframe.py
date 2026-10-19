import streamlit as st
import streamlit.components.v1 as components

st.title("Advanced Unblocked Iframe")

target_url = "https://crazygames.com"

# Custom HTML that loads the unblocker scripts and injects the modified iframe
iframe_html = f"""
<script src="https://unpkg.com"></script>
<script type="module" src="https://unpkg.com"></script>

<iframe is="x-frame-bypass" src="{target_url}" style="width:100%; height:100%; border:none;"></iframe>
"""

# Render the HTML component inside Streamlit
components.html(iframe_html, height=700)
