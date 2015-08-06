from jinja2 import Environment, FileSystemLoader
import yaml
import pandas as pd
import random
import warnings
import toyplot
import toyplot.html

env = Environment(loader=FileSystemLoader('templates'))

with open('members.yaml', 'r') as fd:
    members = yaml.load(fd)

members = pd.DataFrame.from_dict(members).T
members.available.fillna(True, inplace=True)
members.index.name = 'name'

for contribution in ["Papers", "Plots"]:
    canvas, axes, mark = toyplot.bars(members[contribution.lower()], width=60+80*members.shape[0], height=300)
    axes.x.ticks.locator = toyplot.locator.Explicit(labels=members.index)
    axes.label.text = contribution
    axes.y.label.text = "Times presented"
    axes.y.ticks.locator = toyplot.locator.Integer()

    with open("templates/"+contribution.lower()+"_history.html", "wb") as fd:
        #  fd.write(bytes('{% extends "index.html" %}'+"\n"
        #        +"{% block "+contribution.lower()+"_history %}\n", 'UTF-8'))
        toyplot.html.render(canvas, fobj=fd)
        #  fd.write(bytes("\n{% endblock %}\n", 'UTF-8'))

members = members.query('available')

n_presenters = 2

mi = members.papers.min()
pool = list(members.query('papers == @mi').index)
paper_presenters = random.sample(pool, n_presenters)

mi = members.plots.min()
pool = list(members.query('plots == @mi').index)
plot_presenters = random.sample(pool, n_presenters)

max_tries = 100
n_tries = 0
while len(set(plot_presenters + paper_presenters)) != 4:
    plot_presenters = random.sample(pool, n_presenters)
    n_tries+=1
    if n_tries == max_tries:
        warnings.warn("Failed to find unique paper + plot presenters!")
        break

template = env.get_template('index.html')
with open('build/index.html', 'w') as fd:
    fd.write(template.render(paper_presenters=paper_presenters,
                             plot_presenters=plot_presenters))
