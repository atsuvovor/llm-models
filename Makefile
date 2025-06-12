.PHONY: run build docker-clean

run:
	streamlit run app.py

install:
	pip install -r requirements.txt

build:
	docker build -t cyber-attack-sim-app .

docker-clean:
	docker stop $$(docker ps -aq) && docker rm $$(docker ps -aq) || true
