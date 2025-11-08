#!/bin/bash

lms server start &

streamlit run chat.py &
