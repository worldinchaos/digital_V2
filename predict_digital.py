
import glob
import numpy as np
import torch
import os
import cv2
from unet import UNet
import skimage.io as io

#from imaris_ims_file_reader.ims import ims
resolution_level = 0

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p","--path",type=str,default="./Train_image/")
parser.add_argument("-m","--model",type=str,default="./model_pth")
args = parser.parse_args()

if __name__ == "__main__":
   # 选择设备，有cuda用cuda，没有就用cpu
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # 加载网络，图片单通道，分类为1。
    net = UNet(n_channels=1, n_classes=1,bilinear=False)
    # 将网络拷贝到deivce中
    net.to(device=device)
    # 加载模型参数
    checkpoint = torch.load(args.model,map_location=device)
    net.load_state_dict(checkpoint['net'])
    # 测试模式
    net.eval()
    # 读取所有图片路径
    Test_Data_path = args.path
    tests_path = glob.glob(Test_Data_path + '*.tiff')
    # 遍历所有图片
    for test_path in tests_path:
        # 保存结果地址
        save_res_path = test_path.split('.tif')[0] + '_res.tif'
        # 读取图片
        img = io.imread(test_path)
        # 转为灰度图单通道

        # pytorch要求的格式（batch_size,c,w,h）
        img = img.reshape(1, 1, img.shape[0], img.shape[1])
        # 转为tensor
        img = img.astype(np.float32)
        img_tensor = torch.from_numpy(img)
        img_tensor = img_tensor.to(device=device, dtype=torch.float32)
        # 预测
        pred = net(img_tensor)
        # 提取结果
        pred = np.array(pred.data.cpu()[0])[0]
        # 处理结果
        pred[pred >= 0.5] = 65535
        pred[pred < 0.5] = 0
        # 保存图片
        pred=pred.astype(np.uint16)
        io.imsave(save_res_path, pred)