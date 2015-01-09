# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 15:54:43 2014
Derived from previous particle tracking work by Manning, Muse, Cui, Warren.
This now generates an animation if requested.
This project lay out drifter track and the forcast track in latest three days,and forcast 
drifter track for two days finally. 
@author: bling
"""

import sys
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pytz
from track_functions import get_drifter,get_fvcom,get_roms,draw_basemap,distance,uniquecolors
from matplotlib import animation
st_run_time = datetime.now() # Caculate the time running the code with en_run_time 
######################### Option ##############################
drifter_ID = 140430701 #[140410704,140410706,140410707,140410708,140410709] 140410701]
# if raw data, use "drift_X.dat";if want to get drifter data in database, use "None"
INPUT_DATA = 'drift_X.dat' 
MODEL = 'FVCOM'              # 'FVCOM', 'ROMS' or 'BOTH'                  
GRID = 'massbay'            # '30yr', 'massbaya', 'GOM3a', 'GOM3' or 'massbay'
MODE = 'FORECAST'           # 'FORECAST' or 'HINDCAST'
DEPTH = -1.               # depth of drogue in meters
DAYS = 3                     # Length of time wanted in track
run_time = datetime(2015,1,4,0,0,0,0,pytz.UTC)
print "Drifter: %s track %d days"%(drifter_ID,DAYS)
########################## Extract points ##################################
dr_set={'lats':[],'lons':[]}  # collect points of Drifter
fc_set={'lats':[],'lons':[]}  # collect points of MODEL
d_file = open('dr_points.txt','w') # opens an output file for portion of drifters simulated
f_file = open('fc_points.txt','w') # opens an output file for modeled track
a0=int();a1=int();a2=int()  # use to record position of the marked points of the list
an0=str();an1=str();an2=str()  # record the start time of the marked points
a = [a0,a1,a2]; an = [an0,an1,an2]
for i in range(DAYS):    
    begin_time = run_time + timedelta(i)  # add one day with the looping 
    print '%dth day, start at %s'%((i+1),begin_time.strftime('%m/%d/%Y %H:%M'))
    drifter = get_drifter(drifter_ID, INPUT_DATA)
    dr_points = drifter.get_track(begin_time,1)
    dr_set['lons'].extend(dr_points['lon']); dr_set['lats'].extend(dr_points['lat'])
    for h in zip(dr_points['lat'],dr_points['lon']): d_file.write('%f,%f\n'%h)
    st_point = (dr_points['lon'][0],dr_points['lat'][0])
    start_time = dr_points['time'][0]  # start time of the MODEL
    end_time = start_time + timedelta(1)
    a[i] = len(dr_set['lats']); an[i] = start_time.strftime('%m/%d') # %H:%M
    print len(dr_points['lon']),an[i]
    if MODEL in ('FVCOM','BOTH'):
        get_obj = get_fvcom(GRID)
        url_fvcom = get_obj.get_url(start_time,end_time)
        point = get_obj.get_track(st_point[0],st_point[1],DEPTH,url_fvcom)
    if MODEL in ('ROMS', 'BOTH'):
        get_obj = get_roms()
        url_roms = get_obj.get_url(start_time, end_time)
        point = get_obj.get_track(st_point[0],st_point[1],DEPTH,url_roms)
    print len(point['lon'])
    n = len(dr_points['lat'])  # Quantity of one-day's drifter points
    #save the the same quantity of drifter
    fc_set['lons'].extend(point['lon'][:n]); fc_set['lats'].extend(point['lat'][:n])
    for h in zip(point['lat'],point['lon']): f_file.write('%f,%f\n'%h)
d_file.close()
'''forcast two days of the last drifter point.'''
start_time = dr_points['time'][-1]
print start_time 
end_time = start_time + timedelta(2)
an3 = start_time.strftime('%m/%d') # %H:%M
st_point = (dr_set['lons'][-1],dr_set['lats'][-1])  # Position of the last drifter point
if MODEL in ('FVCOM','BOTH'):
    get_obj = get_fvcom(GRID)
    url_fvcom = get_obj.get_url(start_time,end_time)
    point = get_obj.get_track(st_point[0],st_point[1],DEPTH,url_fvcom)
if MODEL in ('ROMS', 'BOTH'):
    get_obj = get_roms()
    url_roms = get_obj.get_url(start_time, end_time)
    point = get_obj.get_track(st_point[0],st_point[1],DEPTH,url_roms)
fc_set['lons'].extend(point['lon']); fc_set['lats'].extend(point['lat']) 
for h in zip(point['lat'],point['lon']): f_file.write('%f,%f\n'%h)
f_file.close()
#################### Plotting ##########################
points = {'lats':[],'lons':[]}  # collect all points we've gained
points['lats'].extend(dr_set['lats']); points['lons'].extend(dr_set['lons'])
points['lats'].extend(fc_set['lats']); points['lons'].extend(fc_set['lons'])
fig = plt.figure()
ax = fig.add_subplot(111)
draw_basemap(fig, ax, points)
ax.plot(dr_set['lons'][0],dr_set['lats'][0],'c.',markersize=16) #,label='Startpoint'
ax.annotate(an[0], xy=(dr_set['lons'][0]+0.005,dr_set['lats'][0]+0.005),fontsize=6,
            xytext=(dr_set['lons'][0]+0.03,dr_set['lats'][0]+0.03),
            arrowprops=dict(arrowstyle="wedge")) #facecolor=colors[i]
#colors=uniquecolors(len(points['lats'])) #config colors
plt.title('Drifter: {0} {1} track'.format(drifter_ID,MODE))
################
def animate(n):  # the function of the animation
    #ax.cla()
    ax.plot(fc_set['lons'][n],fc_set['lats'][n],'ro',markersize=4,label='%s'%MODE) #'%d'%n 
    if n<len(dr_set['lons']):
        po = (dr_set['lons'][n]+0.005,dr_set['lats'][n]+0.005)
        pt = (dr_set['lons'][n]+0.03,dr_set['lats'][n]+0.03)
        if n==(a[0]-1):
            ax.annotate(an[1],xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
        if n==(a[1]-1):
            ax.annotate(an[2],xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
        if n==(a[2]-1):
            ax.annotate(an3,xy=po,xytext=pt,fontsize=6,arrowprops=dict(arrowstyle="wedge"))
        ax.plot(dr_set['lons'][n],dr_set['lats'][n],'bo',markersize=6,label='drifter')   
anim = animation.FuncAnimation(fig, animate, frames=len(fc_set['lons']), interval=50)
plt.legend(loc='lower right',fontsize=10)
###################################################
en_run_time = datetime.now()
print 'Take '+str(en_run_time-st_run_time)+' run the code. End at '+str(en_run_time)
#anim.save('%s multi-days_demo.mp4'%drifter_ID, writer='mencoder',fps=10,dpi=200) 
anim.save('%s-demo_%s.gif'%(drifter_ID,en_run_time.strftime("%d-DEC-%H:%M")),
          writer='imagemagick',fps=10,dpi=100) #ffmpeg,imagemagick,mencoder fps=20
plt.show()