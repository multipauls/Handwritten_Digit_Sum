# -*- coding: utf-8 -*-
"""ML4NS_Assign1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1peL7k1Nekochqdx7HVp3_GjFp7he5kDt
"""

import numpy as np
import matplotlib.pyplot as plt
from google.colab import drive

import torch
import numpy as np
import torchvision.datasets as datasets
import torch.nn as nn
import torchvision.transforms as transforms
import torch.optim as optim

import cv2

drive.mount("/content/drive")

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=32 , kernel_size=7, padding=1, stride=(1,1))
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=32 , kernel_size=7, padding=1, stride=(1,1))
        self.bn1 = nn.BatchNorm2d(32)
        self.bn2 = nn.BatchNorm2d(32)
        self.pad = nn.ZeroPad2d((3, 3))
        self.pool = nn.MaxPool2d(2)
        self.fc = nn.Linear(4160,10)

    def forward(self, x):
       
        x = self.pad(x)
        x = self.conv1(x)
        x = self.bn1(x)
        x = nn.functional.relu(x)
        
        x = self.conv2(x)
        x = self.bn2(x)
        x = nn.functional.relu(x)
        x = self.pool(x)
        
        x = x.view(-1, 4160)
        x = self.fc(x)
        
        return x

def accuracy(outputs, labels):
    _,preds = torch.max(outputs, dim=1)
    return torch.tensor(torch.sum(preds == labels).item() / len(preds))

def train():
    mnist_train = datasets.MNIST('./', train=True, download=True, transform=transforms.ToTensor())
    mnist_test= datasets.MNIST('./', train=False, download=True, transform=transforms.ToTensor())
    cnn = CNN().to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(cnn.parameters(), lr=0.001)

    batch_size = 1

    trainloader = torch.utils.data.DataLoader(mnist_train, batch_size=batch_size, shuffle=True)
    testloader = torch.utils.data.DataLoader(mnist_test, batch_size=batch_size, shuffle=True)

    accur = []
    for epoch in range(5):  
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            inputs, labels = data
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            outputs = cnn(inputs)

            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            if i % 1000 == 999:    # print every 1000 batches
                print('[%d, %5d] loss: %.3f' %
                      (epoch + 1, i + 1, running_loss / 1000))
                running_loss = 0.0
        acc = []
        for j, data in enumerate(testloader, 0):
            inputs, labels = data
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = cnn(inputs)
            acc.append(accuracy(outputs, labels))
        print(torch.stack(acc).mean())
        accur.append(torch.stack(acc).mean())
    print('Finished Training, saving')
    torch.save(cnn, '/content/drive/My Drive/ML4NS1/cnn_mnist')
    print("Saved")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

train()

train_data0 = np.load('/content/drive/My Drive/ML4NS1/data0.npy')
train_lab0 = np.load('/content/drive/My Drive/ML4NS1/lab0.npy')
train_data1 = np.load('/content/drive/My Drive/ML4NS1/data1.npy')
train_lab1 = np.load('/content/drive/My Drive/ML4NS1/lab1.npy')
train_data2 = np.load('/content/drive/My Drive/ML4NS1/data2.npy')
train_lab2 = np.load('/content/drive/My Drive/ML4NS1/lab2.npy')

train_data = np.concatenate((train_data0, train_data1, train_data2))
train_lab = np.concatenate((train_lab0, train_lab1, train_lab2))

def split(image):
    ret, thresh = cv2.threshold(image,50,150,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    connectivity = 8  
    output = cv2.connectedComponentsWithStats(thresh, connectivity, cv2.CV_32S)
    stats = output[2]
    segments = []
    for i in range(1,len(stats)):
        l,t,w,h,a = stats[i]
        cropped = image[t:t+h,l:l+w]
        if a >= 30:
            if w > 22 and w<=37:
                splitted1=image[t:t+h, l:l+int(w/2)]
                splitted2=image[t:t+h, l+int(w/2):l+w]

                splitted1 = cv2.resize(splitted1, (0,0), fx=0.78, fy=0.78, interpolation = cv2.INTER_AREA) 
                splitted2 = cv2.resize(splitted2, (0,0), fx=0.78, fy=0.78, interpolation = cv2.INTER_AREA)


                pad_shape = np.array([28, 28]) - np.array(splitted1.shape)
                splitted1 = np.pad(splitted1, ((pad_shape[0] // 2, (pad_shape[0] + 1) // 2), (pad_shape[1] // 2, (pad_shape[1] + 1) // 2)))
                segments.append(splitted1)

                pad_shape = np.array([28, 28]) - np.array(splitted2.shape)
                splitted2 = np.pad(splitted2, ((pad_shape[0] // 2, (pad_shape[0] + 1) // 2), (pad_shape[1] // 2, (pad_shape[1] + 1) // 2)))
                segments.append(splitted2)
            
            elif w>37:
                splitted1=image[t:t+h, l:l+int(w/3)]
                splitted2=image[t:t+h, l+int(w/3):l+int(2*w/3)]
                splitted3=image[t:t+h, l+int(2*w/3):l+w]

                splitted1 = cv2.resize(splitted1, (0,0), fx=0.78, fy=0.78, interpolation = cv2.INTER_AREA) 
                splitted2 = cv2.resize(splitted2, (0,0), fx=0.78, fy=0.78, interpolation = cv2.INTER_AREA)
                splitted3 = cv2.resize(splitted3, (0,0), fx=0.78, fy=0.78, interpolation = cv2.INTER_AREA)


                pad_shape = np.array([28, 28]) - np.array(splitted1.shape)
                splitted1 = np.pad(splitted1, ((pad_shape[0] // 2, (pad_shape[0] + 1) // 2), (pad_shape[1] // 2, (pad_shape[1] + 1) // 2)))
                segments.append(splitted1)

                pad_shape = np.array([28, 28]) - np.array(splitted2.shape)
                splitted2 = np.pad(splitted2, ((pad_shape[0] // 2, (pad_shape[0] + 1) // 2), (pad_shape[1] // 2, (pad_shape[1] + 1) // 2)))
                segments.append(splitted2)

                pad_shape = np.array([28, 28]) - np.array(splitted3.shape)
                splitted3 = np.pad(splitted3, ((pad_shape[0] // 2, (pad_shape[0] + 1) // 2), (pad_shape[1] // 2, (pad_shape[1] + 1) // 2)))
                segments.append(splitted3)

            else:
                if h>28:
                    cropped = cv2.resize(cropped, (0,0), fx=0.8, fy=0.8, interpolation = cv2.INTER_AREA)
                pad_shape = np.array([28, 28]) - np.array(cropped.shape)
                cropped = np.pad(cropped, ((pad_shape[0] // 2, (pad_shape[0] + 1) // 2), (pad_shape[1] // 2, (pad_shape[1] + 1) // 2)))
                segments.append(cropped)
    return segments

def predict(model_path, train_data, train_lab):
    predictor = torch.load(model_path)
    predictor.to(device)
    acc = []
    counter = 0
    falsectr = 0
    for i in range(len(train_data)):
        img = train_data[i]
        labels = train_lab[i]     
        inputs = split(img)
        sum = 0
        digits = []
        for j in range(len(inputs)):
            image = torch.from_numpy(inputs[j])
            image = torch.reshape(image, (1,1,28,28)).float()
            outputs = predictor(image.to(device))
            digit = torch.argmax(outputs)
            digits.append(digit)
            sum += digit
        if sum == labels:
            counter+=1
        if i % 5000 == 4999:    # print every 5000
                print('%d, accuracy: %.3f' %
                        ( i+1, counter*100 / i))
    print("Final accuracy "+str(counter*100/len(train_data))+"%")

predict('/content/drive/My Drive/ML4NS1/cnn_mnist',  train_data, train_lab)



