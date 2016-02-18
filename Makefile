manual:
	python available.py
	python make_selection.py
	python generate.py
	open build/index.html

auto:
	python increment.py
	python available.py
	python make_selection.py
	python generate.py
	open build/index.html

push:
	git add .
	git commit -m "increment `date +"%d/%m/%y"`"
	git subtree push --prefix build origin gh-pages

email:
	mail -s "Speakers for next week" "simulation_lunch@lists.unimelb.edu.au" <email.txt


.PHONY: manual auto push
