import torch
print(torch.cuda.is_available())  # Trueが返るはず
print(torch.cuda.get_device_name(0))  # GPU名が表示される
