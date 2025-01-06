本文主要记录开发逐际动力机器人过程中的学习过程。

主要的仓库是：https://github.com/limxdynamics/pointfoot-legged-gym

该仓库主要继承了legged-gym环境，并使用了Isaac Gymenvs并行训练。

- [x] 了解legged-gym环境基本信息
- [ ] 了解wheel-legged的基本文件以及和legged-gym的关系
- [ ] 

***

## legged-gym

在这之前, 可以先读一下这个仓库对应的论文: Learning to Walk in Minutes Using Massively Parallel Deep Reinforcement Learnin, https://arxiv.org/pdf/2109.11978

这篇论文是ETH的研究团队于2021年9月在arxiv挂出的。

本文的基本情况： 

- 把data collection 和 policy update都放在了GPU中，可以避免CPU和GPU之间的通讯较长而导致训练速度下降。

- 使用的是PPO算法，有几个点需要注意：

  - Batchsize由单个机器人在单词policy update前运动的步数和机器人的数量决定:$B=n_{robots}n_{steps}$, 

    ​	关于batchsize的选择, 如果太小的话, 会导致policy update时出现更多的噪音现象, 不够连续光滑. 如果太大, 则里面重复的数据会比较多, 导致浪费更新过程, 降低训练速度.

    ​	此外, GAE对于$n_{steps}$也有依赖性, $n_{steps}$体现了一个轨迹，它必须有一定的时间连续性, 如果$n_{steps}$低于某个阈值, 算法就无法学习到最优的解。Reset，一般是机器人摔倒了需要重置，或者走了一定步数上限后重置以生成新的轨迹。

  - reset会带来一定的问题，PPO中的critic是在无限视野（infinite horizen）下工作的，用来预测无限长步数后的奖励如何的，引入reset会打断critic的工作条件，导致它的性能下降。

    因此有必要分析下重置的情况：

    - 第一种是基于失败或达成目标的重置

      ​	这种重置对于Critic来说好预测，可以根据获取的状态或者奖励了解到自己是成功还是失败。

    - 第二种是基于上限步数或者超时的重置

      ​	因为在观测中并不会提供步数/时间的信息，所以critic无法预测这类的重置，导致其对未来的预测出现偏差。

  - 改进的方法如下：

    - 在接口里增加一个信息，区分终止并重置的原因。
    - 如果是因为上限步数/超时导致的终止和重置，就使用critic预测的未来奖励来近似无限步后的奖励。



本文把框架应用在了legged-robot上，本文的几个新idea如下：

- 课程学习

  由于机器人的场景较多，会先从简单的平地开始训练，然后再逐步转移到复杂的台阶上。

- 观测空间，动作和奖励的设计

  观测空间包括：基本线性和角速度、重力矢量的测量、关节位置和速度、策略选择的先前操作，最后，从机器人基本周围的网格中采样的 108 次地形测量。

  动作空间是机器人各个关节的目标位置，经过一个PD控制器后变成各个关节的力矩。

  奖励如下表所示，其中成功跟踪水平方向的速度和绕着z轴（垂直地面）的话就是正向奖励，对z轴方向的速度或者绕着水平轴方向的旋转，就是惩罚，为了让动作更加流畅，所以对关节扭矩、关节加速度、关节目标更改和碰撞都设置了惩罚，最后最右边一排的权重里有一个$dt$，目的是鼓励机器人运行时间长一些。

  ![image-20250105204008285](/home/ubuntu/.config/Typora/typora-user-images/image-20250105204008285.png)

- sim2real的gap

  实际机器人上会有外力干扰和摩擦力等仿真里没有考虑的因素，有以下几种提升sim2real性能的方法。

  - 在仿真时，给观测到的数据加入了一定的噪音。让实际机器人能应对实际传感器的误差。

    <img src="/home/ubuntu/.config/Typora/typora-user-images/image-20250105223500001.png" alt="image-20250105223500001" style="zoom:67%;" />

  - 仿真时给机器人一个随机的冲击力。比如在机器人的x和y方向上加一个力，使得在对应方向上的加速度突然达到$1m/s^2$。可以让实际机器人抵抗各类突发的干扰，比如碰撞。

  - 仿真时地面设定摩擦系数，在$[0.5, 1.25]$之间随机初始化。可以让实际机器人适应不同的地面。



最后就是实验结果，可以在原文中看。

这里直接总结一下实验结果：并行的机器人数量太少的时候，会导致数据离独立同分布的假设偏离较大，训练效果不好；当batchsize一定时并行的机器人数量太多，会导致机器人仿真步数太少，导致数据连续性不够强，性能也会下降。

此外，增加机器人数量可以降低仿真时间。

***

了解了该仓库的算法思路后，就可以分析其工程代码了。

- legged_gym文件树

> 📁 legged_gym
> ├──📁 envs
> │   ├──📁 base
> │		├── 📄 base_config.py
> │		├── 📄 base_task.py
> │		├── 📄legged_robot.py
> │		└── 📄 legged_robot_config.py
> |
> │   ├──📁a1
> │   ├──📁...
> │   └──📄 __init__.py
> │
> |
> ├── 📁 scripts
> │   ├── 📄 play.py
> │   └── 📄 train.py
> │
> │
> ├── 📁 tests
> │   └── 📄 test_env.py
> │
> │
> ├── 📁 utils
> │   ├── 📄 __init__.py
> │   ├── 📄 helper.py
> │   ├── 📄logger.py
> │   ├── 📄 math.py
> │   ├── 📄 task_registry.py
> │   └── 📄 terrian.py
> |
> |
> └── 📄 __init__.py

官方给出了一个基本使用说明：

> 1. Each environment is defined by an env file (`legged_robot.py`) and a config file (`legged_robot_config.py`). The config file contains two classes: one containing all the environment parameters (`LeggedRobotCfg`) and one for the training parameters (`LeggedRobotCfgPPo`).
> 2. Both env and config classes use inheritance.
> 3. Each non-zero reward scale specified in `cfg` will add a function with a corresponding name to the list of elements which will be summed to get the total reward.
> 4. Tasks must be registered using `task_registry.register(name, EnvClass, EnvConfig, TrainConfig)`. This is done in `envs/__init__.py`, but can also be done from outside of this repository.

***

## wheel-legged如何继承了legged-gym

逐际动力的机器人仓库：https://github.com/limxdynamics/pointfoot-legged-gym

- 关键文件树
📁 legged_gym in pointfoot-legged-gym
├── 📁 envs
│   ├── 📄 __init__.py
│   └── 📁 pointfoot
│       ├── 📁 flat
│       │   └── 📁 WF
│       │       └── 📄 pointfoot_flat_config.py
│       │
│       ├── 📁 mixed_terrian
│       │   └── 📄 pointfoot_rough_config.py
│       │
│       └── 📁 WF
│           └── 📄 point_foot.py
|
|
├── 📁 scripts
│   ├── 📄 export_policy_as_onnx.py
│   ├── 📄 play.py
│   └── 📄 train.py
|
|
├── 📁 tests
│   └── 📄 test_env.py
|
|
├── 📁 utils
│   ├── 📄 __init__.py
│   ├── 📄 helper.py
│   ├── 📄 logger.py
│   ├── 📄 math.py
│   ├── 📄 task_registry.py
│   └── 📄 terrian.py
|
|
└── 📄 __init__.py

首先，逐际动力将wheel-legged的机器人直接放在了\legged_gym\envs\WF\point_foot.py里，这里包含了机器人的全部函数，比如reset, step, get_observation, compute_reward, check_termination, render, 等等。

需要注意的是，逐际动力并没有继承原来legged_gym里的基础机器人类BaseTask或者LeggedRobot，而是从头自己写的。



使用的机器人训练参数配置，则分别放在了同一个文件夹路径下的`flat`和`mixed_terrain`中，因为训练的环境有平地和台阶两种，这里逐际动力并没有使用课程学习，每一次只能使用一个环境，所以配置文件也是分开写的，分别是`flat\WF\pointfoot_flat_config.py`和`mixed_terrain\pointfoot_rough_config.py`。 

这里继承了leggeg_gym的BaseConfig，这部分代码量少，需要修改的也比较少，所以他们直接继承了。



在envs/__init__.py中，将wheel-legged环境给注册了。

经过注册后，就可以使用scripts/train.py来训练了。具体的注册以及注册后如何指定wheel-legged来训练的过程我在这里不详细展开，当作一个黑盒即可。



Q：如何修改奖励函数？
A：通过前面分析可知，以平地环境为例子，则找`legged_gym/envs/flat/WF/pointfoot_flat_config.py`，在这里找到PointFootFlatCfg.rewards，就可以看到奖励函数的设定了。



Q：如何修改PPO网络的参数？

A：以台阶环境为例，找到`legged_gym/envs/pointfoot/mixed_terrain/pointfoot_rough_config.py`，找到PointFootRoughCfgPPO，就可以看到PPO的参数了。



可能是逐际动力还没考虑让wheel-legged机器人在台阶环境里训练，所以默认没有给它设计台阶环境的配置文件，只能在平地上训练。但经过我们分析文件结构后，我们可以自己改写。





