
import torch
import torch.nn.functional as F
import torch.nn as nn
import numpy as np

def getFcModel(input_size, output_size, num_layers, neurons_per_layer):
    class FcModel(nn.Module):

        def __init__(self):
            super(FcModel, self).__init__()

            self.dropout1 = nn.Dropout(0.20)
            self.dropout2 = nn.Dropout(0.50)
            self.dropout3 = nn.Dropout(0.50)

            # 1 Layer
            if num_layers == 1:
                self.fc1 = nn.Linear(input_size, output_size) 

            # 2 Layers
            if num_layers == 2:
                self.fc1 = nn.Linear(input_size, neurons_per_layer) 
                self.fc2 = nn.Linear(neurons_per_layer, output_size)

            # Extra layers ... 
            if num_layers == 3:
                self.fc1 = nn.Linear(input_size, neurons_per_layer) 
                self.fc2 = nn.Linear(neurons_per_layer, neurons_per_layer) 
                self.fc3 = nn.Linear(neurons_per_layer, output_size)
                

        def forward(self, x):
            x = torch.flatten(x, 1) # flatten all dimensions except the batch dimension
            
            # 1 Layer
            if num_layers == 1:
                x = self.dropout1(x)
                x = self.fc1(x)

            # 2 Layers
            if num_layers == 2:
                # x = self.dropout1(x)
                x = self.fc1(x)
                x = F.relu(x)
                x = self.dropout2(x)
                x = self.fc2(x)

            if num_layers == 3:
                x = self.dropout1(x)
                x = self.fc1(x)
                x = F.relu(x)
                x = self.dropout2(x)
                x = self.fc2(x)
                x = F.relu(x)
                x = self.dropout3(x)
                x = self.fc3(x)

            return x

    model = FcModel()

    # Initialize model weights
    def init_weights(m):
        if isinstance(m, nn.Linear):
            torch.nn.init.xavier_uniform(m.weight)
            m.bias.data.fill_(0.01)

    model.apply(init_weights)

    return model

def train_TransferLearning_Simultaneous_Backprop_PC(
    epochs, 
    num_classes, 
    train_generator, 
    valid_generator, 
    model, 
    feature_extractor, 
    criterion, 
    optimizer, 
    device,
    print_every_n_batches):
    
    # Return metrics after training
    metrics = {
        'backprop_train_acc': [],
        'backprop_val_acc': [],
        'pc_train_acc': [],
        'pc_val_acc': []
    }

    for epoch in range(epochs):
        running_loss = 0.0
        prediction_list = []
        labels_list = []

        print(f'\nEpoch: {epoch}')

        # Activate dropouts, batch norm...
        model.train()
        feature_extractor.train()

        for i, (data, labels) in enumerate(train_generator):
            
            # Get samples
            data = data.to(device)
            labels = labels.to(device)
            labels_one_hot = F.one_hot(labels, num_classes=num_classes)

            # Zero model gradiants
            model.zero_grad() 

            # Compute features
            features = feature_extractor(data)

            # Comput model output
            prediction = model(features)

            # Calculate loss and gradiants
            loss = criterion(prediction, labels)
            loss.backward()

            # Apply gradients
            optimizer.step()

            # Get running loss
            running_loss += loss.item()

            # Store predictions
            max_index = prediction.max(dim = 1)[1]
            prediction_list.extend(list(max_index.to('cpu').numpy()))
            labels_list.extend(labels.to('cpu').numpy())

            # Calculate partial training accuracy
            if i % print_every_n_batches == print_every_n_batches-1:    # print every N mini-batches

                # Training metrics 
                acc_metric = np.equal(prediction_list, labels_list).sum()*1.0/len(prediction_list)

                print('batch num: %5d, (backprop) acc: %.3f | (pc) acc: ...' % 
                    (i + 1, acc_metric))

        # Finished epoch

        # Calculate validation accuracy and train accuracy for epoch

        acc_metric = np.equal(prediction_list, labels_list).sum()*1.0/len(prediction_list)

        prediction_list_valid = []
        labels_list_valid = []

        #   Disable dropouts: model.eval()
        model.eval()
        feature_extractor.eval()

        for data, labels in valid_generator:
            # Get samples
            data = data.to(device)
            labels = labels.to(device)

            # Compute features
            features = feature_extractor(data)

            # Comput model output
            prediction = model(features)

            # Calculate loss
            loss = criterion(prediction, labels)

            # Store predictions
            max_index = prediction.max(dim = 1)[1]
            prediction_list_valid.extend(list(max_index.to('cpu').numpy()))
            labels_list_valid.extend(labels.to('cpu').numpy())
            

        # Validation metrics 
        valid_accuracy = np.equal(prediction_list_valid, labels_list_valid).sum()*1.0/len(prediction_list_valid)

        # Print Loss and Accuracy 
        print('Epoch: %d, (backprop) loss: %.3f, acc: %.3f, val acc: %.3f | (pc) ...' % 
            (epoch + 1, running_loss / 2000, acc_metric, valid_accuracy))
        
        running_loss = 0.0
        prediction_list = []
        labels_list = []

        # Store metrics for epoch
        metrics['backprop_train_acc'].append(acc_metric)
        metrics['backprop_val_acc'].append(valid_accuracy)

    return metrics

def printMetrics(metrics):
    print("------------------------------------------------")
    print("End of training session\n")

    print("backprop_train_acc=", end="", flush=True)
    print(metrics['backprop_train_acc'])

    print("backprop_val_acc=", end="", flush=True)
    print(metrics['backprop_val_acc'])

    print("pc_train_acc=", end="", flush=True)
    print(metrics['pc_train_acc'])

    print("pc_val_acc=", end="", flush=True)
    print(metrics['pc_val_acc'])
