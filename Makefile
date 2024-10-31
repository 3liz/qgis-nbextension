
PYTHON_PKG=qgisnbextension

lint:
	@ruff check --output-format=concise  $(PYTHON_PKG)

lint-fix:
	@ruff check --preview --fix $(PYTHON_PKG)

typing: 
	@mypy $(PYTHON_PKG)
