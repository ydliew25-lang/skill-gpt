# AI 产品工作流 Skills

将产品工作中的重复任务整理为可复用的 AI 工作流，覆盖 **行业研究、商业合作分析、商业模式绘图、测试设计、可编辑 PPT 制作与产品场景分镜**。

<!-- SKILLS:CATALOG:START -->
本仓库收录 12 项公开展示 Skill，并保留行业案例更新器的 1 个历史版本。每项 Skill 都有明确的输入、执行步骤、输出要求和质量边界，供具备相应工具的 AI 助手读取执行。

## Skill 目录

| Skill | 解决的问题 | 主要输入 | 主要输出 |
|---|---|---|---|
| [具身智能合作案例增量更新器](skills/embodied-industry-case-updater/SKILL.md) | 将新合作信息核验、去重后补充到现有案例库 | Excel 案例表、日期范围、研究范围 | 更新后的 Excel、新增/更新数量、证据边界 |
| [零售合作模式分析](skills/analyze-retail-partnerships/SKILL.md) | 说明零售方、品牌方、平台方和第四方如何合作 | 研究对象、案例或资料、时间/地域范围 | 案例表、合作模式与业务流程表、资源流/资金流图、待验证机会 |
| [绘制商业模式图](skills/draw-business-model/SKILL.md) | 将已有合作分析画成资源、服务与资金对应清楚的关系图 | 合作分析、关系清单或参考图、展示范围与格式 | 高清 PNG、可编辑 SVG、机会与潜在收费标注、待验证事项 |
| [测试用例生成](skills/test-case-generator/SKILL.md) | 将需求与交互流程转成可执行、可判定的测试用例 | 产品需求、流程、技术能力、验收约束 | 场景矩阵、六列测试用例表、检查清单与待确认项 |
| [原图构图可编辑 PPT 工作流](skills/build-editable-pptx-from-references/SKILL.md) | 按已认可风格和参考图制作、续作可编辑演示文稿 | 内容、参考图/PPT、页数、时长、格式要求 | 可编辑 PPTX、预览、讲稿备注与来源 |
| [产品场景分镜制作](create-product-storyboards/SKILL.md) | 将产品需求、用户旅程和工作流转成可评审的分镜 | 需求/流程、产品实拍或界面截图、画风与交付要求 | 镜头脚本、分镜图文、视觉验收记录 |
| [论文转学术主题](skills/paper-to-academic-ppt/SKILL.md) | 将已有论文重组为围绕一个问题展开的学术汇报 | 论文、原典或史料、汇报时长与版式要求 | 逐页论证、可编辑 PPTX、引文出处与讲述备注 |
| [可编辑ppt进度轴制作skill](skills/editable-ppt-progress-axis/SKILL.md) | 为 PowerPoint 添加可编辑的顶部章节进度轴 | PPTX、章节范围、现有目录或参考样式 | 原生可编辑的进度轴、章节高亮与节内进度 |
| [商品试吃数据评注](skills/annotate-product-sampling/SKILL.md) | 将试吃现场原话和动作逐项标注，区分顾客偏好、商品反馈与购买意向 | 试吃现场日志或音视频转写，可选已有标注与数据字典 | 可筛选的 Excel 原文表、标签明细和待确认项 |
| [商品试吃品牌反馈分析](skills/analyze-sampling-feedback/SKILL.md) | 将已标注的试吃对话整理为有原话和计数依据的品牌反馈 | 逐句标注、对应版本的数据字典、可回查的原话或现场记录 | 七列品牌反馈表、改进措施与验证指标 |
| [商品试吃标注数据评测](skills/audit-sampling-annotations/SKILL.md) | 对照试吃原文和标注规则，逐拨查漏标、误标、重复及证据归属 | 原始试吃日志、已标注数据、对应版本的数据字典与评测标准，可选独立标准答案 | 标注评测报告、逐项证据、待裁决与复测清单 |
| [搭建试吃活动数据平台](skills/build-sampling-dashboard/SKILL.md) | 将多门店试吃资料接入分角色的数据平台，让用户从活动结论回查顾客原话 | 门店原始日志、逐句标注、分析报告、角色权限和品牌视觉规范 | 品牌、零售和内部工作台交互原型，支持指标下钻、证据回查和按权限下载 |

<!-- SKILLS:CATALOG:END -->
## 工作流的设计重点

- **把任务拆成可执行步骤**：先明确输入和边界，再组织检索、分析、制作与交付。
- **保留证据与不确定性**：区分公开事实、归纳判断和待验证假设，避免把宣传目标当成实测结果。
- **明确质量要求**：用例逐行独立完整；关系图逐边核对方向、标注和可读性；PPT 分别检查内容、视觉、对象和讲述；数据库更新保留原结构并标识增量。
- **支持继续迭代**：使用已有案例、表格和已认可页面继续工作，记录批次与版本。

## 开始使用

1. 在上表选择一项 Skill，打开对应的 `SKILL.md`。
2. 获取该 Skill 的完整文件夹，保留 `references/`、`assets/`、`scripts/` 等相对路径。
3. 按所使用 AI 环境的导入方式加载该文件夹，或让能够读取文件的 AI 助手读取 `SKILL.md` 及其引用文件。
4. 提供任务所需材料，并明确本次范围。是否能联网、生成 Excel、绘制和导出 SVG/PNG、制作和渲染 PPT，取决于运行环境的工具能力。

只加载需要使用的技能目录：原五项位于 `skills/`，产品场景分镜制作位于 `create-product-storyboards/`；`archive/` 用于查看历史，不需要同时导入。

详细说明见 [使用方法与工具依赖](docs/usage.md)；绘图工作流另见 [绘制商业模式图说明](docs/draw-business-model.md)。

## 调用示例

**行业案例更新**

> 使用 embodied-industry-case-updater，检索最近 7 天的中国具身智能合作案例。读取我上传的 Excel，与现有记录去重后更新“合作案例”子表；新增和修改内容标红，并说明证据边界。

**商业合作研究**

> 使用 analyze-retail-partnerships，分析零售商与平台的合作模式。注明平台类型、履约和付款主体，提供可核验来源，输出合作模式表以及资源流、资金流图。

**商业模式绘图**

> 使用 draw-business-model，根据我提供的合作分析绘制一张资源流与资金流合并图。线条颜色跟随发出方，资源/服务用实线、资金用虚线；机会名称黑色加粗，对应收费名称红色加粗。逐边核验方向和标注，输出高清 PNG 与可编辑 SVG，并说明待验证事项和未解决的布局限制。

**测试设计**

> 使用 test-case-generator，根据我提供的需求和设备能力说明，梳理场景矩阵并生成六列测试用例。每条前置条件和步骤都独立完整，未知能力标为待确认。

**演示文稿制作**

> 使用 build-editable-pptx-from-references，依据附件参考图制作 5 页可编辑 PPT。保留构图，文字和表格使用原生对象，添加来源与备注，并检查最终渲染效果。

**产品场景分镜制作**

> 使用 create-product-storyboards，根据附件中的用户旅程、工作流和产品实拍或界面截图制作场景分镜，逐镜说明角色、动作与反馈，保持画面一致，并按视觉验收标准检查交付。

以上为调用示例，不是本仓库已经执行的任务结果。

## 文件组织

| 路径 | 内容 |
|---|---|
| `skills/` | 原 5 项 Skill 的完整文件 |
| `create-product-storyboards/` | 产品场景分镜制作 Skill、显示配置、可复制模板与视觉验收标准 |
| `archive/embodied-industry-case-update/` | 行业案例增量更新器的原版 |
| [docs/usage.md](docs/usage.md) | 使用方式、工具依赖、PPT 检查脚本说明 |
| [docs/inventory.md](docs/inventory.md) | 来源清单、版本关系、整理范围 |
| [docs/draw-business-model.md](docs/draw-business-model.md) | 商业模式绘图的用途、输入输出、图形规则和调用示例 |
| [CHANGELOG.md](CHANGELOG.md) | 本次整理及公开示例调整记录 |

## 能力与验证范围

这些文件是 AI 工作流规范；仓库本身不提供后台定时调度、自动测试执行、独立绘图程序或独立的 PPT 生成服务。运行时使用的模型、联网工具和文件工具需由宿主环境提供。

PPT Skill 随附 `audit_pptx.py`，用于生成只读结构报告。该报告能辅助核对对象和格式声明，视觉效果、事实准确性和客户端表现仍需分别检查。

本次整理核对了文件完整性、相对引用、配置语法和脚本入口；没有据此宣称已完成所有工作流的端到端测试或跨平台兼容验证，也没有设置未经测量的效率提升比例。

## 发布说明

此仓库保存通用流程与参考规范。测试机器人案例已改为参数化教学示例，具体公司背景已泛化；原始业务数据库、私人对话和账号凭据不作为示例收录。具体调整及历史版本关系见 [整理清单](docs/inventory.md)。

## 产品场景分镜制作参考材料

- [技能入口与制作流程](create-product-storyboards/SKILL.md)
- [技能显示名称和起始提示](create-product-storyboards/agents/openai.yaml)
- [构图、视觉一致性和验收标准](create-product-storyboards/references/visual-qa.md)
- [可复制的资料清单、镜头表与画面描述模板](create-product-storyboards/references/templates.md)

新增 Skill 时，只上传技能文件夹，并在 [skills-catalog.json](skills-catalog.json) 中登记公开展示信息。请勿用单项 README 覆盖本仓库总目录。三处展示由自动工作流维护，详见 [同步说明](docs/automatic-sync.md)。
