#!/bin/bash
if [ -n "$1" ]
then

pip install -r ./req.txt

export OLLAMA_MODELS=$1

ollama serve
ollama pull mxbai-embed-large
ollama pull GandalfBaum/llama3.1-claude3.7
ollama pull gpt-oss
ollama pull deepseek-r1:8b

else
echo "OLLAMA_MODELS path not set. "
fi
