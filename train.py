import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
import pandas as pd
import os

# -------------------------
# 1. Custom Dataset Loader
# -------------------------
class DroneDataset(Dataset):
    def __init__(self, csv_file, img_dir, transform=None):
        self.labels = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.labels.iloc[idx, 0])
        image = Image.open(img_path).convert("RGB")
        label = self.labels.iloc[idx, 1]  # class index
        if self.transform:
            image = self.transform(image)
        return image, label


# -------------------------
# 2. Transformations
# -------------------------
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

# -------------------------
# 3. Load Dataset
# -------------------------
train_dataset = DroneDataset(
    csv_file="data/labels.csv", 
    img_dir="data/images", 
    transform=transform
)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

# -------------------------
# 4. Define Model (Simple CNN using pretrained ResNet18)
# -------------------------
model = models.resnet18(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, 4)  # 4 classes: left, right, forward, stop

# -------------------------
# 5. Training Setup
# -------------------------
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# -------------------------
# 6. Training Loop
# -------------------------
epochs = 5
for epoch in range(epochs):
    running_loss = 0.0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    print(f"Epoch {epoch+1}/{epochs}, Loss: {running_loss/len(train_loader):.4f}")

# -------------------------
# 7. Save Trained Model
# -------------------------
torch.save(model.state_dict(), "drone_nav_model.pth")
print("✅ Model saved as drone_nav_model.pth")
