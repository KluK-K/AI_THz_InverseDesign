# 路线 B 研究道路：Binary Au/Air 反演 THz CPS Low-Pass Filter

## 0. 目标定义

我们要做的不是简单画一个低通滤波器，而是建立一个可复现的 AI 反演设计流程：

- 输入：目标 cutoff frequency、Au 宽度/厚度、gap、基底尺寸、最小工艺尺寸。
- 输出：可制造的二值 Au/air 几何 mask、传统 analog 等效解释、快速 S 参数、COMSOL 全波验证结果。
- 第一目标：在 3 um / 3 um / 3 um CPS、Au 厚 0.275 um、0.5 um 最小特征、sapphire 基底上得到 0.8 THz 附近的 low-pass cutoff。

## 1. 核心判断

路线 B 的关键是二值几何搜索，但不能让 AI 做无物理意义的随机图案。合理闭环是：

1. 用传统 analog / transmission-line 理论定义可解释目标。
2. 用 binary mask 表示 Au/air 几何。
3. 用硬约束保证中心 gap 不被填、两根 Au rail 连续、所有新增金属只在外侧。
4. 用快速模型评估大量候选。
5. 用 GA/BPSO 做全局搜索，用 DBS 做局部精修。
6. 只把最强候选送 COMSOL 3D FEM 验证。
7. 用 COMSOL 误差反向修正快速模型，形成 active learning。

## 2. 物理模型分层

### Level 1: 传统 analog 基线

把 CPS low-pass 解释为分布式 LC 网络：

- 窄高阻段：主要提供串联电感。
- 外侧 pad / stub：主要提供并联电容和开路支节谐振。
- 渐变结构：降低 passband reflection。
- chirped stub：把单一窄带谐振扩展成 0.8 THz 附近的宽截止带。

这一步用于画传统 analog 示意图，以及给优化器合理初始种子。

### Level 2: 快速搜索模型

优先复用已有 MATLAB 脚本：

- `play/real3/thz_cps_monolithic_strong_stub_lpf_0p5um.m`
- `play/real/thz_cps_pngf_like_dbs_demo.m`

阶段目标不是让快速模型完全准确，而是能稳定筛出相对更好的几何。

### Level 3: COMSOL 验证

COMSOL 只验证少量候选：

- baseline 3/3/3 CPS。
- 传统 Bessel/stepped-impedance 结构。
- Route B 最佳二值结构。
- Route B 消融结构：去掉 chirp、去掉 fractal branch、去掉 taper。

## 3. 几何创新主张

推荐主结构命名：

**Mirror-Chirped Fractal SSPP Stub CPS Low-Pass Filter**

中文：

**镜像渐变分形 SSPP 支节型 CPS 低通滤波器**

结构规则：

- 中心 3 um gap 永远为空。
- 两根 3 um Au rail 贯穿全器件，保证 on-chip CPS 兼容。
- 新增金属只在 rail 外侧。
- 上下关于 gap 中线镜像，保证 differential CPS 模式平衡。
- x 方向非周期 chirped 排布，避免单一谐振导致 passband ripple 过大。
- 每个主 stub 可带 0.5 um 量化的短分支，形成多尺度慢波/SSPP 边带。

创新点不在“有 stub”，而在：

- 二值反演自动生成非周期多尺度外侧加载。
- 保留 analog LC 可解释性。
- 用 connectivity 和 fabrication constraints 把 AI 结果锁定在可制造空间。

## 4. 优化目标

建议 objective：

```text
score =
  + w_pass * mean(S21_dB in passband)
  - w_ripple * passband_ripple
  - w_cutoff * abs(f3dB - 0.8 THz)
  - w_edge * leakage around 0.82-1.05 THz
  - w_stop * mean(linear leakage in stopband)
  + w_refl * reflection_reward(S11 < -10 dB)
  - w_fab * fabrication_penalty
  - w_area * excessive_metal_penalty
```

第一阶段建议权重：

- passband loss 权重大，但不能压过 cutoff。
- stopband 目标先设 1.0-1.9 THz 平均低于 -24 dB。
- f3dB 允许初期在 0.75-0.85 THz，COMSOL 修正后收紧。

## 5. 算法路线

### 5.1 GA 初始化

用参数化 seed 生成第一代：

- N = 5, 7, 9, 11 个主 stub。
- stub 长度按 quarter-wave around 0.9-1.2 THz 估算。
- pad 高度、宽度、位置做 0.5 um 量化。
- 加入 chirped 和 random jitter。

### 5.2 BPSO 全局搜索

BPSO 负责 binary mask 的大范围探索：

- particle 是压缩后的 upper-side mask。
- velocity 通过 sigmoid 转成 flip probability。
- 每轮投影回合法几何。
- personal/global best 按 multi-objective score 保存。

### 5.3 DBS 局部精修

DBS 负责最后 5%-10% 性能：

- 随机或 saliency-guided flip。
- 每次 flip 后立即 project constraints。
- 接受 score 变好的 move。
- 周期性 restart，避免局部最优。

## 6. 数据闭环

每个候选必须保存：

- `mask.csv`
- `params.json`
- `fast_sparams.csv`
- `metrics.json`
- `analog_equivalent.json`
- `comsol_status.json`

这样后期可以训练 surrogate：

```text
mask + physical parameters -> S21/S11/f3dB/ripple
```

## 7. 阶段里程碑

### Milestone 1: 可运行研究骨架

- VSCode 工程结构。
- 配置文件。
- binary mask 约束模块。
- 简单 smoke test。

### Milestone 2: 复用已有快速模型

- 把 MATLAB strong-stub 和 PNGF-like DBS 的配置统一。
- 输出统一 metrics。
- 生成可对比的 baseline / seed / optimized report。

### Milestone 3: GA/BPSO/DBS 三段搜索

- GA 找结构族。
- BPSO 搜 mask。
- DBS polish。
- 生成 top-20 candidates。

### Milestone 4: COMSOL 自动验证

- mask 到 COMSOL geometry。
- 自动材料、端口、mesh、frequency sweep。
- 输出 S 参数和 E-field。

### Milestone 5: AI surrogate

- 用 fast model 生成大数据。
- 用 COMSOL 校准小数据。
- 训练 CNN/Transformer surrogate。
- 建立输入参数到快速生成结构的 generator。

## 8. 当前最合理的下一步

先把已有 `play/real3` 的强支节模型纳入本工程，作为 Route B 的第一版 fast evaluator。

原因：

- 它已经满足 0.5 um、3/3/3、Au 厚 0.275 um、outer-only constraints。
- 它已有结果接近 0.8 THz cutoff。
- 它能给 BPSO/DBS 提供物理合理初始空间。

然后再把 `play/real/thz_cps_pngf_like_dbs_demo.m` 作为第二 evaluator，用来交叉检查强支节模型是否过拟合。

