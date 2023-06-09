import torch
import torch.optim
from dataloader import SelfDataSet
from log import Logger
from plot import plot_picture
import os
import torch.nn as nn
import sys
from unet import UNet
from torch.utils.data import Dataset
from torch import optim, utils
import time

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p","--path",type=str,default="./train_image16_adj/")
parser.add_argument("-m","--model",type=str,default="./model_pth_norm_adj")
parser.add_argument("-e","--epoch",type=int,default=40)
parser.add_argument("-l","--learning",type=float,default=0.0001)
args = parser.parse_args()

Unet_train_txt = Logger('Unet_train.txt')
#原医学图像数据集
def Train_Unet(net,device,data_path,batch_size=3,epochs=40,lr=0.0001):
    #加载数据集
    train_dataset = SelfDataSet(data_path)
    train_loader = utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    #定义优化算法
    opt = optim.Adam((net.parameters()))
    #定义损失函数
    loss_fun = nn.BCEWithLogitsLoss()
    bes_los = float('inf')

    for epoch in range(epochs):
        net.train()
        running_loss = 0.0
        i = 0
        begin = time.perf_counter()
        for image, label in train_loader:
            opt.zero_grad()
            image = image.to(device=device, dtype=torch.float32)
            label = label.to(device=device, dtype=torch.float32)
            pred=net(image)
            loss = loss_fun(pred, label)
            loss.backward()
            i = i + 1
            running_loss = running_loss+loss.item()
            opt.step()
        end = time.perf_counter()
        loss_avg_epoch = running_loss/i
        Unet_train_txt.write(str(format(loss_avg_epoch, '.4f')) + '\n')
        print('epoch: %d avg loss: %f time:%d s' % (epoch, loss_avg_epoch, end - begin))
        if loss_avg_epoch < bes_los:
            bes_los = loss_avg_epoch
            state = {'net': net.state_dict(), 'opt': opt.state_dict(), 'epoch': epoch}
            torch.save(state, args.model)



if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net = UNet(1, 1,  bilinear=False)
    #print(net)
    net.to(device=device)
    #对应数据集的路径
    data_path = args.path
    Train_Unet(net, device, data_path, epochs=args.epoch, batch_size=1,lr=args.learning)
    Unet_train_txt.close()
    plot_picture('Unet_train.txt')
