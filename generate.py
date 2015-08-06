import warnings
import random
import yaml
import pandas as pd
import toyplot
import toyplot.html
from jinja2 import Environment, FileSystemLoader

# read in the list of members and their presenting histories
with open('members.yaml', 'r') as fd:
    members = yaml.load(fd)

# convert to a pandas dataframe
members = pd.DataFrame.from_dict(members).T
members.available.fillna(True, inplace=True)
members.index.name = 'name'

# generate plots of the current standings and render them to html files
for contribution in ["Papers", "Plots"]:
    canvas, axes, mark = toyplot.bars(members[contribution.lower()], width=60+80*members.shape[0], height=300)
    axes.x.ticks.locator = toyplot.locator.Explicit(labels=members.index)
    axes.label.text = contribution
    axes.y.label.text = "Times presented"
    axes.y.ticks.locator = toyplot.locator.Integer()
    toyplot.html.render(canvas, fobj="templates/"+contribution.lower()+"_history.html")

# cut down the members to just those who are available this coming week and
# split by type
members = members.query('available')
postdocs = members.query('type == "postdoc"')
postdocs.name = "postdocs"
postdocs.presenters = dict(
    paper = "",
    plot = ""
)
students = members.query('type == "student"')
students.name = "students"
students.presenters = postdocs.presenters.copy()

# choose the paper presenters randomly from those who have presented the
# minimum number of times.
for contribution in ('papers', 'plots'):
    for group in (students, postdocs):
        mi = group[contribution].min()
        pool = list(group.query(contribution + ' == @mi').index)
        group.presenters[contribution[:-1]] = random.sample(pool, 1)[0]

# if we have someone who is meant to be presenting both types of
# contributions then keep randomizing the plot presenter choce until we get
# a valid combination (if possible)
max_tries = 100
n_tries = 0
#  import pdb
#  pdb.set_trace()
for group in (students, postdocs):
    while len(set(group.presenters.values())) < 2:
        mi = group["plots"].min()
        pool = list(group.query('plots == @mi').index)
        group.presenters["plot"] = random.sample(pool, 1)[0]
        n_tries+=1
        if n_tries == max_tries:
            warnings.warn("Failed to find unique paper + plot presenters for"
                          " the %s!" % group.name)
            break

# render the page
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')
with open('build/index.html', 'w') as fd:
    fd.write(template.render(postdoc_presenters=postdocs.presenters,
                             student_presenters=students.presenters))
