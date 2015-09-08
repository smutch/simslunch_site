import yaml
import pandas as pd
import toyplot
import toyplot.html
from jinja2 import Environment, FileSystemLoader

# read in the list of members and their presenting histories
with open('members.yaml', 'r') as fd:
    members_in = yaml.load(fd)

# convert to a pandas dataframe
members = pd.DataFrame.from_dict(members_in).T
members.index.name = 'name'

# generate plots of the current standings and render them to html files
for contribution in ["Papers", "Plots"]:
    canvas, axes, mark = toyplot.bars(members[contribution.lower()], width=20+50*members.shape[0], height=300)
    axes.x.ticks.locator = toyplot.locator.Explicit(labels=members.index)
    axes.label.text = contribution
    axes.x.ticks.labels.angle = 45
    axes.x.ticks.show = True
    axes.x.ticks.labels.style = {"baseline-shift":0, "text-anchor":"end", "-toyplot-anchor-shift":"-6px"}
    axes.y.label.text = "Times presented"
    axes.y.ticks.locator = toyplot.locator.Integer()
    toyplot.html.render(canvas, fobj="templates/"+contribution.lower()+"_history.html")

# read in this week's presenters
with open('selected_presenters.yaml', 'r') as fd:
    presenters = yaml.load(fd)

# render the page
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')
with open('build/index.html', 'w') as fd:
    fd.write(template.render(presenters=presenters))

# increment the presenter counters
for member_type in iter(presenters.values()):
    for presentation, name in iter(member_type.items()):
        members_in[name][presentation+'s'] += 1

# write out the updated members list
with open('members.yaml', 'w') as fd:
    yaml.safe_dump(members_in, fd)

