

#Cleaned version of 4

# Select L_M or L_arc
L_AR = 0
L_M = 1


import numpy as np

import torch
from torch.autograd import Variable
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F

from os.path import expanduser
home = expanduser("~")

import matplotlib.pyplot as plt

import math


def plot_isocontours(ax, func, xlimits=[-6, 6], ylimits=[-6, 6],
                     numticks=101, cmap=None, alpha=1., legend=False):
    x = np.linspace(*xlimits, num=numticks)
    y = np.linspace(*ylimits, num=numticks)
    X, Y = np.meshgrid(x, y)
    aaa = torch.from_numpy(np.concatenate([np.atleast_2d(X.ravel()), np.atleast_2d(Y.ravel())]).T).type(torch.FloatTensor)
    bbb = func(Variable(aaa))
    bbb = bbb.data
    zs = torch.exp(bbb)
    Z = zs.view(X.shape)
    Z=Z.numpy()
    cs = plt.contour(X, Y, Z, cmap=cmap, alpha=alpha)
    ax.set_yticks([])
    ax.set_xticks([])
    plt.gca().set_aspect('equal', adjustable='box')



def lognormal4_2(x, mean, logvar):
    '''
    x: [B,X]
    mean,logvar: [X]
    output: [B]
    '''
    D = x.size()[1]
    term1 = D * torch.log(torch.FloatTensor([2.*math.pi])) #[1]
    return -.5 * (Variable(term1) + logvar.sum(0) + ((x - mean).pow(2)/torch.exp(logvar)).sum(1))


def logpz(z):
    cccc = lognormal4_2(z, Variable(torch.zeros(2)+2), Variable(torch.zeros(2)))
    aaa = torch.clamp(cccc, min=-30)
    bbb = torch.clamp(lognormal4_2(z, Variable(torch.zeros(2)), Variable(torch.zeros(2))), min=-30)

    return torch.log(.5*torch.exp(aaa) + .5*torch.exp(bbb))



def plot_it2(e, model, elbo):

    plt.cla()

    ax = plt.subplot2grid((rows,cols), (0,0), frameon=False)
    plot_isocontours(ax, logpz, cmap='Blues')

    func = lambda zs: lognormal4_2(zs, model.mean1, model.logvar1)
    plot_isocontours(ax, func, cmap='Reds')

    func = lambda zs: lognormal4_2(zs, (model.mean1*model.linear_transform)+model.bias_transform, torch.log(torch.exp(model.logvar2) + model.linear_transform.pow(2)*torch.exp(model.logvar1)))
    plot_isocontours(ax, func, cmap='Greens')   

    ax.annotate('iter:'+str(e), xytext=(.1, 1.), xy=(0, 1), textcoords='axes fraction')
    ax.annotate('elbo'+str(elbo), xytext=(.1, .95), xy=(0, 1), textcoords='axes fraction')

    plt.draw()
    plt.pause(1.0/30.0)


def train(model, path_to_load_variables='', path_to_save_variables='', 
            epochs=10, batch_size=20, display_epoch=2):
    

    if path_to_load_variables != '':
        model.load_state_dict(torch.load(path_to_load_variables))
        print 'loaded variables ' + path_to_load_variables

    optimizer = optim.Adam(model.params, lr=.005)

    for epoch in range(1, epochs + 1):

        optimizer.zero_grad()

        elbo, logpz, logqz = model.forward()
        loss = -(elbo)

        loss.backward()
        optimizer.step()

        if epoch%display_epoch==0:
            test_score =test(model)
            print 'Train Epoch: {}/{}'.format(epoch, epochs), \
                'Loss:{:.4f}'.format(loss.data[0]), \
                'logpz:{:.4f}'.format(logpz.data[0]), \
                'logqz:{:.4f}'.format(logqz.data[0]), \
                'test', test_score

            plot_it2(epoch, model, test_score)

            print 'Mean1', model.mean1.data.numpy()
            print 'Logvar1', model.logvar1.data.numpy()
            print 'Linear Transform', model.linear_transform.data.numpy()
            print 'Transform Bias', model.bias_transform.data.numpy()
            print 'Log var 2', model.logvar2.data.numpy()
            print



    if path_to_save_variables != '':
        torch.save(model.state_dict(), path_to_save_variables)
        print 'Saved variables to ' + path_to_save_variables



def test(model, path_to_load_variables='', batch_size=100):

    if path_to_load_variables != '':
        model.load_state_dict(torch.load(path_to_load_variables))
        print 'loaded variables ' + path_to_load_variables

    elbos = []
    data_index= 0
    for i in range(batch_size):
        elbo, logpz, logqz = model()
        elbos.append(elbo.data[0])
    return np.mean(elbos)








class MCGS(nn.Module):
    #Multiple Covaried Gaussian Samples 
    def __init__(self, dim, logpz):
        super(MCGS, self).__init__()

        torch.manual_seed(1000)

        self.z_size = dim

        self.mean1 = Variable(torch.zeros(self.z_size), requires_grad=True)
        self.logvar1 = Variable(torch.randn(self.z_size)-3., requires_grad=True)

        self.linear_transform = Variable(torch.zeros(self.z_size), requires_grad=True)
        self.bias_transform = Variable(torch.zeros(self.z_size), requires_grad=True)
        self.logvar2 = Variable(torch.randn(self.z_size)-3., requires_grad=True)

        self.params = [self.mean1, self.logvar1, self.linear_transform, self.bias_transform, self.logvar2]


        self.logpz = logpz


    def sample(self, mu, logvar):
        eps = Variable(torch.FloatTensor(1, self.z_size).normal_()) #[1,Z]
        z = eps.mul(torch.exp(.5*logvar)) + mu  #[1,Z]
        logqz = lognormal4_2(z, mu.detach(), logvar.detach())
        return z, logqz


    def forward(self):
        
        z, logqz = self.sample(self.mean1, self.logvar1) #[1,Z]
        z2, logqz2 = self.sample((z*self.linear_transform)+self.bias_transform, self.logvar2) #[1,Z]

        
        if L_M:
        	#z2 under marginal q2
        	logqz2 = lognormal4_2(z2, (self.mean1*self.linear_transform)+self.bias_transform, torch.log(torch.exp(self.logvar2) + self.linear_transform.pow(2)*torch.exp(self.logvar1)))

        logpz = self.logpz(z) 
        logpz2 = self.logpz(z2) 

        logpz = logpz + logpz2
        logqz = logqz + logqz2

        elbo = logpz - logqz  #[P,B]
        elbo = torch.mean(elbo) #[1]

        logpz = torch.mean(logpz)
        logqz = torch.mean(logqz)

        return elbo, logpz, logqz










rows = 1
cols = 1
fig = plt.figure(figsize=(4+cols,4+rows), facecolor='white')
plt.ion()
plt.show(block=False)

model = MCGS(dim=2, logpz=logpz)

path_to_load_variables=''
path_to_save_variables=''

train(model=model, 
            path_to_load_variables=path_to_load_variables, 
            path_to_save_variables=path_to_save_variables, 
            epochs=10000, batch_size=4, display_epoch=40)






























































