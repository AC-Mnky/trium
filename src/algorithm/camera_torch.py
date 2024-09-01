import torch
import torch.nn as nn
from torch import tensor
import numpy as np
from torch.utils.data import Dataset, DataLoader

INITIAL_XYZ, INITIAL_ROTATION, INITIAL_FOV, RESOLUTION = (
    # (140.0, -40.0, -220.0), (56.0, 0.0, 0.0), (52, 50), (320, 240)
    # (100.0, -30.0, -200.0), (50.0, 0.0, 0.0), (50.0, 40.0), (320, 240)
    (142.0, -38.0, -219.0), (56.3, 0.9, -0.5), (51.45, 51.09), (320, 240)
)


class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.xyz = nn.parameter.Parameter(tensor(INITIAL_XYZ, dtype=torch.float))
        self.rotation = nn.parameter.Parameter(tensor(INITIAL_ROTATION, dtype=torch.float))
        self.fov = nn.parameter.Parameter(tensor(INITIAL_FOV, dtype=torch.float))
        self.resolution = nn.parameter.Parameter(tensor(RESOLUTION), requires_grad=False)
        self.matrix = None
        self.build()

    def build(self):
        tpo = self.rotation / 180 * np.pi
        theta, phi, omega = tpo[0], tpo[1], tpo[2]
        half_fov = self.fov / 180 * np.pi / 2
        half_fov_h, half_fov_v = half_fov[0], half_fov[1]
        res_h, res_v = self.resolution[0], self.resolution[1]

        trans_phi = torch.stack((
            torch.cos(phi), -torch.sin(phi), torch.zeros(()),
            torch.sin(phi), torch.cos(phi), torch.zeros(()),
            torch.zeros(()), torch.zeros(()), torch.ones(()),
        )).reshape((3, 3))

        trans_theta = torch.stack((
            torch.sin(theta), torch.zeros(()), -torch.cos(theta),
            torch.zeros(()), torch.ones(()), torch.zeros(()),
            torch.cos(theta), torch.zeros(()), torch.sin(theta),
        )).reshape((3, 3))

        trans_omega = torch.stack((
            torch.ones(()), torch.zeros(()), torch.zeros(()),
            torch.zeros(()), torch.cos(omega), torch.sin(omega),
            torch.zeros(()), -torch.sin(omega), torch.cos(omega),
        )).reshape((3, 3))

        trans = torch.matmul(torch.matmul(trans_phi, trans_theta), trans_omega)

        img_to_relative_cords_mapping = torch.stack((
            torch.ones(()), torch.zeros(()), torch.zeros(()),
            -torch.tan(half_fov_h), 2 / res_h * torch.tan(half_fov_h), torch.zeros(()),
            -torch.tan(half_fov_v), torch.zeros(()), 2 / res_v * torch.tan(half_fov_v),
        )).reshape((3, 3))

        self.matrix = torch.matmul(trans, img_to_relative_cords_mapping)

    def forward(self, x: tensor):
        # self.build()
        x = torch.concat((torch.ones(x.shape[0], 1), x), dim=1)
        x = torch.tensordot(x, self.matrix, dims=([1], [1]))
        x /= x[:, 2:3].repeat(1, 3)
        x = torch.stack((self.xyz[0] - self.xyz[2] * x[:, 0], self.xyz[1] - self.xyz[2] * x[:, 1]), dim=1)
        return x


def criterion(output: tensor, label: tensor):
    return torch.sum(torch.square(output / label - 1), dim=1)


class NewDataset(Dataset):
    def __init__(self, data, labels):
        # Initialize the data and labels
        self.data = data
        self.labels = labels

    def __len__(self):
        # Return the total number of samples
        return len(self.data)

    def __getitem__(self, index):
        # Retrieve a sample from the dataset
        sample = self.data[index]
        label = self.labels[index]
        return sample, label


def train(model, dataloader):
    model.train()
    for x, target_y in train_dataloader:
        optimizer.zero_grad()
        y = model(x)
        loss = torch.mean(criterion(y, target_y), dim=0)
        loss.backward(retain_graph=True)
        optimizer.step()
        # print('train loss:', float(loss))


def evaluate(model, dataloader):
    model.eval()
    loss_sum = 0
    num = 0
    with torch.no_grad():
        for x, target_y in dataloader:
            y = model(x)
            loss_sum += torch.sum(criterion(y, target_y), dim=0)
            num += x.shape[0]
    print('test loss:', float(loss_sum / num))


if __name__ == '__main__':
    model = Model()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    import camera_convert

    camera_state = camera_convert.CameraState((142.0, -38.0, -219.0), (56.3, 0.9, -0.5), (51.45, 51.09), (320, 240))

    data = tensor([(i, j) for i in range(0, 320, 10) for j in range(0, 240, 10)])
    labels = tensor(
        [camera_convert.img2space(camera_state, i, j)[1:3]
         for i in range(0, 320, 10) for j in range(0, 240, 10)])

    all_dataset = NewDataset(data, labels)
    train_dataset, test_dataset = torch.utils.data.random_split(all_dataset, [32*12, 32*12])
    # train_dataset = NewDataset(data[:500], labels[:500])
    # test_dataset = NewDataset(data[500:], labels[500:])
    train_dataloader = DataLoader(train_dataset, batch_size=10, shuffle=True)
    test_dataloader = DataLoader(test_dataset, batch_size=100, shuffle=True)

    print()
    evaluate(model, test_dataloader)

    print()
    for epoch in range(1000):
        train(model, train_dataloader)
        evaluate(model, test_dataloader)
        paras = []
        for para in model.parameters():
            paras.append(tuple(para.tolist()))
        print(tuple(paras))


