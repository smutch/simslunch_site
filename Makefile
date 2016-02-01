manual:
	python make_selection.py
	python generate.py
	open build/index.html

auto:
	python increment.py
	python make_selection.py
	python generate.py
	open build/index.html

push:
	git add .
	git commit -m "increment `date +"%d/%m/%y"`"
	git subtree push --prefix build origin gh-pages

.PHONY: manual auto push
