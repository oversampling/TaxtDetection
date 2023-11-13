import os
import math
import time
import torch
import torch.nn as nn
from torch.autograd import Variable
from torch.utils.data import DataLoader
from torchtext.datasets import AG_NEWS
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator
from torch import optim
from torch.utils.data import random_split
from torchvision import transforms
from PIL import Image

class CRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(CRNN, self).__init__()
        self.hidden_size = hidden_size
        self.cnn = nn.Conv2d(input_size, hidden_size, kernel_size=3, stride=1, padding=1)
        self.rnn = nn.LSTM(hidden_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.cnn(x)
        x = x.view(x.size(0), -1, self.hidden_size)
        x, _ = self.rnn(x)
        x = self.fc(x)
        return x
   
class SynthDataset(Dataset):
    def __init__(self, path, transform=None):
        self.path = path
        self.images = os.listdir(self.path)
        self.nSamples = len(self.images)
        self.transform = transform
        self.collate_fn = SynthCollator()

    def __len__(self):
        return self.nSamples

    def __getitem__(self, index):
        assert index <= len(self), 'index range error'
        imagepath = os.path.join(self.path, self.images[index])
        img = Image.open(imagepath)
        if self.transform is not None:
            img = self.transform(img)
        item = {'img': img, 'idx': index}
        item['label'] = os.path.basename(imagepath).split('_')[0]
        return item
   
