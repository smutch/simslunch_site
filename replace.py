import warnings
import sys
import random
import yaml
import pandas as pd
import datetime
from scrape_doodle import scrape_doodle
from termcolor import colored
import numpy as np
import pickle
from make_selection import simslunch_time

def replace(name):
    print(colored('%s is to be replaced.'%name,'red'))

    # read in the list of members and their presenting histories
    with open('members.yaml', 'r') as fd:
        members = yaml.load(fd)

    # convert to a pandas dataframe
    members = pd.DataFrame.from_dict(members).T
    members.index.name = 'name'
    emails = members.email
    
    # this guy is not available
    if name in members.index:
        members['available'][name] = 0
    else:
        print(colored('%s is not in our group!'%name,'red'))
        return

    this_thursday = simslunch_time(week=0).strftime("%m/%d/%y")  
    next_thursday = simslunch_time(week=1).strftime("%m/%d/%y")  
    next2_thursday = simslunch_time(week=2).strftime("%m/%d/%y") 

    # cut down the members to just those who are available this coming week 
    print(colored("Unavailable list: %s"%members[members.available==0].index.tolist(),'red'))
    members = members[members.available==1]                                           
                                                                                   
    if len(members)<5:                                                                
       print(colored("not enough people","red"))                                     
       return                                                                        

    # read in the selected selected_presenters                  
    with open('selected_presenters.yaml', 'r') as fd: 
        selected_presenters = yaml.load(fd)                    

    # find this is a paper or plot
    for contribution in ['papers','plots']:
        if name in selected_presenters[next2_thursday][contribution[:-1]]:
            reselect_contribution = contribution
            tmp = selected_presenters[next2_thursday][contribution[:-1]].split(', ')
            tmp.remove(name)
            selected_presenters[next2_thursday][contribution[:-1]] = tmp[0]

    # choose the paper selected_presenters randomly from those who have presented the
    # minimum number of times.
    offset = 0
    count_min = members[reselect_contribution].min()
    count_max = members[reselect_contribution].max()
    diff = count_max - count_min
    while offset<diff:
        mi = count_min+offset
        pool = list(set(members.query(reselect_contribution + ' == @mi').index) - set(selected_presenters[next2_thursday]['paper'].split(', ')) - set(selected_presenters[next2_thursday]['plot'].split(', ')) - set(selected_presenters[next_thursday][reselect_contribution[:-1]].split(', ')))
        if len(pool)<1:
            offset +=1
        else:
            reselected_name = random.sample(pool,1)[0] 
            selected_presenters[next2_thursday][reselect_contribution[:-1]] += ', %s'%reselected_name
            break

    with open("selected_presenters_tba.yaml", "w") as fd:  
        yaml.safe_dump(selected_presenters, fd)            

    print(colored('Next week (%s):\npapers:\t%s\nplots:\t%s\n'%(next_thursday,selected_presenters[next_thursday]['paper'], selected_presenters[next_thursday]['plot']),'red'))
    print(colored('2 weeks later (%s):\npapers:\t%s\nplots:\t%s\n'%(next2_thursday,selected_presenters[next2_thursday]['paper'], selected_presenters[next2_thursday]['plot']),'red'))

    f = open('email.bash','w')
    context = 'Hi %s,\n\nYou are selected to be the speaker (for %s) for the simulation lunch meeting to be held 2 weeks later (%s). (http://smutch.github.io/simslunch_site/index.html)\nPlease let me know if you do not want to present a %s:)\n\nCheers,\nYuxiang'%(reselected_name, reselect_contribution, simslunch_time(week=2).strftime("%d/%B/%y"),contribution)
    f.write("mail -s '(2 Weeks Later) speaker on the simulation lunch meeting' %s <<< '%s'\n"%(emails[reselected_name], context))
    f.close()
            
if __name__ == "__main__":
    if len(sys.argv)<2:
        print(colored("Who do you want to replace?",'red'))
    else:
        replace(sys.argv[1])
