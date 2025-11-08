#!/bin/bash
if [ -n "$1" ]
then


export OLLAMA_MODELS=$1

ollama serve &

streamlit run chat.py &

else
echo "OLLAMA_MODELS path not set. "
fi
