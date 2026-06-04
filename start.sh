#!/bin/bash
apt-get update
apt-get install -y ffmpeg
streamlit run enhance.py --server.port=$PORT --server.address=0.0.0.0