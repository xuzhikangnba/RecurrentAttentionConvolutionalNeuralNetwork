"""Main entry point for doing all stuff."""
from __future__ import division, print_function

import argparse
import warnings
import torch.optim as optim
import networks as net
from manager_coords import Manager, Optimizers

# To prevent PIL warnings.
warnings.filterwarnings("ignore")

FLAGS = argparse.ArgumentParser()
FLAGS.add_argument('--arch',
                   choices=['vgg', 'resnet', 'densenet'],
                   help='Architectures', default='vgg')
FLAGS.add_argument('--mode',
                   choices=['finetune', 'eval'],
                   help='Run mode', default='finetune')
FLAGS.add_argument('--num_outputs', type=int, default=-1,
                   help='Num outputs for dataset')
# Optimization options.
FLAGS.add_argument('--lr', type=float,
                   help='Learning rate for parameters, used for baselines')
FLAGS.add_argument('--lr_decay_every', type=int,
                   help='Step decay every this many epochs')
FLAGS.add_argument('--lr_decay_factor', type=float,
                   help='Multiply lr by this much every step of decay')
FLAGS.add_argument('--finetune_epochs', type=int,
                   help='Number of initial finetuning epochs')
FLAGS.add_argument('--batch_size', type=int, default=32,
                   help='Batch size')
FLAGS.add_argument('--weight_decay', type=float, default=0.0,
                   help='Weight decay')

# Paths.
FLAGS.add_argument('--dataset', type=str, default='',
                   help='Name of dataset')
FLAGS.add_argument('--train_path', type=str, default='../data',
                   help='Location of train data')
FLAGS.add_argument('--test_path', type=str, default='../data',
                   help='Location of test data')
FLAGS.add_argument('--save_prefix', type=str, default='../checkpoints/',
                   help='Location to save model')
FLAGS.add_argument('--loadname', type=str, default='',
                   help='Location to save model')
# Other.
FLAGS.add_argument('--cuda', action='store_true', default=True,
                   help='use CUDA')


def main():
    """Do stuff."""
    args = FLAGS.parse_args()

    if args.arch == 'vgg':
        cnn = net.VGG
    elif args.arch == 'resnet':
        cnn = net.ResNet
    elif args.arch == 'densenet':
        pass
    else:
        raise ValueError('Architecture %s not supported.' % (args.arch))

    # Load the required model.
    model = net.APN2(args.num_outputs, cnn)

    if args.cuda:
        model = model.cuda()

    # Create the manager object.
    manager = Manager(args, model)

    # Perform necessary mode operations.
    if args.mode == 'finetune':
        assert args.lr and args.lr_decay_every

        # Get optimizer with correct params.
        params_to_optimize = list(model.apn1.parameters()) + list(model.apn2.parameters())
        optimizer = optim.Adam(params_to_optimize, lr=args.lr)
        optimizers = Optimizers(args)
        optimizers.add(optimizer, args.lr, args.lr_decay_every)

        manager.train(args.finetune_epochs, optimizers,
                      savename=args.save_prefix)
    elif args.mode == 'eval':
        # Just run the model on the eval set.
        manager.eval()

if __name__ == '__main__':
    main()
