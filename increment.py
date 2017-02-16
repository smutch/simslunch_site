import yaml
from make_selection import simslunch_time

def increment():
    # read in this week's presenters
    with open('selected_presenters.yaml', 'r') as fd:
        presenters = yaml.load(fd)
    this_week = simslunch_time(0).strftime("%m/%d/%y")
    presenters = presenters[this_week]

    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)

    # increment the presenter counters
    for presentation in ['papers', 'plots']:
        for name in (presenters[presentation[:-1]]).split(', '):
             members[name][presentation] +=1

    # write out the updated members list
    with open('members.yaml', 'w') as fd:
        yaml.safe_dump(members, fd)

if __name__ == "__main__":
    increment()
