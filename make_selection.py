import warnings
import random
import yaml
import pandas as pd

# read in the list of members and their presenting histories
with open('members.yaml', 'r') as fd:
    members = yaml.load(fd)

# read in last week's presenters and increment
try:
    with open("selected_presenters.yaml", "r") as fd:
        last_presenters = yaml.load(fd)
    for member_type in iter(last_presenters.values()):
        for presentation, name in iter(member_type.items()):
            members[name][presentation+'s'] += 1
except FileNotFoundError:
    pass

# write out the updated members list
with open('members.yaml', 'w') as fd:
    yaml.safe_dump(members, fd)

# convert to a pandas dataframe
members = pd.DataFrame.from_dict(members).T
members.available.fillna(True, inplace=True)
members.index.name = 'name'

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

# write the presenters to a file
presenters = dict(postdocs = postdocs.presenters,
                  students = students.presenters)
with open("selected_presenters.yaml", "w") as fd:
    yaml.safe_dump(presenters, fd)
