# 学术插图 AI 绘制工作流

本教程采用标准化工作流，将复杂的绘图任务拆解为「逻辑构建」与「视觉渲染」两个独立且互补的环节。通过利用 LLM 强大的逻辑推理能力来指导绘图模型的像素生成能力，产出符合 CVPR/NeurIPS 等顶刊标准的学术插图。

## 环境配置

```bash
# 1. 安装依赖
bash Draw/setup.sh

# 2. 编辑配置文件，填入 API Key
Draw/config_llm.json

# 3. 启动 ComfyUI
bash Draw/start.sh
# 访问 http://localhost:8188
```



---

## 工作流概览

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Step 1         │    │  Step 2         │    │  Step 3         │
│  The Architect  │ -> │  The Renderer   │ -> │  The Editor     │
│  逻辑构建       │    │  视觉渲染       │    │  交互式微调     │
│  (Gemini/GPT)   │    │  (Nano-Banana)  │    │  (自然语言编辑) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 步骤一：逻辑构建（The Architect）

**目标**：利用逻辑推理能力强的 LLM（如 Gemini 3 Pro, GPT-5, Claude 4.5）将论文内容转化为 `[VISUAL SCHEMA]`。

**核心理念**：将抽象的算法逻辑转化为绘图模型能够理解的「强硬」物理描述。

### Prompt 模板

```markdown
# Role
你是一位 CVPR/NeurIPS 顶刊的**视觉架构师**。你的核心能力是将抽象的论文逻辑转化为**具体的、结构化的、几何级的视觉指令**。

# Objective
阅读我提供的论文内容，输出一份 **[VISUAL SCHEMA]**。这份 Schema 将被直接发送给 AI 绘图模型，因此必须使用**强硬的物理描述**。

# Phase 1: Layout Strategy Selector (布局决策)
在生成 Schema 之前，请先分析论文逻辑，从以下**布局原型**中选择最合适的一个（或组合）：

1. **Linear Pipeline**: 左→右流向 (适合 Data Processing, Encoding-Decoding)
2. **Cyclic/Iterative**: 中心包含循环箭头 (适合 Optimization, RL, Feedback Loops)
3. **Hierarchical Stack**: 上→下或下→上堆叠 (适合 Multiscale features, Tree structures)
4. **Parallel/Dual-Stream**: 上下平行的双流结构 (适合 Multi-modal fusion, Contrastive Learning)
5. **Central Hub**: 一个核心模块连接四周组件 (适合 Agent-Environment, Knowledge Graphs)

# Phase 2: Schema Generation Rules
1. **Dynamic Zoning**: 根据选择的布局，定义 2-5 个物理区域 (Zones)
2. **Internal Visualization**: 必须定义每个区域内部的"物体" (Icons, Grids, Trees)，禁止使用抽象概念
3. **Explicit Connections**: 如果是循环过程，必须明确描述 "Curved arrow looping back from Zone X to Zone Y"

# Output Format (The Golden Schema)
请严格遵守以下 Markdown 结构输出：

---BEGIN PROMPT---

[Style & Meta-Instructions]
High-fidelity scientific schematic, technical vector illustration, clean white background, distinct boundaries, academic textbook style. High resolution 4k, strictly 2D flat design with subtle isometric elements.

[LAYOUT CONFIGURATION]
* **Selected Layout**: [例如：Cyclic Iterative Process with 3 Nodes]
* **Composition Logic**: [例如：A central triangular feedback loop surrounded by input/output panels]
* **Color Palette**: Professional Pastel (Azure Blue, Slate Grey, Coral Orange, Mint Green).

[ZONE 1: LOCATION - LABEL]
* **Container**: [形状描述, e.g., Top-Left Panel]
* **Visual Structure**: [具体描述, e.g., A stack of documents]
* **Key Text Labels**: "[Text 1]"

[ZONE 2: LOCATION - LABEL]
* **Container**: [形状描述, e.g., Central Circular Engine]
* **Visual Structure**: [具体描述, e.g., A clockwise loop connecting 3 internal modules: A (Gear), B (Graph), C (Filter)]
* **Key Text Labels**: "[Text 2]", "[Text 3]"

[ZONE 3: LOCATION - LABEL]
... (Add Zone 4/5 if necessary based on layout)

[CONNECTIONS]
1. [描述连接线, e.g., A curved dotted arrow looping from Zone 2 back to Zone 1 labeled "Feedback"]
2. [描述连接线, e.g., A wide flow arrow from Zone 2 to Zone 3]

---END PROMPT---

# Input Data
[在此处粘贴你的论文内容]
```

---

## 步骤二：绘图渲染（The Renderer）

**目标**：利用 Nano-Banana Pro 的指令遵循能力，将蓝图转化为像素。

**操作**：将步骤一生成的 `---BEGIN PROMPT---` 到 `---END PROMPT---` 之间的内容完整粘贴进去。

### Prompt 模板

```markdown
**Style Reference & Execution Instructions:**

1. **Art Style (Visio/Illustrator Aesthetic):**
   Generate a **professional academic architecture diagram** suitable for a top-tier computer science paper (CVPR/NeurIPS).
   * **Visuals:** Flat vector graphics, distinct geometric shapes, clean thin outlines, and soft pastel fills (Azure Blue, Slate Grey, Coral Orange).
   * **Layout:** Strictly follow the spatial arrangement defined below.
   * **Vibe:** Technical, precise, clean white background. NOT hand-drawn, NOT photorealistic, NOT 3D render, NO shadows/shading.

2. **CRITICAL TEXT CONSTRAINTS (Read Carefully):**
   * **DO NOT render meta-labels:** Do not write words like "ZONE 1", "LAYOUT CONFIGURATION", "Input", "Output", or "Container" inside the image.
   * **ONLY render "Key Text Labels":** Only text inside double quotes (e.g., "[Text]") listed under "Key Text Labels" should appear in the diagram.
   * **Font:** Use a clean, bold Sans-Serif font (like Roboto or Helvetica) for all labels.

3. **Visual Schema Execution:**
   Translate the following structural blueprint into the final image:

[在此处直接粘贴 Step 1 生成的 ---BEGIN PROMPT--- ... ---END PROMPT--- 内容]
```

---

## 步骤三：交互式微调（The Editor）

核心理念：利用 Nano-Banana Pro 的自然语言编辑能力进行「微调」。

> 💡 如果对图能达到 80 分的满意，就不要轻易点击重新生成。

### 情况 A：整体布局满意，细节有瑕疵

采取「自然语言编辑」策略：

| 修改类型 | 示例指令 |
|---------|---------|
| 修改图标 | "Change the 'Gear' icon in the center to a 'Neural Network' icon" |
| 调整颜色 | "Make the background of the left panel pure white instead of light blue" |
| 风格统一 | "Make all lines thinner and cleaner" |
| 文字修正 | "Correct the text 'ZONNE' to 'ZONE'" |

### 情况 B：整体布局错误

**不要试图通过修补来挽救**。回到步骤一，检查并修改 `[VISUAL SCHEMA]`：
- 是否选错了 `[LAYOUT CONFIGURATION]`？
- `Internal Visualization` 的描述是否不够具体？

---

## 进阶技巧

### 1. 人工介入微调

直接修改 `[VISUAL SCHEMA]` 往往比「抽卡」更快：
- 不想要某个图标？直接把 `Top Visual: A robot` 改成 `Top Visual: A brain icon`
- 颜色太花哨？直接在 `Color Palette` 里删掉多余的颜色

### 2. 提供参考图像

建立「科研审美库」，收集顶刊论文中布局精妙、配色高级的插图。

**风格迁移**：上传目标风格图片，删除通用 Art Style 描述，改为：
> "生成的 Figure 风格、布局特征和配色方案应严格参考我上传的图片"

**参数化控色**：使用精准的 HEX 代码（如 `#E1F5FE`）而非 "Light Blue"。

### 3. 去除水印

使用 Bookmarklet 脚本（在 Google AI Studio 页面点击书签即可）：

```javascript
javascript:(function(){const o=XMLHttpRequest.prototype.open;XMLHttpRequest.prototype.open=function(m,u){if(u.includes("watermark"))return console.log("🚫 Blocked:",u);return o.apply(this,arguments)};const f=window.fetch;window.fetch=function(u,...a){if(typeof u==="string"&&u.includes("watermark"))return console.log("🚫 Blocked fetch:",u),new Promise(()=>{});return f.apply(this,arguments)};Object.defineProperty(Image.prototype,"src",{set(v){if(v.includes("watermark"))return console.log("🚫 Blocked IMG:",v);this.setAttribute("src",v)}});const n=document.createElement("div");n.textContent="✅ Watermark blocking active!";Object.assign(n.style,{position:"fixed",top:"20px",left:"50%",transform:"translateX(-50%)",background:"rgba(0,0,0,0.75)",color:"#fff",padding:"8px 14px",borderRadius:"6px",fontSize:"14px",zIndex:99999,transition:"opacity 0.3s"});document.body.appendChild(n);setTimeout(()=>{n.style.opacity="0";setTimeout(()=>n.remove(),300)},500)})();
```

### 4. 后期处理

将 AI 生成的图视为 90% 的完成品，使用 Photoshop/Illustrator 进行最后修整：
- 抹掉 AI 生成的文字，换成符合论文格式的矢量文字
- 超长流程图可分段生成，最后在 PPT 里拼接

---

## ⚠️ 注意事项

### 1. "视觉合理性" vs "科学真实性"

AI 可能会优先考虑「画面好不好看」而牺牲「科学是否正确」：
- 信号通路中的抑制箭头方向可能画反
- 实验步骤的顺序可能被「自动优化」

### 2. 文本标注的「张冠李戴」

在信息量较大的图表中，AI 可能会：
- 为未提到的元素添加多余的说明
- 把原本属于模块 A 的标签挪到模块 B 上

### 3. 数据图表禁区

**严正声明**：本工作流仅适用于「概念结构图」「流程图」「系统架构图」等不涉及具体实验数值的示意图。

**绝对禁止**：使用 AI 绘制、生成或修改任何与实验数据直接相关的统计图表（散点图、柱状图、折线图等）。

> AI 无法理解数据的物理意义，它生成的每一个数据点都是基于概率的「瞎编」。使用 AI 生成数据图表严重涉嫌数据造假和学术不端！

### 4. 禁止 AI 绘图的期刊

将 AI 生成的图作为「草图」：
1. 导入 Figma/Illustrator，调高透明度作为底层「临摹范本」
2. 手动重新绘制线条和形状
3. 图标可使用 [iconfont-阿里巴巴矢量图标库](https://www.iconfont.cn/)
4. 规则图形/数据图表使用 Python (matplotlib/seaborn) 生成

---

## 总结

> 工具就是工具，Nano Banana Pro 帮我们解决的是「画出来」的问题，而不是「画得对」的问题。

把节省下来的时间用在严谨、严谨、再严谨的校对上，这样 AI 才会成为你的科研利器，而非学术隐患。
