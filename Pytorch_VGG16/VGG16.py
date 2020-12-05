import math
import torch
import torch.nn as nn

cfg = {'VGG16': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512,
                 512, 'M', 512, 512, 512, 'M']}


class VGG(nn.Module):
    def __init__(self, net_name):
        super(VGG, self).__init__()

        # 构建网络的卷积层和池化层，最终输出命名features，原因是通常认为经过这些操作的输出
        # 为包含图像空间信息的特征层
        self.features = self._make_layers(cfg[net_name])

        # 构建卷积层之后的全连接层以及分类器
        self.classifier = nn.Sequential(
            nn.Dropout(),  # 防止或减少过拟合采用的函数 函数会在训练过程中随机扔掉一部分神经元 按照概率使某个神经元不更新权重
            nn.Linear(512, 512),  # fc1
            nn.ReLU(True),
            nn.Dropout(),
            nn.Linear(512, 512),  # fc2
            nn.ReLU(True),
            nn.Linear(512, 10)  # fc3 最终Cifar10的输出是10分类
        )

        # 初始化权重
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
                m.bias.data.zero_()

    def forward(self, x):
        x = self.features(x)  # 前向传播的时候先经过卷积层和池化层
        x = x.view(x.size(0), -1)
        x = self.classifier(x)  # 再将features（得到网络输出的特征层）的结果拼接到分类器上
        return x

    def _make_layers(self, cfg):
        layers = []
        in_channels = 3
        for v in cfg:
            if v == 'M':
                layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
            else:
                # conv2d = nn.Conv2d(in_channels, v, kernel_size=3, padding=1)
                # layers += [conv2d, nn.ReLU(inplace=True)]
                layers += [nn.Conv2d(in_channels, v, kernel_size=3, padding=1),
                           nn.BatchNorm2d(v),
                           nn.ReLU(inplace=True)]
                in_channels = v
        return nn.Sequential(*layers)


net = VGG('VGG16')
