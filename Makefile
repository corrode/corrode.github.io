SHELL := /bin/bash

.PHONY: help
help: ## This help message
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

.PHONY: dev run serve
dev run serve: ## Serve website locally
	zola serve --drafts
    
.PHONY: build
build: ## Build website
	zola build

.PHONY: social
social: ## Generate social images for blog posts
	./scripts/social.sh

.PHONY: workshops
workshops: ## Generate workshop pages
	./scripts/workshops.py
