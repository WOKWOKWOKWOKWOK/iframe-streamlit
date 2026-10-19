import streamlit as st
import requests
import json

st.set_page_config(layout="wide", title="Cloud VM Manager")

# Enter your Cloud Platform API token safely here or via st.secrets
# This example uses DigitalOcean's straightforward API to spin up an Ubuntu Droplet
API_TOKEN = st.text_input("Enter your Provider API Token:", type="password")

st.title("🚀 Custom Ubuntu VM Provisioner")
st.write("Configure and deploy a cloud VM instantly.")

col1, col2 = st.columns(2)
with col1:
    vm_name = st.text_input("Instance Name", value="streamlit-ubuntu-node")
    region = st.selectbox("Data Center Region", ["nyc1", "sfo3", "ams3", "fra1"])

with col2:
    ubuntu_version = st.selectbox("Ubuntu Base Image", ["ubuntu-24-04-x64", "ubuntu-22-04-x64"])
    size_slug = st.selectbox("Hardware Size", ["s-1vcpu-1gb", "s-1vcpu-2gb", "s-2vcpu-4gb"])

if st.button("Deploy Live VM Instance", type="primary"):
    if not API_TOKEN:
        st.error("Please provide a valid API authentication token first.")
    else:
        with st.spinner("Provisioning your Ubuntu environment on the cloud..."):
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_TOKEN}"
            }
            payload = {
                "name": vm_name,
                "region": region,
                "size": size_slug,
                "image": ubuntu_version,
                "backups": False,
                "ipv6": True
            }
            
            # API endpoint to launch a virtual instance
            url = "https://digitalocean.com"
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 202:
                data = response.json()
                st.success(f"Successfully created droplet! ID: {data['droplet']['id']}")
                st.info("The server is spinning up. Give it ~60 seconds to fetch your public IP address.")
                st.json(data['droplet'])
            else:
                st.error(f"Failed to create instance: {response.text}")
