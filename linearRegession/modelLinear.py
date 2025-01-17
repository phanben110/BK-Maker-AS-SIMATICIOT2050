import numpy as np
import matplotlib.pyplot as plt
# create dummy data for training
import pandas as pd 
import numpy as np  
from sklearn.model_selection import train_test_split 
from BEN_model import linearRegression

kp = pd.read_csv('kp.txt', sep = "\t")
kp = np.array(kp).T

ki = pd.read_csv("ki.txt", sep = "\t")
ki = np.array(ki).T 

kd = pd.read_csv("kd.txt", sep = "\t") 
kd = np.array(kd).T 

Kp = np.append(kp[0],np.append(ki[0],kd[0]))
Ki = np.append(kp[1],np.append(ki[1],kd[1]))
Kd = np.append(kp[2],np.append(ki[2],kd[2]))
K1 = np.append(kp[3],np.append(ki[3],kd[3]))
K2 = np.append(kp[4],np.append(ki[4],kd[4]))
K3 = np.append(kp[5],np.append(ki[5],kd[5]))
print ( Kp )
#Y = np.array(kp[0], dtype=np.float32) 
#X = np.array([kp[1],kp[2],kp[3],kp[4],kp[5]],dtype=np.float32).T
#X = np.array([kp[3],kp[4],kp[5]],dtype=np.float32).T
Y = np.array(Kd, dtype=np.float32) 
X = np.array([Kp,Ki,K1,K2,K3],dtype=np.float32).T

Y = Y.reshape(-1, 1)
print (Y.shape)
print (X.shape)

x_values = [i for i in range(11)]
x_train = np.array(x_values, dtype=np.float32)
x_train = x_train.reshape(-1, 1)

y_values = [2*i + 1 for i in x_values]
y_train = np.array(y_values, dtype=np.float32)
y_train = y_train.reshape(-1, 1)
print (x_train.shape)
print (y_train.shape)
xTrain, xTest, yTrain, yTest = train_test_split(X,Y, test_size= 0.2, random_state =101)

import torch
from torch.autograd import Variable
#class linearRegression(torch.nn.Module):
#    def __init__(self, inputSize, outputSize):
#        super(linearRegression, self).__init__()
#        self.linear = torch.nn.Linear(inputSize, outputSize)
#
#    def forward(self, x):
#        out = self.linear(x)
#        return out


inputDim = 5        # takes variable 'x' 
outputDim = 1       # takes variable 'y'
learningRate = 0.00111 
epochs = 200000

model = linearRegression(inputDim, outputDim)
##### For GPU #######
if torch.cuda.is_available():
    model.cuda()

criterion = torch.nn.MSELoss() 
optimizer = torch.optim.SGD(model.parameters(), lr=learningRate)

for epoch in range(epochs):
    # Converting inputs and labels to Variable
    if torch.cuda.is_available():
        inputs = Variable(torch.from_numpy(xTrain).cuda())
        #inputs = Variable(torch.from_numpy(x_train).cuda())
        labels = Variable(torch.from_numpy(yTrain).cuda())
        #labels = Variable(torch.from_numpy(y_train).cuda())
    else:
        inputs = Variable(torch.from_numpy(x_train))
        labels = Variable(torch.from_numpy(y_train))

    # Clear gradient buffers because we don't want any gradient from previous epoch to carry forward, dont want to cummulate gradients
    optimizer.zero_grad()

    # get output from the model, given the inputs
    outputs = model(inputs)

    # get loss for the predicted output
    loss = criterion(outputs, labels)
    print(loss)
    # get gradients w.r.t to parameters
    loss.backward()

    # update parameters
    optimizer.step()

    print('epoch {}, loss {}'.format(epoch, loss.item()))


with torch.no_grad(): # we don't need gradients in the testing phase
    if torch.cuda.is_available():
        predicted = model(Variable(torch.from_numpy(xTest).cuda()))#.cpu().data.numpy()
    else:
        predicted = model(Variable(torch.from_numpy(xTest))).data.numpy()
    print(predicted)
    print(yTest)

torch.save(model.state_dict(), "kd.pt")
#plt.clf()
#plt.plot(xTrain, yTrain, 'go', label='True data', alpha=0.5)
#plt.plot(xTrain, predicted, '--', label='Predictions', alpha=0.5)
#plt.legend(loc='best')
#plt.show()

