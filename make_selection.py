import warnings
import random
import yaml
import pandas as pd
from scrape_doodle import scrape_doodle
import numpy as np

# read in the list of members and their presenting histories
with open('members.yaml', 'r') as fd:
    members = yaml.load(fd)

# convert to a pandas dataframe
members = pd.DataFrame.from_dict(members).T
members.index.name = 'name'

# cut down the members to just those who are available this coming week and
# split by type
try:
    members.available.fillna(True, inplace=True)
    members = members.query('available')
except AttributeError:
    pass

# Temporarily increment the contribution counts to include future volunteers
volunteers, doodle_poll = scrape_doodle()
for name in doodle_poll.columns:
    for contribution in ('papers', 'plots'):
        members.loc[name][contribution] += np.count_nonzero(doodle_poll[name].loc[:, contribution[:-1]])

# Set up the dicts for storing the selection information
postdocs = members.query('type == "postdoc"')
postdocs.name = "postdocs"
postdocs.presenters = dict(
    paper = "",
    plot = ""
)
postdocs.volunteered = dict(
    paper = False,
    plot = False,
)
students = members.query('type == "student"')
students.name = "students"
students.presenters = postdocs.presenters.copy()
students.volunteered = postdocs.volunteered.copy()

# select volunteers if there are any
for k, l in iter(volunteers.items()):
    for v in l:
        vgroup = None
        for group in (postdocs, students):
            if v in group.index and group.volunteered[k] is False:
                vgroup = group
                break
        if vgroup is None:
            for group in (postdocs, students):
                if not group.volunteered[k]:
                    vgroup = group
                    break
        group.presenters[k] = v
        group.volunteered[k] = True

# choose the paper presenters randomly from those who have presented the
# minimum number of times.
for contribution in ('papers', 'plots'):
    for group in (students, postdocs):
        if not group.volunteered[contribution[:-1]]:
            mi = group[contribution].min()
            pool = list(group.query(contribution + ' == @mi').index)
            group.presenters[contribution[:-1]] = random.sample(pool, 1)[0]

            # if we have someone who is meant to be presenting both types of
            # contributions then keep randomizing until we get
            # a valid combination (if possible)
            max_tries = 100
            n_tries = 0
            while len(set(group.presenters.values())) < 2:
                try:
                    group.presenters[contribution[:-1]] = random.sample(pool, 1)[0]
                except ValueError:
                    n_tries = max_tries
                n_tries+=1
                if n_tries >= max_tries:
                    mi += 1
                    pool = list(group.query(contribution + ' == @mi').index)
                    n_tries = 0

# write the presenters to a file
presenters = dict(postdocs = postdocs.presenters,
                  students = students.presenters)
with open("selected_presenters.yaml", "w") as fd:
    yaml.safe_dump(presenters, fd)
