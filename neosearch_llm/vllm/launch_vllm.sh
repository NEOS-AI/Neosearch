pip install --upgrade pip

sh export_requirements_from_poetry.sh
pip install -r requirements.txt

# For passing the API key, you could use it for authentication with OpenAI python client
vllm serve NousResearch/Meta-Llama-3-8B-Instruct --dtype auto --api-key nsk-myapikey
