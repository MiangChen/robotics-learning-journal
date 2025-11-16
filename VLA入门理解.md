这个文档主要面向第一次接触VLA的小白, 假设之前对于LLM之类的有一定了解, 但是并不太深入. 因此在学习VLA之前, 需要先了解一定的背景知识, 在下面我们会先介绍下representatin-learning models, vsiual language models, pre training, 在做什么事情. 然后再引入VLA领域的论文RT系列.

该比较的目的:

- [ ] VLA的基础
  - 发展历史
  - 原理
  - 应用场景
  - 优势和劣势

- [ ] RT系列论文解读
- [ ] OpenVLA解读
- [ ] 关注点：集群机器人/移动机器人/有限资源平台
- [ ] 上手实验
- [ ] 个人总结

# VLA的基础

## 发展历史



## Representation-learning models 

### 经典论文:

CLIP: https://proceedings.mlr.press/v139/radford21a

### **特征**:

- **目标**：学习两个模态（视觉和语言）的**共同嵌入空间**（common embeddings）。
- 输入输出：
  - 输入：图像（视觉模态）和文本（语言模态）。
  - 输出：每个模态的嵌入表示，通常在一个共享的向量空间中。

### 训练流程：

### **1. 数据准备**

CLIP 使用大量的图像-文本对作为训练数据。这些对通常由描述性文本与相应的图像组成。例如：

- 图像：一张猫的照片。
- 文本：描述该图像的语句，如“a cute cat sitting on the couch”。

### **2. 模态特征提取**

CLIP 的模型分为两个部分：

1. 视觉编码器（Vision Encoder）：
   - 使用卷积神经网络（CNN，如 ResNet）或视觉变换器（Vision Transformer, ViT）提取图像的特征。
   - 输出：图像的特征表示向量。
2. 文本编码器（Text Encoder）：
   - 使用语言模型（如 Transformer 架构）提取文本的特征。
   - 输出：文本的特征表示向量。

这两个编码器被独立训练，同时会确保它们的输出在同一共享向量空间中。

### **3. 嵌入表示**

将图像和文本通过各自的编码器映射到同一个 **d 维共享嵌入空间**中：

- 图像嵌入：$$v∈Rd, \mathbf{v} \in \mathbb{R}^d,v∈Rd$$
- 文本嵌入：$t∈Rd,\mathbf{t} \in \mathbb{R}^d,t∈Rd$

### **4. 对比学习（Contrastive Learning）**

#### **核心思想**

- 目标是让相关的图像-文本对的嵌入向量在共享空间中尽可能接近，而不相关的对尽可能远离。

#### **具体实现**

- 相似度计算：
  - 使用余弦相似度衡量图像嵌入 $\mathbf{v}$ 和文本嵌入 $\mathbf{t}$ 的关系：$ \text{sim}(\mathbf{v}, \mathbf{t}) = \frac{\mathbf{v} \cdot \mathbf{t}}{\|\mathbf{v}\| \|\mathbf{t}\|}$
- 正样本对（Positive Pairs）：
  - 同一图像和描述该图像的文本组成正样本对。
- 负样本对（Negative Pairs）：
  - 随机选择其他图像或文本组成负样本对。

#### **损失函数：对比损失（Contrastive Loss）**

CLIP 使用**跨熵损失**（cross-entropy loss）来优化正负样本对的区分：

- 假设有 NNN 个图像-文本对，图像嵌入 vi\mathbf{v}_ivi 和文本嵌入 ti\mathbf{t}_iti，则损失函数为：

$$\begin{align} \mathcal{L} &= -\frac{1}{2N} \sum_{i=1}^{N} \bigg[\log \frac{\exp(\text{sim}(\mathbf{v}_i, \mathbf{t}_i))}{\sum_{j=1}^{N} \exp(\text{sim}(\mathbf{v}_i, \mathbf{t}_j))} + \log \frac{\exp(\text{sim}(\mathbf{v}_i, \mathbf{t}_i))}{\sum_{j=1}^{N} \exp(\text{sim}(\mathbf{v}_j, \mathbf{t}_i))} \bigg] \end{align}$$

- 解释：
  - 第一项：对于每个图像，最大化与正确文本匹配的概率。
  - 第二项：对于每个文本，最大化与正确图像匹配的概率。

编码器通过神经网络参数学习到如何将图像和文本的语义信息压缩到这些向量中。

***

## **Visual Language Models**

### 经典论文: 

Flamingo: 

BLIP: 

PaLI-X: https://arxiv.org/pdf/2305.18565

PALM-E: https://arxiv.org/pdf/2303.03378

### 特征: 

- 目标: 学习输入的图像和文本之间的联系, 并给出针对输入的文本回答
- 输入输出:
  - 输入: 图像（视觉模态）和文本（语言模态）。
  - 输出: 针对输入的文本回答

### 训练流程:

### **1. 数据准备**

Visual Language Models 通常需要多模态数据，其中图像与文本对的描述包含：

- 图像：视觉模态的输入（例如一张含物体的图片）。
- 文本：相应的自然语言描述（例如“a man riding a horse on the beach”）。
- 可选：有些任务可能还需要额外的上下文（如问题-回答对）。

这类模型需要数据规模较大，可能包括从网络爬取的多模态数据或专门构建的数据集。

### **2. 模态特征提取**

Visual Language Models 通常包含以下两个核心编码器：

1. **视觉编码器（Vision Encoder）**：
   - 使用预训练的视觉模型（如 Vision Transformer, ViT 或 CNN）。
   - 提取图像的视觉特征 $\mathbf{v}$，并通过一个投影层将其映射到模型的隐空间。
2. **语言编码器（Text Encoder）**：
   - 使用预训练的语言模型（如 GPT 或 Transformer-based 模型）。
   - 将输入的文本（如问题或描述）编码为语言特征 $\mathbf{t}$。

此外，为了进行多模态融合，视觉特征通常会被编码为与语言特征兼容的形式（例如序列化或转换为 token）。

### **3. 多模态融合**

将视觉特征和语言特征整合以实现多模态信息的交互。这是 Visual Language Models 的核心步骤。

- **方法**：
  1. 序列化融合：
     - 将视觉特征序列化为类似文本的 token，并与语言 token 拼接。
  2. 注意力机制（Cross-Attention）：
     - 使用跨模态注意力机制，让文本特征和视觉特征相互作用。
     - 例如，文本 token 能关注到图像的某些区域（通过位置编码或区域特征）。
- **输出**：
  - 融合后的多模态表示，作为生成器的输入。

### **4. 生成模块**

Visual Language Models 的输出通常是**自由形式文本**，由生成模块完成：

1. **基于解码器（Decoder-based Models）**：
   - 使用语言生成模型（如 GPT 风格的 Transformer 解码器）。
   - 接受融合后的多模态表示，生成自然语言文本。
2. **生成过程**：
   - 文本以逐词或逐 token 的方式生成。
   - 解码方法可以是贪婪解码、采样或 beam search 等。

Visual Language Models 使用的训练目标包括：

1. **语言建模损失（Language Modeling Loss）**：
   - 给定输入（图像、文本），预测下一个 token。
   - 损失函数为交叉熵损失：

### **5. 训练**

Visual Language Models 使用的训练目标包括：

1. **语言建模损失（Language Modeling Loss）**：
   - 给定输入（图像、文本），预测下一个 token。
   - 损失函数为交叉熵损失：

​	$\mathcal{L} = -\frac{1}{N} \sum_{i=1}^{N} \log P(y_i \mid y_{<i}, \mathbf{v}, \mathbf{t})$

​	其中$ y_i$ 是第 $i$ 个生成 token。

2. **任务特定损失（Optional）**：
   - 例如，视觉问答任务可以引入回答准确性的指标。

***

## Pre training

预训练分为两大主要方向: 

1. **预训练的视觉表示（visual representations）**：
   - 目标：通过预训练的视觉模型（如图像编码器），对机器人摄像头观测到的图像进行特征提取。
   - 方法：
     - 监督学习（supervised learning）：
       - 利用 ImageNet 分类等任务的预训练模型（如 CNN、Vision Transformers）。
     - 数据增强（data augmentation）：
       - 对训练数据进行增强，如图像翻转、裁剪、颜色调整等，使模型学习到更稳健的视觉特征。
2. **预训练的语言模型（pre-trained language models, LLMs）**：
   - 目标：通过语言模型的能力，辅助机器人完成高层次任务。
   - 方法：
     - 作为指令编码器（instruction encoder）：
       - 利用 LLM 将自然语言的指令转化为机器人可理解的编码，帮助机器人理解任务需求。
     - 作为高层次规划工具（high-level planning）：
       - 使用 LLM 提供高层次任务规划，指导机器人如何分步骤完成复杂任务。比如Code as Policies

***

​	之前常见的预训练模型就是这两类, 一类是处理输入的图像信息, 一个是处理输入的文本.  

​	在以前的机器人框架中, 经常看到多层的框架, 首先用预训练好的视觉模型, 处理相机看到的场景, 通过分割, 检测等提取出场景的文本描述, 这些信息可以和用户的命令一起输入给预训练的语言模型, 再得到输出的控制指令. 

​	那么, 结合之前提到的VLM, 自然而然会有一个想法, 是不是就可以把这两个预训练模型给结合起来, 用一个模型就完成呢?  

​	这就是RT2做的事情, 它的movivation就是结合已有的这两类预训练模型来做机器人控制, 此时的模型就叫做VLA了. 但是在阅读RT2之前, 我们最好先了解下它的前一代模型RT-1的思路.



## 综述

Towards Generalist Robot Policies: What Matters in Building Vision-Language-Action Models： https://arxiv.org/abs/2412.14058

本文详细讨论了VLA领域的论文研究情况。

本文的作者提出了一个统一的RoboVLMs框架，可以用一个统一框架来实验，并回答以下几个问题：

- why 为什么VLA是一种高效的机器人策略生成器。
- which 哪一种VLM最适合构建VLA
- how 如何VLA的架构
- when 何时加入额外的数据给VLA微调







## RT-1

RT-1: https://arxiv.org/pdf/2212.06817

![image-20250104200732718](assets/rt1.png)

### 训练流程: 

### 1. 数据准备

#### a. 数据收集

RT-1需要使用同时包含图像, 相应自然语言指令和动作序列的数据集。

数据格式如下: $ i,{(x_j,a_j)}_{j=0}^T $

其中:

- $i$表示语言指令 instruction

- $x_j$表示$t=j$时刻的图像

- $a_j$表示$t=j$时刻采取的动作

通过这种数据格式，可以看出RT-1采用了模仿学习（Imitation Learning）的思路。在一个连续的时间段内采样数据，使其形成一个完整的轨迹，从而训练模型模仿正确的动作序列。

### 2. 模型架构

RT-1的架构结合了先进的图像编码器和语言理解模块，通过条件化机制实现视觉与语言的融合。

#### a. 图像编码器：EfficientNet-B3

- **EfficientNet** 是一种高效的卷积神经网络架构，能够在保持高准确率的同时显著减少参数量和计算量。EfficientNet-B3是其系列中的一个变种，适用于中等规模的任务。
- **MBConv块**：EfficientNet使用Mobile Inverted Bottleneck Convolution（MBConv）块，这种结构通过深度可分离卷积提高计算效率。

#### b. 语言嵌入：Universal Sentence Encoder

- **Universal Sentence Encoder（USE）** 将自然语言指令转换为高维嵌入向量，捕捉语义信息。这些嵌入向量用于指导图像编码器提取与任务相关的图像特征。

#### c. 条件化机制：FiLM层

- **FiLM（Feature-wise Linear Modulation）层**：将语言嵌入向量作为输入，生成仿射变换参数（缩放和偏移），用于调整图像编码器中间层的特征。
- **身份初始化**：为了避免打断预训练网络的中间激活，FiLM层的全连接层（如fc和hC）的权重初始化为零，使其在初始阶段表现为恒等映射，保持预训练权重的功能不变。

#### d. vision-language tokens

- **特征图**: 经过EfficientNet和USE处理后, 得到9tokens x 9tokens x 512层的特征数据

#### e. TokenLearner压缩

- **TokenLearner**：一种元素级注意力模块，能够将大量的视觉令牌映射到更少的令牌，以减少Transformer需要处理的令牌数量，加速推理过程。
- **压缩过程**：从9x9 81个视觉令牌压缩为8个最终令牌，保留关键信息，提升推理速度。

#### f. Transformer处理

- **Transformer架构**：采用仅解码器（decoder-only）的序列模型，包含8层自注意力机制，总参数量为1900万。
- **输入令牌**：将每张图像压缩后的8个令牌与历史图像(6张图)的令牌拼接，总计48个令牌（包括位置编码），输入到Transformer中。
- **输出动作令牌**：Transformer生成与任务相关的动作令牌，指导机器人执行具体动作。

#### g. 动作生成与编码

- 动作离散化：将动作维度离散化为256个箱（bins）。具体动作包括：
  - **手臂运动**：7个变量（x, y, z, roll, pitch, yaw, 开合抓手）。
  - **基座运动**：3个变量（x, y, yaw）。
  - **模式切换**：1个离散变量，用于切换控制臂、基座或终止任务。
  
- **动作编码**：每个动作变量维度映射到256个离散值中的一个，形成离散的动作令牌。这么做的原因是离散化后的动作空间较为固定，便于模型学习和优化。
  
  动作编码是一个很重要的思路, 为了便于理解动作编码, 这里可以举一个例子:
  
  ​	假设机械臂的x位置范围是**0.0米到1.0米**。那么经过离散化后, 区间宽度 = (1.0 - 0.0) / 256 ≈ 0.0039m, 假设实际的数据是运动到**目标值**：0.75米, 则**区间编号** = floor((0.75 - 0.0) / 0.0039) = floor(192) = 192, 把这个192给模型学习, 而不是把原始的0.75m给模型.
  
  ​	假设在应用阶段, RT-1给出的x是100, 可以解码出实际物理距离 = 100/256 * (1.0 - 0.0) ≈ 0.39m

***

​	通过RT-1的工作流程可以发现，其设计也包含了预训练的理念。具体而言，EfficientNet-B3是在ImageNet数据集上进行预训练的。然而，经过ImageNet训练的模型主要用于分类任务，即输入图片后输出分类标签。RT-1通过FiLM层对文本指令进行编码，从而引导模型关注EfficientNet检测到的不同物体。

​	实际上，RT-1中FiLM与EfficientNet的结合思路已经与视觉-语言模型（VLM）非常接近。那么，为什么不进一步直接采用VLM呢？在RT-1取得了不错的效果后，Google的研究人员继续深入研究，结合新的思路，诞生了RT-2。



## RT-2

​	RT-2的思路如下图所示. 

![image-20250104202642220](assets/rt2.png)

​	看到这个框架图, 可能会有非常多的问题, 这和RT-1看起来差别太大了, 那么接下来一步一步的分析。

​	首先是RT-2是中间的灰色框，里面又包含一个ViT和LLM，分别是前面基础知识里提到的VLM的视觉编码器和语言编码器。在后续的分析中，我们不再单独区分这两者，直接看作一个整体，叫做VLM就可以。

​	关于VLM的选择, RT2使用的VLM是PaLI-X和PALM-E, 可以注意下作者单位, RT-2的大团队是GoogleDeepind, PaLI-X是GoogleResearch, PALM-E是Robotics at Google和Google Research, 是Google的不同部门, 因此在这几个论文里也可以看到重复出现的作者, 他们保持紧密的合作, 也是他们使用PALM和PaLI-X的原因.

​	为了让VLM更好的对齐机器人任务, 也就是输入文本和场景图片后输出机器人动作, 需要引入和RT-1一样的机器人数据, 也就是左下角的那张图所示的，这里继续延续RT-1的离散化动作思路, 让VLM继续输出原始的token, 也就是图片里那些灰色的且不经过翻译完全看不懂的编码数字。

​	但仅仅用实际机器人数据微调是不行的, 实际机器人的数据和VLM之前pre trained的那些数据差距太大, 而且实际机器人的数据因难以获取，所以数量也比较少，硬要微调的话可能会导致网络梯度过大, 从而网络崩溃。所以还需要加入一些别的数据共同训练, 这些数据就像左上角的两张所示, 就是一些互联网上爬取的图片以及对其中内容的回答。RT-2把这个方式叫做Co-Fine-Tune, Co是cooperate, 表示协同, 也就是通过网络上的大规模Visual-Question-Answer数据和机器人动作数据来共同微调VLM，当然，也不仅仅是为了防止网络崩溃，他们发现这样协同训练可以加强VLM的泛化能力。

​	通过上面这个微调VLM的流程可以很容易知道，这样微调出来的VLM的输出可能会与action无关。为了解决这个问题， RT-2采取了一个简单的方法，在输入是问机器人该做什么时，RT-2会对VLM的输出进行一个筛选，只输出其中与action相关的token，简单粗暴，他们把这个叫做Output Constraint，不过他们对此给出细节说明。

​	最后，VLM输出了一些action tokens，经过反编码，就可以变成实际物理世界的action，就可以直接把这些参数部署到机器人上了。

​	

​	至此，就已经完成了RT-2的框架分析。虽然这个框架看似简单，但这就是VLA的出发点。后续我们可以继续介绍更新的VLA论文。

***

## OpenVLA

论文链接：https://arxiv.org/abs/2406.09246

该论文发表于2024年6月，研究团队主要来自于斯坦福大学、加州伯克利、麻省理工，合作企业主要是Google Deepmind。	

![image-20250106220111470](assets/openvla.png)

过去VLA存在几个痛点：1. 大部分是闭源的，前面的RT-2模型就是闭源的 2. 过去的微调方法不够高效，模型也比较大，不方便迁移到新的机器人本体和别的任务上，不便于部署。

基于这两个问题，本文给出了一个全部开源的VLA，也就是论文名字OpenVLA的由来。

OpenVLA在训练上有一些细节：

- VLM的基础框架是Prismatic VLM，其visual encoder用了SigLIP和DinoV2两个模型，输入的图像会分别经过这两个模型，然后再结合到一起；用于将图像编码映射到语言模型里的projector是一个两层的MLP；语言模型是一个7B的Llama2。
- 采用了和RT-2一样的离散动作输出方式；在把VLM连续动作映射到256个离散值的时候，是用连续动作的1%到99%分位区间的值映射到0～255上，这样可以避免数据中的极端值扩大区间范围而导致大量数据堆积到较小的离散区间里。
- 由于LLama tokenizer只能提供100个特殊token来作为动作的token，不足256个，所以他们复用了一些低频的token来作为动作的token。
- 使用的数据集主体是OpenX。
- 图像的尺寸统一采用了224x224，并且他们发现如果把图像分辨率提高到384x384并不能带来性能提升，并且时间还会慢3倍。
- 传统的VLM微调过程中一般会冻结vision encoder，本次训练没用采用冻结VLA中的vision encoder部分，并且发现如果微调vision encoder的话可以提升VLA的性能。
- 过去LLM和VLM对数据集的训练只用1或2个epoch，本次VLA的训练采用了更多的epoch，直到成功率到达95%才停止，最终使用了27个epoch。
- 本次采用的是固定学习率，数值是$2*10^{-5}$，他们发现使用warmup的方式不会提升性能。



# 开源的仿真环境

CALVIN

SimplerEnv：
