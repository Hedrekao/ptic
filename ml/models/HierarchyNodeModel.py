import torch.nn as nn


class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1, dropout_rate=0.2):
        super().__init__()

        self.dropout = nn.Dropout2d(dropout_rate)

        self.bn1 = nn.BatchNorm2d(in_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv1 = nn.Conv2d(in_channels, out_channels,
                               kernel_size=3, stride=stride, padding=1)

        self.bn2 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels,
                               kernel_size=3, padding=1)

        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels,
                          kernel_size=1, stride=stride)
            )
        else:
            self.shortcut = nn.Identity()

    def forward(self, x):
        # Pre-activation pattern
        out = self.bn1(x)
        out = self.relu(out)
        out = self.conv1(out)

        out = self.bn2(out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.conv2(out)

        out += self.shortcut(x)

        return out


class HierarchyNodeModel(nn.Module):
    def __init__(self, num_classes, input_channels=3):
        super().__init__()

        self.conv1 = nn.Sequential(
            nn.Conv2d(input_channels, 16, kernel_size=3,
                      stride=1, padding=1),  # Changed from 7 to 3
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.Dropout2d(0.1),
            nn.MaxPool2d(kernel_size=2, stride=2)  # Changed pool size to 2
        )  # Output: 50x50

        self.layer1 = nn.Sequential(
            ResidualBlock(16, 48, dropout_rate=0.1),
            ResidualBlock(48, 48, dropout_rate=0.1),
            ResidualBlock(48, 48, dropout_rate=0.1)
        )

        self.layer2 = nn.Sequential(
            ResidualBlock(48, 96, stride=2, dropout_rate=0.15),
            ResidualBlock(96, 96, dropout_rate=0.15),
            ResidualBlock(96, 96, dropout_rate=0.15)
        )

        self.layer3 = nn.Sequential(
            ResidualBlock(96, 192, stride=2, dropout_rate=0.2),
            ResidualBlock(192, 192, dropout_rate=0.2)
        )

        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))

        # Adjust the head for better feature extraction
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.3),
            nn.Linear(192, 96),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(96, num_classes)
        )

        # Weight initialization
        self.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(
                m.weight, mode='fan_in', nonlinearity='relu')
        elif isinstance(m, nn.BatchNorm2d):
            nn.init.constant_(m.weight, 1)
            nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.Linear):
            nn.init.normal_(m.weight, 0, 0.01)
            nn.init.constant_(m.bias, 0)

    def forward(self, x):
        x = self.conv1(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.avgpool(x)
        x = self.head(x)
        return x
