# this script needs a git clone of https://github.com/helium/denylist
# insert the .git directory in GIT_DIR

#    MIT LICENSE
#    Copyright (c) 2022 Tom Tobback
#    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
#    to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
#    and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#    IN THE SOFTWARE.

import os
import subprocess
from operator import itemgetter
import matplotlib.pyplot as plt

GIT_DIR = "/home/tom/CODE/lorawan/helium/github-helium-denylist/denylist"

print("=================================================")
print("ANALYSE DENYLIST VIA GIT CLONE")
print("=================================================")

print("looking in folder", GIT_DIR)
os.chdir(GIT_DIR)

print("updating repo with git pull..")
os.system("git pull")

# get output of git log into a string
print("checking all commits of denylist")
commits_str = subprocess.check_output("git log --pretty=format:\"%h,%ad,%s\" --date=short denylist.csv", shell=True).decode("utf-8")

# initialise list for commits
commit_list = []
# process csv string into lines and split into fields
commit_lines = commits_str.splitlines()
for line in commit_lines:
    line_fields = line.split(",")
    #print(line_fields)
    commit_list.append(line_fields)

sorted_commit_list = sorted(commit_list, key=itemgetter(1))
        
# initialise list for denylists and counts
denylist_list = []
denylist_counts_list = []
for index, commit in enumerate(sorted_commit_list):
    this_denylist_str = subprocess.check_output("git show " + commit[0] + ":denylist.csv", shell=True).decode("utf-8")
    this_denylist = this_denylist_str.splitlines()
    # check difference with previous list
    new_count = 0
    old_count = 0
    removed_count = 0
    if index > 1:
        previous_denylist = denylist_list[index-1]
        for hotspot in this_denylist:
            if hotspot not in previous_denylist:
                new_count += 1
        #print("new:", new_count)
        # we have the new count, so the rest of this list is old count
        old_count = len(this_denylist) - new_count
        # to find out the removed count, we look at the previous list
        removed_count = len(previous_denylist) - old_count
    # add this list to list of lists
    denylist_list.append(this_denylist)
    this_commit_dict = {}
    this_commit_dict['hash'] = commit[0]
    this_commit_dict['date'] = commit[1]    
    this_commit_dict['name'] = commit[2]    
    this_commit_dict['size'] = len(this_denylist)
    this_commit_dict['new'] = new_count
    this_commit_dict['old'] = old_count
    this_commit_dict['removed'] = removed_count
    print(this_commit_dict['hash'], this_commit_dict['date'], 
    "\tsize:", this_commit_dict['size'],
    "\tnew:", this_commit_dict['new'],
    "\told:", this_commit_dict['old'],
    "\tremoved:", this_commit_dict['removed'],
    "\tname:", this_commit_dict['name'])  
    denylist_counts_list.append(this_commit_dict)


# plot bar graph
plt.figure(num="Helium denylist github commits")    
dates = []
sizes = []
news = []
olds = []
removeds = []
print("=================================================")
print("markdown friendly format")
print("=================================================")
for denylist_count in denylist_counts_list:
    dates.append(denylist_count['date'])
    sizes.append(denylist_count['size'])
    news.append(denylist_count['new'])
    olds.append(denylist_count['old'])        
    removeds.append(-denylist_count['removed']) # to show negative bar
    # print in markdown friendly format
    print("|", denylist_count['hash'], "|", denylist_count['date'], 
    "|",denylist_count['size'], "|",denylist_count['new'], "|",
    denylist_count['old'], "|",denylist_count['removed'], "|",
    denylist_count['name'], "|")
plt.grid(axis='y', alpha=0.3, linestyle='dashed')
# add bars
plt.bar(dates, olds, color='darkblue', width= 0.5)
plt.bar(dates, news, bottom=olds, color='royalblue', width = 0.5) # stacked
plt.bar(dates, removeds, color='violet', width = 0.5) # negative
plt.xlabel("commit dates")
plt.ylabel("hotspot counts")
plt.gca().set_xticklabels(dates, rotation = 30)
#plt.gca().set_xticklabels(dates)
# format y label with 1,000 separator
y_values = plt.gca().get_yticks()
plt.gca().set_yticklabels(['{:,.0f}'.format(y) for y in y_values])
plt.title("Helium denylist github commits")
plt.legend(labels=["Previous", "Additions", "Removals"])

# print size labels on top of bars
# look for max size to set the ylim with margin for size labels
max_size = 0
for x, size in enumerate(sizes):
    plt.text(x, size + 1000, f"{size:,d}", color='blue', ha='center')
    if size > max_size:
        max_size = size
plt.ylim(top=max_size + 5000)
plt.axhline(y=0, color='black', linewidth=0.5)
plt.show()    

print("=================================================")

