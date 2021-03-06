import torch
import torchvision
import torchvision.transforms as transforms

import matplotlib.pyplot as plt
import numpy as np

from multiprocessing import Process, freeze_support

import torch.nn as nn
import torch.nn.functional as F

import torch.optim as optim
import torch.backends.cudnn as cudnn


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # self.features = self.make_layers([64, 'MP', 128, 'MP', 256, 256, 'MP', 512, 512, 'MP', 512, 512, 'MP'])
        self.features = self.make_layers([64, 64, 'MP', 128, 128, 'MP', 256, 256, 256, 'MP', 512, 512, 512, 'MP', 512, 512, 512, 'MP'])
        self.classifier = nn.Linear(512, 10)

    def forward(self, x):
        output = self.features(x)
        output = output.view(output.size(0), -1)
        output = self.classifier(output)
        return output

    def make_layers(self, layer_info):
        layers = []
        in_size = 3
        for inf in layer_info:
            if inf != 'MP':
                layers += [nn.Conv2d(in_size, inf, kernel_size=3, padding=1),
                           nn.ReLU(inplace=True), nn.BatchNorm2d(inf)]
                in_size = inf
            else:
                layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
				
        layers += [nn.AvgPool2d(kernel_size=1, stride=1)]
        return nn.Sequential(*layers)



def downloadData():
    trainData_transformation = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    testData_transformation = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])


    trainset = torchvision.datasets.CIFAR10(root='./data', download=True, train=True, transform=trainData_transformation)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=4, num_workers=2, shuffle=True)

    testset = torchvision.datasets.CIFAR10(root='./data', , download=True, train=False, transform=testData_transformation)
    testloader = torch.utils.data.DataLoader(testset, batch_size=4,  num_workers=2, shuffle=False)

    classes = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')
    
	return trainloader, testloader, classes






def Train_Test(trainloader, testloader,classes, net):
    print('Start of Training!')
    dataiter = iter(trainloader)
    images, labels = dataiter.next()

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)


    for epoch in range(230):  # loop over the dataset multiple times
        print("Starting Epoch %d" % epoch)
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            # get the inputs; data is a list of [inputs, labels]
            inputs, labels = data

            inputs = inputs.to(device)
            labels = labels.to(device)

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = net(inputs)
            #         print("##########################")
            #         print(np.shape(outputs))
            #         print(np.shape(labels))
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.item()
            if i % 2000 == 1999:  # print every 2000 mini-batches
                print('[%d, %5d] loss: %.3f' %
                      (epoch + 1, i + 1, running_loss / 2000))
                running_loss = 0.0

        if (epoch+1) % 20 == 0:
			PATH = './cifar_net.pkl'
			torch.save(net.state_dict(), PATH)
			
            correct = 0
            total = 0
            with torch.no_grad():
                for data in testloader:
                    images, labels = data
                    images = images.to(device)
                    labels = labels.to(device)

                    outputs = net(images)
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()

            print('Accuracy of the network on the 10000 test images at epoch %d: %d %%' % (
                    epoch, 100 * correct / total))

    print('Finished Training')


    # net = Net()
    # net.load_state_dict(torch.load(PATH))

    outputs = net(images)

    correct = 0
    total = 0
    with torch.no_grad():
        for data in testloader:
            images, labels = data
            images = images.to(device)
            labels = labels.to(device)

            outputs = net(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    print('Accuracy of the network on the 10000 test images: %d %%' % (
            100 * correct / total))

    class_correct = list(0. for i in range(10))
    class_total = list(0. for i in range(10))
    with torch.no_grad():
        for data in testloader:
            images, labels = data
            images = images.to(device)
            labels = labels.to(device)
            outputs = net(images)
            _, predicted = torch.max(outputs, 1)
            c = (predicted == labels).squeeze()
            for i in range(4):
                label = labels[i]
                class_correct[label] += c[i].item()
                class_total[label] += 1

    for i in range(10):
        print('Accuracy of %5s : %2d %%' % (
            classes[i], 100 * class_correct[i] / class_total[i]))

    torch.save(net, './cifat_net.pkl')


if __name__ == '__main__':
    # freeze_support()
    # Process(target=f).start()
    trainloader, testloader, classes = downloadData()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(device)
    net = Net()
    net = net.to(device)
    if device == 'cuda':
        net = torch.nn.DataParallel(net)
        cudnn.benchmark = True

    Train_Test(trainloader, testloader, classes, net)




