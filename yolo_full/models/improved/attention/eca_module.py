"""
ECA (Efficient Channel Attention) 模块
一种高效的通道注意力机制
"""

import torch
import torch.nn as nn
import math


class ECAModule(nn.Module):
    """
    Efficient Channel Attention (ECA) 模块
    
    Paper: ECA-Net: Efficient Channel Attention for Deep Convolutional Neural Networks
    Link: https://arxiv.org/abs/1910.03151
    
    相比SENet，ECA避免了降维，使用1D卷积学习通道注意力，
    参数更少，计算更高效
    """
    
    def __init__(self, channels, k_size=3, gamma=2, b=1):
        """
        Args:
            channels: 输入通道数
            k_size: 1D卷积核大小（如果为None则自适应计算）
            gamma: 自适应核大小的gamma参数
            b: 自适应核大小的b参数
        """
        super(ECAModule, self).__init__()
        
        # 自适应计算卷积核大小
        if k_size is None:
            t = int(abs((math.log(channels, 2) + b) / gamma))
            k_size = t if t % 2 else t + 1
        
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.conv = nn.Conv1d(1, 1, kernel_size=k_size, padding=(k_size - 1) // 2, bias=False)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        """
        前向传播
        
        Args:
            x: 输入特征图 [B, C, H, W]
            
        Returns:
            out: 注意力加权后的特征图 [B, C, H, W]
        """
        # 全局平均池化 [B, C, H, W] -> [B, C, 1, 1]
        y = self.avg_pool(x)
        
        # 将通道维度变换为序列维度 [B, C, 1, 1] -> [B, 1, C]
        y = y.squeeze(-1).transpose(-1, -2)
        
        # 1D卷积学习通道间的依赖 [B, 1, C] -> [B, 1, C]
        y = self.conv(y)
        
        # 恢复形状并应用sigmoid [B, 1, C] -> [B, C, 1, 1]
        y = y.transpose(-1, -2).unsqueeze(-1)
        y = self.sigmoid(y)
        
        # 通道注意力加权
        return x * y.expand_as(x)


class ECABasicBlock(nn.Module):
    """带有ECA的基本残差块"""
    
    def __init__(self, in_channels, out_channels, stride=1):
        super(ECABasicBlock, self).__init__()
        
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # ECA模块
        self.eca = ECAModule(out_channels)
        
        # 残差连接
        self.downsample = None
        if stride != 1 or in_channels != out_channels:
            self.downsample = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        identity = x
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        # 应用ECA注意力
        out = self.eca(out)
        
        # 残差连接
        if self.downsample is not None:
            identity = self.downsample(x)
        
        out += identity
        out = self.relu(out)
        
        return out


# 测试代码
if __name__ == '__main__':
    print("测试ECA模块...")
    
    # 创建ECA模块
    eca = ECAModule(channels=64, k_size=3)
    print(f"✓ ECA模块创建成功")
    
    # 测试输入
    x = torch.randn(2, 64, 56, 56)
    print(f"输入shape: {x.shape}")
    
    # 前向传播
    with torch.no_grad():
        out = eca(x)
    print(f"输出shape: {out.shape}")
    
    # 计算参数量
    total_params = sum(p.numel() for p in eca.parameters())
    print(f"参数量: {total_params}")
    
    # 测试ECA基本块
    print("\n测试ECA基本块...")
    block = ECABasicBlock(64, 128, stride=2)
    
    with torch.no_grad():
        out = block(x)
    print(f"输入shape: {x.shape}")
    print(f"输出shape: {out.shape}")
    
    total_params = sum(p.numel() for p in block.parameters())
    print(f"参数量: {total_params:,}")
    
    print("\n✓ 所有测试通过!")










