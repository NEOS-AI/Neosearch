pip install --upgrade pip

sh export_requirements_from_poetry.sh
pip install -r requirements.txt

# For CUDA 12.4 & torch 2.4
pip install flashinfer -i https://flashinfer.ai/whl/cu124/torch2.4
# For other CUDA & torch versions, please check https://docs.flashinfer.ai/installation.html

# For 4 GPUs total (2 data parallel, 2 tensor parallel)
python3 -m sglang.launch_server --model-path meta-llama/Meta-Llama-3-8B-Instruct --port 30000 --dp 2 --tp 2