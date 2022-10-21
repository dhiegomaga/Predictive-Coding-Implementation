# Predictive Coding Model

## Bachelor Thesis

This project was the base of my Bachelor's Thesis, mentored by [Professor Reinhold von Schwerin](https://studium.hs-ulm.de/de/users/142412) and Professor [Ronald Blechschmidt](https://studium.hs-ulm.de/de/users/617327), during my stay at the Technische Hochschule Ulm. 

[Download Final Thesis file](THU_Thesis-final.pdf)

## Overview

This repository contrains an implementation of the paper *An Approximation of the Error Backpropagation Algorithm in a Predictive Coding Network with Local Hebbian Synaptic Plasticity, Whittington, James CR and Bogacz, Rafal [2017]* - [link](https://www.mitpressjournals.org/doi/full/10.1162/NECO_a_00949). 

Predictive Coding is an alternative approach to artificial neural networks, inspired by theories of brain function. The network is structured in a hierarchical fashion with multiple layers (similar to deep learning), in which bottom-most layers receive *sensory input*, while the higher layers are responsible for representing the underlying *hidden causes* of such inputs (i.e. the inferred structure of the real world which gave rise to such input, i.e. explain the input). 

Meanwhile, top-bottom (feedback) connections generate the predicted input given the hidden causes encoded in the higher layers, which are then compared with the actual input. Finally, their difference (the prediction error) is transmitted through bottom-up (forward) connections, adjusting the actual valued of the hidden causes such that they better explain the sensory information. 

There are many flavors of the Predictive Coding framework, and one in particular is a simple classifier for a static input network (that is, the input data does not contain a temporal dimension). 

## Run Latest Model 

We compare the performance of a typical Backprop network againt the Predictive Coding implementation, on the Imagenet dataset. 

**Run all the commands below from the root folder**

### Reduced (64x64) ImageNet

1. Download the `Train(64x64) part1`, `Train(64x64) part2` and `Val(64x64)` (select `npz format`) from the [imagenet website](https://image-net.org/download-images). Extract inside `datasets/imagenet-64x64/`.

2. (optional) Create subsampled dataset (select desired class indices modifying `DESIRED_CLASSES` in the file `reduce-dataset.py`) and then 

```bash
python datasets/imagenet-64x64-reduced/reduce-dataset.py
```

3. Update the variable `NUM_CLASSES` in `examples/imagenet-64x64.py` to match the number of classes selected on previous step

4. Train the backpropagation + predictive coding networks

```bash
python -W ignore examples/imagenet-64x64.py
```

### "Full" image size (224x224) ImageNet

1. Download the entire ImageNet dataset (from somewhere) and update the variable `FOLDER` in the file `examples/imagenet-224x224.py` to match the location of the dataset. 

2. (optional) Select only some folders of some classes from the dataset, and put them inside the folder `datasets/imagenet-reduced/train/` and `datasets/imagenet-reduced/val/`. 

4. Train the backpropagation + predictive coding networks

```bash
python -W ignore examples/imagenet-224x224.py
```

### Experiment Sequence 

1. For 50 classes: 

```bash
./experiments/ImageNet_50_classes_224x224/run.bash | tee -a results/ImageNet_50_classes_224x224/log.txt
```

- Or, using `tmux`: 

```bash
tmux
```

```bash
./experiments/ImageNet_50_classes_224x224/run.bash | tee -a results/ImageNet_50_classes_224x224/log.txt
```

Detach from session with `Ctrl+B` and then `D`

- To reattach after logging off: 

```bash
tmux attach
```
