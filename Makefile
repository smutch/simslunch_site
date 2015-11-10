auto:
	python increment.py
	python make_selection.py
	python generate.py
	open build/index.html

manual:
	python make_selection.py
	python generate.py
	open build/index.html

.PHONY: manual
