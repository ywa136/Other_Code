

import numpy as np
import tensorflow as tf
import pickle
import math 

from os.path import expanduser
home = expanduser("~")

# # from VAE_mnist import VAE
# from VAE_mnist2 import VAE
# # from IWAE_mnist import IWAE
# from IWAE_mnist2 import IWAE

# from NQAE_mnist import NQAE


from autoencoders2 import VAE as VAE1
# from autoencoders import IWAE as IWAE1
# from autoencoders import VAE_MoG as VAE_MoG

'''
This is trying to reproduce the results of the IWAE paper 
'''



#########################################
#Load MNIST
#########################################

# import gzip
# with gzip.open('mnist.pkl.gz', 'rb') as f:

#Mac
# with open(home+ '/Documents/MNIST_data/mnist.pkl', 'rb') as f:

#Boltzmann
# with open(home+ '/data/mnist.pkl', 'rb') as f:
with open(home+ '/data/binarized_mnist.pkl', 'rb') as f:
	train_set, valid_set, test_set = pickle.load(f)

#No labels for the binarized mnist
# train_x, train_y = train_set
# valid_x, valid_y = valid_set
# test_x, test_y = test_set
train_x = train_set
valid_x = valid_set
test_x = test_set
# train_y = []
# valid_y = []
# test_y = []

print 'Train'
print train_x.shape
# print train_y.shape
print "Valid"
print valid_x.shape
# print valid_y.shape
print 'Test'
print test_x.shape
# print test_y.shape

#########################################
#Train VAE and IWAE
#########################################
# timelimit = 500
f_height=28
f_width=28
batch_size = 20
n_particles = 1

network_architecture = \
    dict(n_hidden_recog_1=200, # 1st layer encoder neurons
         n_hidden_recog_2=200, # 2nd layer encoder neurons
         n_hidden_gener_1=200, # 1st layer decoder neurons
         n_hidden_gener_2=200, # 2nd layer decoder neurons
         n_input=f_height*f_width, # 784 image
         n_z=50)  # dimensionality of latent space


# network_architecture_for_NQAE = \
#     dict(n_hidden_recog_1=200, # 1st layer encoder neurons
#          n_hidden_recog_2=200, # 2nd layer encoder neurons
#          n_hidden_recog_3=200,
#          n_hidden_gener_1=200, # 1st layer decoder neurons
#          n_hidden_gener_2=200, # 2nd layer decoder neurons
#          n_input=f_height*f_width, # 784 image
#          n_z=50,
#          rnn_state_size=10)  # dimensionality of latent space

# #mac
# print 'Training NQAE'
# nqae = NQAE(network_architecture_for_NQAE, transfer_fct=tf.tanh, learning_rate=0.001, batch_size=batch_size, n_particles=n_particles)
# nqae.train(train_x=train_x, train_y=train_y, timelimit=timelimit, max_steps=99999, display_step=50, path_to_load_variables='', path_to_save_variables=home+ '/Documents/tmp/quae.ckpt')

# print 'Training VAE'
# vae = VAE(network_architecture, transfer_fct=tf.tanh, learning_rate=0.001, batch_size=batch_size, n_particles=n_particles)
# vae.train(train_x=train_x, train_y=train_y, timelimit=timelimit, max_steps=99999, display_step=50, path_to_load_variables='', path_to_save_variables=home+ '/Documents/tmp/vae.ckpt')

# print 'Training IWAE'
# iwae = IWAE(network_architecture, transfer_fct=tf.tanh, learning_rate=0.001, batch_size=batch_size, n_particles=n_particles)
# iwae.train(train_x=train_x, train_y=train_y, timelimit=timelimit, max_steps=99999, display_step=50, path_to_load_variables='', path_to_save_variables=home+ '/Documents/tmp/iwae.ckpt')

#boltzmann
# print 'Training NQAE'
# nqae = NQAE(network_architecture_for_NQAE, transfer_fct=tf.tanh, learning_rate=0.001, batch_size=batch_size, n_particles=n_particles)
# nqae.train(train_x=train_x, train_y=train_y, timelimit=timelimit, max_steps=99999, display_step=50, path_to_load_variables='', path_to_save_variables=home+ '/data/quae3.ckpt')

# print 'Training VAE'
# vae = VAE(network_architecture, transfer_fct=tf.tanh, learning_rate=0.0001, batch_size=batch_size, n_particles=n_particles)
# vae.train(train_x=train_x, valid_x=valid_x, timelimit=timelimit, max_steps=99999, display_step=100, valid_step=500, path_to_load_variables=home+ '/data/vae5.ckpt', path_to_save_variables=home+ '/data/vae3.ckpt')

# print 'Training IWAE'
# iwae = IWAE(network_architecture, transfer_fct=tf.tanh, learning_rate=0.001, batch_size=batch_size, n_particles=n_particles)
# iwae.train(train_x=train_x, train_y=train_y, timelimit=timelimit, max_steps=99999, display_step=50, path_to_load_variables=home+ '/data/iwae3.ckpt', path_to_save_variables='')



print 'Training VAE'
vae = VAE1(network_architecture, transfer_fct=tf.tanh, learning_rate=0.001, batch_size=batch_size, n_particles=n_particles)
# vae.train(train_x=train_x, valid_x=valid_x, timelimit=timelimit, max_steps=99999, display_step=100, valid_step=1000, path_to_load_variables='', path_to_save_variables=home+ '/data/vae1.ckpt')


#USE THIS TO TRAIN LIKE IWAE PAPER
# vae.train2(train_x=train_x, valid_x=valid_x, display_step=1000, path_to_load_variables='', path_to_save_variables=home+ '/data/vae_stage_7_5.ckpt', starting_stage=0)


# generation = vae.generate(path_to_load_variables=home+'/data/vae_stage_7_2.ckpt')
# print generation.shape
# with open(home+ '/data/generated_image.pkl', 'wb') as f:
#     pickle.dump([generation], f)

x, x_mean = vae.reconstruct(path_to_load_variables=home+'/data/vae_stage_7_2.ckpt', train_x=train_x)
print x_mean.shape
with open(home+ '/data/reconstructed_image.pkl', 'wb') as f:
    pickle.dump([x, x_mean], f)
print 'saved reconstruction'


# iwae_elbo = vae.evaluate2(datapoints=test_x[:1000], n_samples=5000, path_to_load_variables=home+ '/data/vae_stage_7_2.ckpt')
# print 'iwae elbo of validation', iwae_elbo

# iwae_elbo = vae.evaluate(datapoints=test_x, n_samples=n_particles, n_datapoints=None, path_to_load_variables=home+ '/data/vae_stage_7_2.ckpt', load_vars=True)
# print 'iwae elbo of validation', iwae_elbo


# print 'Training IWAE'
# iwae = IWAE1(network_architecture, transfer_fct=tf.tanh, learning_rate=0.001, batch_size=batch_size, n_particles=n_particles)
# iwae.train(train_x=train_x, valid_x=None, timelimit=timelimit, max_steps=99999, display_step=100, valid_step=500, path_to_load_variables='', path_to_save_variables='')

# print 'Training VAE_MoG'
# vae = VAE_MoG(network_architecture, transfer_fct=tf.tanh, learning_rate=0.001, batch_size=batch_size, n_particles=n_particles)
# vae.train(train_x=train_x, valid_x=valid_x, timelimit=timelimit, max_steps=99999, display_step=100, valid_step=500, path_to_load_variables='', path_to_save_variables='')


# #########################################
# #Sample 5000 times from them
# #Get log likelihood of the test set
# #########################################
# print 'Negative Log Likelihood'

# print 'vae means'
# x_means_VAE = []
# for i in range(5000/batch_size):
# 	generation = vae.generate()
# 	for j in range(len(generation)):
# 		x_means_VAE.append(generation[j])

# print 'iwae means'
# x_means_IWAE = []
# for i in range(5000/batch_size):
# 	generation = iwae.generate()
# 	for j in range(len(generation)):
# 		x_means_IWAE.append(generation[j])

# print 'nqae means'
# x_means_NQAE = []
# for i in range(5000/batch_size):
# 	generation = nqae.generate()
# 	for j in range(len(generation)):
# 		x_means_NQAE.append(generation[j])

# def neg_log_likelihood(test_data, means):

# 	neg_log_like = 0
# 	for i in range(len(test_data)):
# 		if i % 50 == 0:
# 			print i
# 		for j in range(len(means)):

# 			a = test_data[i] * np.log(means[j])
# 			b = (1-test_data[i]) * np.log(1- means[j])
# 			c = a + b
# 			d = np.sum(c) #over dimensions
# 			neg_log_like += d

# 	return (-neg_log_like / len(test_data)) / len(means)


# print 'VAE', neg_log_likelihood(test_x, x_means_VAE)
# print 'IWAE', neg_log_likelihood(test_x, x_means_IWAE)
# print 'NQAE', neg_log_likelihood(test_x, x_means_NQAE)


# #########################################
# #Visualize generated data
# #########################################
# import matplotlib.cm as cm
# import matplotlib.pyplot as plt
# generation = iwae.generate()[0]
# plt.imshow(generation.reshape((28, 28)), cmap=cm.Greys_r)
# plt.show()
# plt.savefig(home+'/Downloads/sampled_image.png')



# #########################################
# New log marginal likelihood lower bound
# #########################################
# print 'evaluating'
# nll = vae.evaluate(datapoints=test_x, n_samples=300, n_datapoints=100)
# print nll



print 'Done'




















