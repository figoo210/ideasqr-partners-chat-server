lsof -ti :8000 | xargs kill -9
cd server
source venv/bin/activate
nohup python3 main.py > output.log &