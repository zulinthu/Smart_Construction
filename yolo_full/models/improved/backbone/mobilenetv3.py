"""
MobileNetV3轻量化骨干网络
用于替换YOLOv5的CSPDarknet53
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class HSwish(nn.Module):
    """Hard Swish激活函数"""

    def __init__(self, inplace=True):
        super(HSwish, self).__init__()
        self.inplace = inplace

    def forward(self, x):
        return x * F.relu6(x + 3, inplace=self.inplace) / 6


class HSigmoid(nn.Module):
    """Hard Sigmoid激活函数"""

    def __init__(self, inplace=True):
        super(HSigmoid, self).__init__()
        self.inplace = inplace

    def forward(self, x):
        return F.relu6(x + 3, inplace=self.inplace) / 6


class SEModule(nn.Module):
    """Squeeze-and-Excitation模块"""

    def __init__(self, in_channels, reduction=4):
        super(SEModule, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(in_channels, in_channels // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(in_channels // reduction, in_channels, bias=False),
            HSigmoid(),
        )

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y.expand_as(x)


class MobileBottleneck(nn.Module):
    """MobileNetV3基本模块"""

    def __init__(self, in_channels, out_channels, kernel_size, stride, exp_size, se=False, nl="RE"):
        """
        Args:
            in_channels: 输入通道数
            out_channels: 输出通道数
            kernel_size: 卷积核大小
            stride: 步长
            exp_size: 扩张通道数
            se: 是否使用SE模块
            nl: 非线性激活 ('RE'=ReLU, 'HS'=HSwish)
        """
        super(MobileBottleneck, self).__init__()
        self.use_res_connect = stride == 1 and in_channels == out_channels

        # 选择激活函数
        if nl == "RE":
            activation = nn.ReLU6
        elif nl == "HS":
            activation = HSwish
        else:
            raise ValueError(f"Unknown activation: {nl}")

        # 1x1扩张卷积
        layers = []
        if exp_size != in_channels:
            layers.extend(
                [
                    nn.Conv2d(in_channels, exp_size, 1, 1, 0, bias=False),
                    nn.BatchNorm2d(exp_size),
                    activation(inplace=True),
                ]
            )

        # Depthwise卷积
        padding = (kernel_size - 1) // 2
        layers.extend(
            [
                nn.Conv2d(
                    exp_size, exp_size, kernel_size, stride, padding, groups=exp_size, bias=False
                ),
                nn.BatchNorm2d(exp_size),
                activation(inplace=True),
            ]
        )

        # SE模块
        if se:
            layers.append(SEModule(exp_size))

        # 1x1线性卷积
        layers.extend(
            [nn.Conv2d(exp_size, out_channels, 1, 1, 0, bias=False), nn.BatchNorm2d(out_channels)]
        )

        self.conv = nn.Sequential(*layers)

    def forward(self, x):
        if self.use_res_connect:
            return x + self.conv(x)
        else:
            return self.conv(x)


class MobileNetV3(nn.Module):
    """MobileNetV3骨干网络"""

    def __init__(self, mode="small", width_mult=1.0, out_stages=[3, 4, 5]):
        """
        Args:
            mode: 'small' 或 'large'
            width_mult: 宽度倍数
            out_stages: 输出的stage索引
        """
        super(MobileNetV3, self).__init__()

        self.mode = mode
        self.out_stages = out_stages

        if mode == "small":
            # MobileNetV3-Small配置
            # [k, exp, c, se, nl, s]
            config = [
                # Stage 1
                [3, 16, 16, True, "RE", 2],
                # Stage 2
                [3, 72, 24, False, "RE", 2],
                [3, 88, 24, False, "RE", 1],
                # Stage 3
                [5, 96, 40, True, "HS", 2],
                [5, 240, 40, True, "HS", 1],
                [5, 240, 40, True, "HS", 1],
                [5, 120, 48, True, "HS", 1],
                [5, 144, 48, True, "HS", 1],
                # Stage 4
                [5, 288, 96, True, "HS", 2],
                [5, 576, 96, True, "HS", 1],
                [5, 576, 96, True, "HS", 1],
            ]
        else:
            # MobileNetV3-Large配置
            config = [
                # Stage 1
                [3, 16, 16, False, "RE", 1],
                # Stage 2
                [3, 64, 24, False, "RE", 2],
                [3, 72, 24, False, "RE", 1],
                # Stage 3
                [5, 72, 40, True, "RE", 2],
                [5, 120, 40, True, "RE", 1],
                [5, 120, 40, True, "RE", 1],
                # Stage 4
                [3, 240, 80, False, "HS", 2],
                [3, 200, 80, False, "HS", 1],
                [3, 184, 80, False, "HS", 1],
                [3, 184, 80, False, "HS", 1],
                [3, 480, 112, True, "HS", 1],
                [3, 672, 112, True, "HS", 1],
                # Stage 5
                [5, 672, 160, True, "HS", 2],
                [5, 960, 160, True, "HS", 1],
                [5, 960, 160, True, "HS", 1],
            ]

        # 第一层卷积
        input_channel = self._make_divisible(16 * width_mult, 8)
        self.conv_stem = nn.Sequential(
            nn.Conv2d(3, input_channel, 3, 2, 1, bias=False),
            nn.BatchNorm2d(input_channel),
            HSwish(inplace=True),
        )

        # 构建MobileBottleneck层
        layers = []
        for k, exp, c, se, nl, s in config:
            output_channel = self._make_divisible(c * width_mult, 8)
            exp_channel = self._make_divisible(exp * width_mult, 8)
            layers.append(
                MobileBottleneck(input_channel, output_channel, k, s, exp_channel, se, nl)
            )
            input_channel = output_channel

        self.layers = nn.ModuleList(layers)

        self._initialize_weights()

    def _make_divisible(self, v, divisor, min_value=None):
        """确保通道数可被divisor整除"""
        if min_value is None:
            min_value = divisor
        new_v = max(min_value, int(v + divisor / 2) // divisor * divisor)
        if new_v < 0.9 * v:
            new_v += divisor
        return new_v

    def _initialize_weights(self):
        """初始化权重"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x):
        """前向传播"""
        x = self.conv_stem(x)

        outputs = []
        for idx, layer in enumerate(self.layers):
            x = layer(x)
            if (idx + 1) in self.out_stages:
                outputs.append(x)

        if len(self.out_stages) == 1:
            return outputs[0]
        return outputs


def mobilenetv3_small(width_mult=1.0, out_stages=[3, 4, 5]):
    """创建MobileNetV3-Small模型"""
    return MobileNetV3(mode="small", width_mult=width_mult, out_stages=out_stages)


def mobilenetv3_large(width_mult=1.0, out_stages=[3, 4, 5]):
    """创建MobileNetV3-Large模型"""
    return MobileNetV3(mode="large", width_mult=width_mult, out_stages=out_stages)


# 测试代码
if __name__ == "__main__":
    print("测试MobileNetV3...")

    # 创建模型
    model = mobilenetv3_small(width_mult=1.0)
    model.eval()

    # 测试输入
    x = torch.randn(1, 3, 640, 640)

    # 前向传播
    with torch.no_grad():
        outputs = model(x)

    # 打印输出
    print(f"\n输入: {x.shape}")
    for i, out in enumerate(outputs):
        print(f"输出 {i + 1}: {out.shape}")

    # 计算参数量
    total_params = sum(p.numel() for p in model.parameters())
    print(f"\n总参数量: {total_params:,}")

    print("\n✓ 测试完成!")
