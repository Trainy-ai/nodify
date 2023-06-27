# Nodify Tensorboard Plugin

<p align="center">
  <img height='100px' src="./assets/trainy.png">
</p>

[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
![GitHub Repo stars](https://img.shields.io/github/stars/Trainy-ai/nodify?style=social)
[![](https://dcbadge.vercel.app/api/server/d67CMuKY5V)](https://discord.gg/d67CMuKY5V)

This is a tensorboard plugin by [Trainy](trainy.ai) to supplement the existing [PyTorch Profiler](https://pytorch.org/tutorials/intermediate/tensorboard_profiler_tutorial.html). This provides additional visualizations to effectively characterize traces for runs involving multiple GPUs. The plugin expects all traces to be collected using `torch.profile` and to be located in the same folder.

## Installation & Quickstart

Install tensorboard and the plugin.
```
pip install tensorboard
pip install nodify-plugin
```

Generate PyTorch profiler traces as shown [here](https://pytorch.org/tutorials/recipes/recipes/profiler_recipe.html) and bring up the tensorboard where your traces are living. A set of example logs are provided in this repo under `log/resnet18`

```
tensorboard --logdir log/resnet18/
```

Take a look at our [quickstart guide](https://github.com/Trainy-ai/nodify) to learn about the different graph views and how you can use them to debug your multinode training.

## Development

To view the plugin for development, create a virtual environment, install the requirements, and install the plugin.

```
python -m venv venv
. venv/bin/activate
pip install -e .
``` 

## Feature roadmap

A lot of the features on the roadmap use Meta's [Dynolog](https://developers.facebook.com/blog/post/2022/11/16/dynolog-open-source-system-observability/), [kineto](https://github.com/pytorch/kineto), and [holistic trace analyzer](https://pytorch.org/blog/trace-analysis-for-masses/).

* On-demand tracing and metrics through dynologger
* Recommendations for fixing multinode bottlenecks
* reading from logs stored on cloud object-stores (e.g. Amazon S3, Azure Blob) 