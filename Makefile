HOST ?= pi0.local
USER ?= jdkram
PORT ?= 5000
REMOTE := $(USER)@$(HOST)
REMOTE_DIR := /home/$(USER)/rpi-zero-display
SERVICE := rpi-display

.PHONY: deploy restart logs ssh test-grid test-solid-white test-solid-black test-solid-red test-sizes date

deploy:
	rsync -avz --delete \
		--exclude '__pycache__' \
		--exclude '*.pyc' \
		pi/ $(REMOTE):$(REMOTE_DIR)/
	ssh $(REMOTE) "sudo cp $(REMOTE_DIR)/rpi-display.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl restart $(SERVICE)"

restart:
	ssh $(REMOTE) "sudo systemctl restart $(SERVICE)"

logs:
	ssh $(REMOTE) "journalctl -u $(SERVICE) -f"

ssh:
	ssh $(REMOTE)

test-grid:
	curl -sf "http://$(HOST):$(PORT)/test" | python3 -m json.tool

test-solid-white:
	curl -sf "http://$(HOST):$(PORT)/test/solid/white" | python3 -m json.tool

test-solid-black:
	curl -sf "http://$(HOST):$(PORT)/test/solid/black" | python3 -m json.tool

test-solid-red:
	curl -sf "http://$(HOST):$(PORT)/test/solid/red" | python3 -m json.tool

test-sizes:
	curl -sf "http://$(HOST):$(PORT)/test/sizes" | python3 -m json.tool

date:
	curl -sf "http://$(HOST):$(PORT)/date" | python3 -m json.tool
