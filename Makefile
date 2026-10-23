target:
	@printf "Use 'make \033[0;36mtarget\033[0m' where \033[0;36mtarget\033[0m is one of the following:\n\n"
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {t[++c]=$$1; d[c]=$$NF; type[c]=1; if(length($$1)>m) m=length($$1)} /^##@/ {type[++c]=0; text[c]=substr($$0, 5)} END {for(i=1;i<=c;i++) if(type[i]==1) printf "  \033[0;36m%-*s\033[0m %s\n", m, t[i], d[i]; else {if(h++) printf "\n"; printf "\033[1m%s\033[0m\n", text[i]}}' $(MAKEFILE_LIST)


clean:  ## Clean the project
	rm -rf build dist *.egg-info .venv .ruff_cache
	rm uv.lock

type:  ## Run pyright
	@uv run pyright --pythonversion 3.13

lint:  ## Run ruff
	@uv run ruff check --config pyproject.toml

install:  ## Install the project
	uv sync

install_dev:	 ## Install the package in development mode
	uv sync --all-extras
