



import os
from os.path import expanduser
home = expanduser("~")

import json
import subprocess

import model_specs as ms

def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print ('Made dir', path) 


def print_stuff():
    print ()
    print ('Exp Name:', exp_name)
    print (envs)
    print ([m['name'] for m in models_list])
    # print ('Noframskip', noFrameSkip)
    print ('which_gpu', which_gpu)
    print ('Iters', iters)
    print ('Num_frames', num_frames)
    print ('num_processes', num_processes)
    print ()
    print ('save_params', save_params)
    print ('vid_', vid_)
    print ('gif_', gif_)
    print ('ls_', ls_)
    print ('vae_', vae_)
    print ('grad_var_', grad_var_)
    print ('save_interval', save_interval)
    print ()
    print ()









# Experiment 
##################
exp_name = 'testing_dqn_pong'
envs = ['Pong'] # ['Breakout'] # ['MontezumaRevenge']  ## ['Kangaroo', 'Freeway', #[ ] ## 'Seaquest', #['Kangaroo']  , , 'Enduro',   #['Pong']#['MontezumaRevenge'] #['Enduro']['Seaquest']   # # ## # , ,  ### # ###,,,,, 'BeamRider', 'Alien', 
            # 'Amidar','Assault', 'Freeway',
            # ,'Venture','Zaxxon','PrivateEye', 'Gopher']
models_list = [ms.dqn] #[ms.a2c_adam] #_1step] #, ms.a2c_adam_10step, ms.a2c_adam_50step] #  [ms.a2c_over, ms.a2c_under, ms.a2c_adam] # [] #[ms.a2c_adam] # ## [ms.a2c_adam_1] #  # #  # #, #[ms.a2c_traj_action_mask] #  # #,   #[]  # # # # #[ms.a2c_with_var]  # #[ms.a2c_sgd]#  #[ms.a2c_list]  #  #[mf.a2c_dropout]  mf.ppo_linear] # [mf.ppo_v1]# [mf.a2c_long] 
which_gpu = 1

num_frames = 10e6
iters = 1
seed_offset = 0
noFrameSkip = True
num_processes= 1#2 #10 # 32


save_interval= 3e5 #save model params and videos and gifs
save_params = 0
vid_ = 0
gif_ = 0
ls_ = 0
vae_ = 0
explore_ = 0
grad_var_ = 0
code_location = os.path.dirname(os.path.realpath(__file__))
#####################
























exp_path = home + '/Documents/tmp/' + exp_name+'/'

make_dir(exp_path)

if noFrameSkip:
    envs = [x+'NoFrameskip-v4' for x in envs]
print_stuff()

for env in envs:

    env_path = exp_path +env
    make_dir(env_path)

    for model_dict in models_list:

        model_path = env_path +'/'+ model_dict['name']
        make_dir(model_path)

        for iter_i in range(seed_offset,seed_offset+iters):

            iter_path = model_path +'/'+ 'seed'+str(iter_i)
            make_dir(iter_path)

            model_dict['exp_name'] = exp_name
            model_dict['exp_path'] = exp_path
            model_dict['seed']=iter_i
            model_dict['save_to']=iter_path
            model_dict['num_frames']=num_frames
            model_dict['env'] = env
            model_dict['cuda'] = True
            model_dict['which_gpu'] = which_gpu
            model_dict['save_interval'] = save_interval
            model_dict['num_processes'] = num_processes
            model_dict['save_params'] = save_params 
            model_dict['vid_'] = vid_
            model_dict['gif_'] = gif_
            model_dict['ls_'] = ls_
            model_dict['vae_'] = vae_
            model_dict['explore_'] = explore_
            model_dict['grad_var_'] = grad_var_

            print (env, model_dict['name'], iter_i)

            #write to json
            json_path = iter_path+'/model_dict.json'
            with open(json_path, 'w') as outfile:
                json.dump(model_dict, outfile,sort_keys=True, indent=4)

            #train model
            # subprocess.call("(cd "+code_location+" && python train_explore_exploit.py --m {})".format(json_path), shell=True) 
            subprocess.call("(cd "+code_location+" && python train4.py --m {})".format(json_path), shell=True) 
            print('')

    print_stuff()

print ('Done.')






#ENVIRONMENT LIST

# Alien
# Amidar
# Assault
# Asterix
# Asteroids
# Atlantis
# BankHeist
# BattleZone
# BeamRider
# Bowling
# Boxing
# Breakout
# Centipede
# ChopperCommand
# CrazyClimber
# DemonAttack
# DoubleDunk
# Enduro
# FishingDerby
# Freeway
# Frostbite
# Gopher
# Gravitar
# IceHockey
# Jamesbond
# Kangaroo
# Skipping
# Krull
# KungFuMaster
# MontezumaRevenge
# MsPacman
# NameThisGame
# Pitfall
# Pong
# PrivateEye
# Qbert
# Riverraid
# RoadRunner
# Robotank
# Seaquest
# SpaceInvaders
# StarGunner
# Tennis
# TimePilot
# Tutankham
# UpNDown
# Venture
# VideoPinball
# WizardOfWor
# Zaxxon





