
import os
from os.path import expanduser
home = expanduser("~")



import sys
for i in range(len(sys.path)):
    if 'er/Documents' in sys.path[i]:
        sys.path.remove(sys.path[i])#[i]
        break

import copy
import glob
import os
import time

import gym
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable
from torch.utils.data.sampler import BatchSampler, SubsetRandomSampler


sys.path.insert(0, '../baselines/')
sys.path.insert(0, '../baselines/baselines/common/vec_env')
from subproc_vec_env import SubprocVecEnv

sys.path.insert(0, './utils/')
from envs import make_env, make_env_monitor, make_env_basic


# from agent_modular2 import a2c
# from agent_modular2 import ppo
# from agent_modular2 import a2c_minibatch
# from agent_modular2 import a2c_list_rollout
# from agent_modular2 import a2c_with_var

from a2c_agents import a2c



from train_utils import do_vid, do_gifs, do_params, do_ls, update_ls_plot, save_params_v2, load_params_v2

sys.path.insert(0, './visualizations/')
from make_plots import make_plots

import argparse
import json
import subprocess








def train(model_dict):

    def update_current_state(current_state, state, channels):
        # current_state: [processes, channels*stack, height, width]
        state = torch.from_numpy(state).float()  # (processes, channels, height, width)
        # if num_stack > 1:
        #first stack*channel-channel frames = last stack*channel-channel , so slide them forward
        current_state[:, :-channels] = current_state[:, channels:] 
        current_state[:, -channels:] = state #last frame is now the new one

        return current_state


    def update_rewards(reward, done, final_rewards, episode_rewards, current_state):
        # Reward, Done: [P], [P]
        # final_rewards, episode_rewards: [P,1]. [P,1]
        # current_state: [P,C*S,H,W]
        reward = torch.from_numpy(np.expand_dims(np.stack(reward), 1)).float() #[P,1]
        episode_rewards += reward #keeps track of current episode cumulative reward
        masks = torch.FloatTensor([[0.0] if done_ else [1.0] for done_ in done]) #[P,1]
        final_rewards *= masks #erase the ones that are done
        final_rewards += (1 - masks) * episode_rewards  #set it to the cumulative episode reward
        episode_rewards *= masks #erase the done ones
        masks = masks.type(dtype) #cuda
        if current_state.dim() == 4:  # if state is a frame/image
            current_state *= masks.unsqueeze(2).unsqueeze(2)  #[P,1,1,1]
        else:
            current_state *= masks   #restart the done ones, by setting the state to zero
        return reward, masks, final_rewards, episode_rewards, current_state



    num_frames = model_dict['num_frames']
    cuda = model_dict['cuda']
    which_gpu = model_dict['which_gpu']
    num_steps = model_dict['num_steps']
    num_processes = model_dict['num_processes']
    seed = model_dict['seed']
    env_name = model_dict['env']
    save_dir = model_dict['save_to']
    num_stack = model_dict['num_stack']
    algo = model_dict['algo']
    save_interval = model_dict['save_interval']
    log_interval = model_dict['log_interval']

    save_params = model_dict['save_params']
    vid_ = model_dict['vid_']
    gif_ = model_dict['gif_']
    ls_ = model_dict['ls_']

    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['CUDA_VISIBLE_DEVICES'] = str(which_gpu)

    if cuda:
        torch.cuda.manual_seed(seed)
        dtype = torch.cuda.FloatTensor
        model_dict['dtype']=dtype
    else:
        torch.manual_seed(seed)
        dtype = torch.FloatTensor
        model_dict['dtype']=dtype


    # Create environments
    print (num_processes, 'processes')
    monitor_rewards_dir = os.path.join(save_dir, 'monitor_rewards')
    if not os.path.exists(monitor_rewards_dir):
        os.makedirs(monitor_rewards_dir)
        print ('Made dir', monitor_rewards_dir) 
    envs = SubprocVecEnv([make_env(env_name, seed, i, monitor_rewards_dir) for i in range(num_processes)])


    if vid_:
        print ('env for video')
        envs_video = make_env_monitor(env_name, save_dir)

    if gif_:
        print ('env for gif')
        envs_gif = make_env_basic(env_name)

    if ls_:
        print ('env for ls')
        envs_ls = make_env_basic(env_name)

    obs_shape = envs.observation_space.shape  # (channels, height, width)
    obs_shape = (obs_shape[0] * num_stack, *obs_shape[1:])  # (channels*stack, height, width)
    shape_dim0 = envs.observation_space.shape[0]  #channels

    model_dict['obs_shape']=obs_shape
    model_dict['shape_dim0']=shape_dim0



    # Create agent
    if algo == 'a2c':
        agent = a2c(envs, model_dict)
        print ('init a2c agent')
    elif algo == 'ppo':
        agent = ppo(envs, model_dict)
        print ('init ppo agent')
    elif algo == 'a2c_minibatch':
        agent = a2c_minibatch(envs, model_dict)
        print ('init a2c_minibatch agent')
    elif algo == 'a2c_list_rollout':
        agent = a2c_list_rollout(envs, model_dict)
        print ('init a2c_list_rollout agent')
    elif algo == 'a2c_with_var':
        agent = a2c_with_var(envs, model_dict)
        print ('init a2c_with_var agent')
    # elif algo == 'a2c_bin_mask':
    #     agent = a2c_with_var(envs, model_dict)
    #     print ('init a2c_with_var agent')
    # agent = model_dict['agent'](envs, model_dict)

    #Load model
    if model_dict['load_params']:
        # agent.actor_critic = torch.load(os.path.join(args.load_path))
        # agent.actor_critic = torch.load(args.load_path).cuda()
        
        # print ('loaded ', args.load_path)

        if model_dict['load_number'] == 3:
            load_params_v2(home+'/Documents/tmp/confirm_works_1_withsaving/PongNoFrameskip-v4/a2c/seed0/', agent, 3000160, model_dict)

        elif model_dict['load_number'] == 6:
            load_params_v2(home+'/Documents/tmp/confirm_works_1_withsaving/PongNoFrameskip-v4/a2c/seed0/', agent, 6000160, model_dict)
        elif model_dict['load_number'] == 9:
            load_params_v2(home+'/Documents/tmp/confirm_works_1_withsaving/PongNoFrameskip-v4/a2c/seed0/', agent, 9000160, model_dict)

        # else:
        #     load_params_v2(home+'/Documents/tmp/confirm_works_1_withsaving/PongNoFrameskip-v4/a2c/seed0/', agent, 8000160, model_dict)
        else:
            PROBLEM















    # Init state
    state = envs.reset()  # (processes, channels, height, width)
    current_state = torch.zeros(num_processes, *obs_shape)  # (processes, channels*stack, height, width)
    current_state = update_current_state(current_state, state, shape_dim0).type(dtype) #add the new frame, remove oldest
    agent.insert_first_state(current_state) #storage has states: (num_steps + 1, num_processes, *obs_shape), set first step 

    # These are used to compute average rewards for all processes.
    episode_rewards = torch.zeros([num_processes, 1]) #keeps track of current episode cumulative reward
    final_rewards = torch.zeros([num_processes, 1])

    num_updates = int(num_frames) // num_steps // num_processes
    save_interval_num_updates = int(save_interval /num_processes/num_steps)

    #Begin training
    # count =0
    start = time.time()
    start2 = time.time()
    for j in range(num_updates):
        for step in range(num_steps):

            # Act, [P,1], [P], [P,1], [P]
            # value, action = agent.act(Variable(agent.rollouts.states[step], volatile=True))
            value, action, action_log_probs, dist_entropy = agent.act(Variable(agent.rollouts.states[step]))#, volatile=True))
            # print (action_log_probs.size())
            # print (dist_entropy.size())

            cpu_actions = action.data.squeeze(1).cpu().numpy() #[P]
            # cpu_actions = action.data.cpu().numpy() #[P]
            # print (actions.size())

            # Step, S:[P,C,H,W], R:[P], D:[P]
            state, reward, done, info = envs.step(cpu_actions) 

            # Record rewards and update state
            reward, masks, final_rewards, episode_rewards, current_state = update_rewards(reward, done, final_rewards, episode_rewards, current_state)
            current_state = update_current_state(current_state, state, shape_dim0)

            # Agent record step
            # agent.insert_data(step, current_state, action.data, value.data, reward, masks, action_log_probs.data, dist_entropy.data)
            agent.insert_data(step, current_state, action.data, value, reward, masks, action_log_probs, dist_entropy) #, done)





        #Optimize agent
        agent.update()  #agent.update(j,num_updates)
        agent.insert_first_state(agent.rollouts.states[-1])


        # print ('save_interval_num_updates', save_interval_num_updates)
        # print ('num_updates', num_updates)
        # print ('j', j)
        total_num_steps = (j + 1) * num_processes * num_steps
        
        # if total_num_steps % save_interval == 0 and save_dir != "":
        if j % save_interval_num_updates == 0 and save_dir != "" and j != 0:

            #Save model
            if save_params:
                do_params(save_dir, agent, total_num_steps, model_dict)
                save_params_v2(save_dir, agent, total_num_steps, model_dict)
            #make video
            if vid_:
                do_vid(envs_video, update_current_state, shape_dim0, dtype, agent, model_dict, total_num_steps)
            #make gif
            if gif_:
                do_gifs(envs_gif, agent, model_dict, update_current_state, update_rewards, total_num_steps)


        #Print updates
        if j % log_interval == 0:# and j!=0:
            end = time.time()

            to_print_info_string = "{}, {}, {:.1f}/{:.1f}/{:.1f}/{:.1f}, {}, {:.1f}, {:.1f}".format(j, total_num_steps,
                                       final_rewards.min(),
                                       final_rewards.median(),
                                       final_rewards.mean(),
                                       final_rewards.max(),
                                       int(total_num_steps / (end - start)),
                                       end - start,
                                       end - start2)
            print(to_print_info_string) 
            start2 = time.time()



            to_print_legend_string = "Upts, n_timesteps, min/med/mean/max, FPS, Time"
            if j % (log_interval*30) == 0:
            
                if ls_:
                    do_ls(envs_ls, agent, model_dict, total_num_steps, update_current_state, update_rewards)
                # print("Upts, n_timesteps, min/med/mean/max, FPS, Time, Plot updated, LS updated")
                # print(to_print_info_string + ' LS recorded')#, agent.current_lr)
                # else:
                #update plots
                try:
                    if ls_:
                        update_ls_plot(model_dict)
                    make_plots(model_dict)
                    print(to_print_legend_string + " Plot updated")
                except:
                    raise #pass
                    print(to_print_legend_string)



    try:
        make_plots(model_dict)
    except:
        print ()
        # pass #raise





if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--m')
    args = parser.parse_args()

    #Load model dict 
    with open(args.m, 'r') as infile:
        model_dict = json.load(infile)


    train(model_dict)




