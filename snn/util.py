import torch.nn
import torch
import csv
from os import system, name 
import numpy as np

# Onehot encode a 1 dim array to 2 dim array
def indices_to_one_hot(data, nb_classes):
    """Convert an iterable of indices to one-hot encoded labels."""
    targets = np.array(data).reshape(-1)
    M = np.eye(nb_classes)[targets]
    M += 0.03
    return np.minimum(0.97, M)
  
# define our clear function 
def clear(): 
  
    # for windows 
    if name == 'nt': 
        _ = system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 

def dRelu(x):
    return torch.gt(x, torch.zeros(x.shape, device=x.device)).type(x.type())

def dLinear(x):
    return torch.ones(x.shape).type(x.type())

def dSigmoid(x):
    sig_x = torch.nn.Sigmoid()(x)
    return sig_x*(1 - sig_x)

def Linear(x):
    return x

# Pre processing functions to make algorithm stable
def preLinear(x):
    return x

def preRelu(x):
    return x

def preSigmoid(x):
    return torch.log(x/(1 - x))

# Reads csv, first 2 columns are X, last column is Y
def read_csv(file):
    x_data, y_data= [],[]
    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(reader) # skip first line
        for row in reader:
            x_data.append(
                np.array([ float(row[0]), float(row[1]) ])
            )

            y_data.append(
                np.array([ float(row[2]) ])
            )
    
    return x_data, y_data

def normalize_dataset(data):
    """Normalizes a list of numpy arrays to the interval [0,1]
    """
    min_value = min([min(n) for n in data])
    data = [array-min_value for array in data]
    max_value = max([max(n) for n in data])
    return [array/max_value for array in data], min_value, max_value

def denormalize_sample(sample, min_value, max_value):
    """Applies the inverse of normalization to a single sample
    """
    return sample*max_value + min_value