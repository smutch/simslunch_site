import warnings
import random
import yaml
import pandas as pd
import datetime
from scrape_doodle import scrape_doodle
from termcolor import colored
import numpy as np
import pickle

def simslunch_time(week=2):
    """http://stackoverflow.com/a/6558571"""
    today = datetime.date.today()
    weekday = 3  # 0 = Monday, 1=Tuesday, 2=Wednesday...
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0: # Target day already happened this week
        week+=1
    days_ahead +=7*(week-1)
    return today + datetime.timedelta(days_ahead)


def make_selection():

    # check the clock, give people time to visit the doodle polls
    # the selection can be done after 5pm every Thursday
    # AND BEFORE SUNDAY!!!
    now = datetime.datetime.now()
    today = datetime.date.today()
    days_ahead = today.weekday() -3
    if days_ahead < 0:
        days_ahead += 7
    tick_end = datetime.datetime(now.year, now.month, now.day-days_ahead, 17,0,0,0)
    
    if now < tick_end:
        print(colored("THIS IS NOT THE TIME!!!",'red'))
        #return

    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)

    # convert to a pandas dataframe
    members = pd.DataFrame.from_dict(members).T
    members.index.name = 'name'
    emails = members.email
    
    # cut down the members to just those who are available this coming week 
    print(colored("Unavailable list: %s"%members[members.available==0].index.tolist(),'red'))
    members = members[members.available==1]                                           
                                                                                   
    # the meeting is better off when less than 4 participants
    if len(members)<4:                                                                
       print(colored("not enough people","red"))                                     
       return                                                                        

    # Temporarily increment the contribution counts to include future volunteers
    doodle_poll = scrape_doodle("http://doodle.com/poll/g3idnd5gfg8ck2ze")
    next2_thursday = simslunch_time(week=2).strftime("%-m/%-d/%y")
    doodle_poll[doodle_poll=='q']=False      
    doodle_poll = doodle_poll.astype(np.bool)
    for name in doodle_poll.columns:
        for contribution in ('papers', 'plots'):
            try:
                members.loc[name][contribution] += np.count_nonzero(doodle_poll[name].loc[:, contribution[:-1]])
            except KeyError:
                print(name+' is not here')

    # pickle the doodle poll for later use
    with open("doodle_poll.pkl", "wb") as fd:
        pickle.dump(doodle_poll, fd)

    presenters = dict(paper = "", plot = "") 

    # select volunteers if there are any
    volunteers = {}
    for t in ('paper', 'plot'):
        volunteers[t] = list(doodle_poll.columns[doodle_poll.loc[next2_thursday, t]])
    for k, l in iter(volunteers.items()):
        if len(l)>0:
            presenters[k] = l                                 
            print(colored("Volunteered for "+k+" by "+str(l)[1:-1],'red')) 
        else:
            presenters[k] = []

    # selected presenters list
    with open('selected_presenters.yaml', 'r') as fd: 
        selected_presenters = yaml.load(fd)
        
    this_thursday = simslunch_time(week=0).strftime("%m/%d/%y")
    next_thursday = simslunch_time(week=1).strftime("%m/%d/%y")
    next2_thursday = simslunch_time(week=2).strftime("%m/%d/%y")

    # choose the paper presenters randomly from those who have presented the
    # minimum number of times.
    for contribution in ('papers', 'plots'):
        offset = 0
        count_min = members[contribution].min()
        count_max = members[contribution].max()
        diff = count_max - count_min
        while (len(presenters[contribution[:-1]])<2) and (offset<=diff):
            mi = count_min+offset
            # you want to exclude volunteers and selected people next_thursday
            pool = list(set(members.query(contribution + ' == @mi').index) - set(presenters['paper']) - set(presenters['plot']) - set(selected_presenters[next_thursday][contribution[:-1]].split(', ')))
            # SELECTION!!!
            presenters[contribution[:-1]] += random.sample(pool, min(len(pool),2-len(presenters[contribution[:-1]])))
            offset +=1

    selected_presenters.pop(this_thursday)
    selected_presenters[next2_thursday] = dict(paper = "", plot = "")
    for contribution in ('papers', 'plots'): 
        selected_presenters[next2_thursday][contribution[:-1]] = ', '.join(presenters[contribution[:-1]])

    # save the updated selected_presenters file to selected_presenters_tba.yaml
    # it will be mv-ed to selected_presenters.yaml, which will be mv-ed to selected_presenters.yaml.bak in the same time
    with open("selected_presenters_tba.yaml", "w") as fd:  
        yaml.safe_dump(selected_presenters, fd)            

    # show me the result
    print(colored('Next week (%s):\npapers:\t%s\nplots:\t%s\n'%(next_thursday,selected_presenters[next_thursday]['paper'], selected_presenters[next_thursday]['plot']),'red'))
    print(colored('2 weeks later (%s):\npapers:\t%s\nplots:\t%s\n'%(next2_thursday,selected_presenters[next2_thursday]['paper'], selected_presenters[next2_thursday]['plot']),'red'))

    # write emails
    f = open('email.bash','w')
    for contribution in ('paper', 'plot'):
        for name in selected_presenters[next_thursday][contribution].split(', '):
            context = 'Hi %s,\n\nPlease allow me to remind you that you are the speaker (for %s) for the simulation lunch meeting next week (%s). (http://smutch.github.io/simslunch_site/index.html)\n\nCheers,\nYuxiang'%(name, contribution, simslunch_time(week=1).strftime("%d/%B/%y"))
            f.write("mail -s '(Next Week) speaker on the simulation lunch meeting' %s <<< '%s'\n"%(emails[name], context))
        for name in selected_presenters[next2_thursday][contribution].split(', '):
            if name in volunteers[contribution]:
                context = 'Hi %s,\n\nYou volunteered to be the speaker (for %s) for the simulation lunch meeting to be held 2 weeks later (%s). (http://smutch.github.io/simslunch_site/index.html)\nPlease let me know if you do not want to present a %s:)\n\nCheers,\nYuxiang'%(name, contribution, simslunch_time(week=2).strftime("%d/%B/%y"),contribution)
            else:
                context = 'Hi %s,\n\nYou are selected to be the speaker (for %s) for the simulation lunch meeting to be held 2 weeks later (%s). (http://smutch.github.io/simslunch_site/index.html)\nPlease let me know if you do not want to present a %s:)\n\nCheers,\nYuxiang'%(name, contribution, simslunch_time(week=2).strftime("%d/%B/%y"),contribution)
            f.write("mail -s '(2 Weeks Later) speaker on the simulation lunch meeting' %s <<< '%s'\n"%(emails[name], context))
    f.close()
            
if __name__ == "__main__":
    make_selection()
