# Trains backprop on imagenet dataset 
# Dataset link: http://www.image-net.org/download-images
# Extracted .npz files should go inside dataset/ folder
# RUN THIS FROM 'examples' folder

import numpy as np
from matplotlib import pyplot as plt
from sklearn.utils import shuffle
import datetime

# tensorflow etc
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import sys
sys.path.insert(0,'..')
from snn import util

# Dataset Parameters
CLASSES = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19] 
DATASET_BATCH_COUNT = 10
SUB_MEAN=True
IMAGE_SIZE = 32
VALID_PERC = 0.2

# Train parameters
BATCH_SIZE = 16
EPOCHS=15
DATA_PERC = 0.2
LR = 0.001

def get_images(data, img_size, subtract_mean=False):
    # Returns the dataset with image format, instead of flat array
    # Useful for convolutional networks

    # Normalize
    data = data/np.float32(255)
    
    if subtract_mean:
        mean_image = np.mean(data, axis=0)
        data -= mean_image

    img_size2 = img_size * img_size

    data = np.dstack((data[:, :img_size2], data[:, img_size2:2*img_size2], data[:, 2*img_size2:]))
    data = data.reshape((x.shape[0], img_size, img_size, 3)).transpose(0, 1, 2, 3)

    return data

def select_classes(x,y, CLASSES):
    indices = []
    for label in CLASSES:
        rows = [i for i, x in enumerate(y) if x == label]
        indices.extend(rows)

    x = x[indices, :]
    y = y[indices]

    return x, y

# Load data
dataset = None
multiple_files = True
y =np.zeros((0,))
x = np.zeros((0,IMAGE_SIZE*IMAGE_SIZE*3))

if multiple_files:
    count = 6# set to 10 when training on the full dataset
    prefix = 'train_data_batch_'
    for i in range(1, count+1):
        name = prefix + str(i) + '.npz'
        dataset = np.load('../datasets/'+name)
        x_batch = dataset['data']
        y_batch = dataset['labels']

        # Select only certain classes
        x_batch,y_batch = select_classes(x_batch,y_batch, CLASSES)

        y = np.concatenate([y, y_batch], axis=0)
        x = np.concatenate([x, x_batch], axis=0)

else:
    dataset = np.load('../datasets/val_data.npz')
    x = dataset['data']
    y = dataset['labels']

    # Select only certain classes
    x,y = select_classes(x,y, CLASSES)

# Subtract 1 from labels 
y = np.array([i-1 for i in y])

# Shuffle
x, y = shuffle(x, y)

# Convert x to images (optional, use for convolutions)
x = get_images(x, IMAGE_SIZE, subtract_mean=SUB_MEAN)
if not SUB_MEAN: 
    # show image sample
    plt.imshow(x[0], interpolation='nearest')
    plt.show()

# Separate train and validation data
x_train = []
y_train = []
x_valid = []
y_valid = []
if VALID_PERC <= 1.0 and VALID_PERC>0:
    train_index = int(x.shape[0]*(1-VALID_PERC))
    x_train = x[:int(train_index*DATA_PERC)]
    y_train = y[:int(train_index*DATA_PERC)]
    x_valid = x[train_index:]
    y_valid = y[train_index:]

# One hot encode y
num_classes = len(CLASSES)
y_train = keras.utils.to_categorical(y_train, num_classes)
y_valid = keras.utils.to_categorical(y_valid, num_classes)

# Define model
model = Sequential([
  layers.Input(shape=(IMAGE_SIZE,IMAGE_SIZE,3)),
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(128, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(256, 3, padding='same', activation='relu'),
  layers.Conv2D(256, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(512, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Flatten(),
  layers.Dense(1024, activation='relu'),
  layers.Dropout(0.3),
#   layers.Dense(500, activation='relu'),
#   layers.Dropout(0.3),
  layers.Dense(num_classes, activation='softmax')
])

opt = keras.optimizers.Adam(learning_rate=LR)
model.compile(optimizer=opt,
              loss=keras.losses.CategoricalCrossentropy(from_logits=False),
              metrics=['accuracy', keras.metrics.RootMeanSquaredError()])

model.summary()

# Get time before training
t_start = datetime.datetime.now()
print("Starting timer")

result = model.fit(
  x=x_train,
  y=y_train,
  batch_size=BATCH_SIZE,
  validation_data=(x_valid,y_valid),
  epochs=EPOCHS
)
accuracy_txt = 'accuracy'
print("Train_loss=", end="", flush=True)
print(result.history['root_mean_squared_error'])
# print(result.history['loss'])

print("Train_accuracy=", end="", flush=True)
print(result.history[accuracy_txt])

print("Valid_loss=", end="", flush=True)
print(result.history['val_root_mean_squared_error'])
# print(result.history['val_loss'])

print("Valid_accuracy=", end="", flush=True)
print(result.history['val_'+accuracy_txt])

# Get time after training
t_end = datetime.datetime.now()
elapsedTime = (t_end - t_start )
dt_sec = elapsedTime.total_seconds()

print(f"Training time per epoch: {dt_sec/EPOCHS}")
