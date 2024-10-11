pip install --upgrade pip

sh export_requirements_from_poetry.sh
pip install -r requirements.txt

vllm serve meta-llama/Meta-Llama-3.1-8B
