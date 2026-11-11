# 使用方法与工具依赖

## 获取与加载

可以从仓库页面下载文件，也可以使用 Git：

```bash
git clone https://github.com/ydliew25-lang/skill-gpt.git
cd skill-gpt
```

在支持自定义 Skill 的 AI 环境中，按该环境的方式加载 `skills/<技能名称>/`。不支持自动发现 Skill 时，可以让具备文件读取能力的助手读取对应 `SKILL.md`，并按其中的相对引用读取配套规范和模板。

需要保留完整目录。只复制主文件，可能使参考规范、图标或脚本不可用。不要把 `archive/` 与主版本一起导入自动递归发现技能的目录。

导入方式和触发语法由运行环境决定。`agents/openai.yaml` 是部分 Skill 的界面配置；保留它有助于兼容，但不代表所有平台均已通过测试。测试用例生成与行业案例更新器的历史文件包没有该文件，属于原有结构。

## 工具依赖

| Skill | 需要的能力 | 可在材料不足时完成的工作 |
|---|---|---|
| 具身智能合作案例增量更新器 | 实时网页检索和原文阅读；读取、编辑、保存 `.xlsx` 并保留格式 | 无 Excel 时生成结构化候选清单，不宣称已经和原库去重或写入 |
| 零售合作模式分析 | 现实案例的检索与来源核验；按交付要求使用绘图或文件工具 | 依据用户提供的材料归纳；将无法核实的事项标为待验证 |
| 绘制商业模式图 | 读取用户材料；可控矢量或代码绘图；中文字体与文本渲染；PNG/SVG 导出和图像预览 | 整理已确认关系和待确认项；缺少绘图工具时说明限制，不宣称已生成图文件 |
| 测试用例生成 | 读取产品需求与参考文件的 AI 助手；导出文件时需要相应文件工具 | 输出场景矩阵和用例草稿，明确待确认能力与参数 |
| 原图构图可编辑 PPT 工作流 | 演示文稿制作、导出和渲染；必要时的图片处理；文件保存能力 | 先整理可确定的文字、备注和结构，说明缺失的参考材料 |

PPT 工作流中的 **Presentations** 指运行环境的演示文稿工具；**Library** 指其文件检索、持久保存与版本管理方式。移到其他环境时，应映射到实际可用的对应工具，不应把这些名字当作本仓库内附带的软件包。

## 商业模式图的输入与输出

技能目录：[`skills/draw-business-model/`](../skills/draw-business-model/)。完整说明见 [绘制商业模式图](draw-business-model.md)。

提供合作分析、关系清单或参考图，以及本次需要覆盖的参与方、关系范围与交付格式。该 Skill 先把材料整理为有向关系，再设计布局、绘制和检查；不会因为画图而自动扩展为新的行业调研。

默认交付高清 PNG 与可编辑 SVG。执行环境应具备中文文本渲染、可控绘图、图像预览与文件导出能力；具体软件或绘图库由宿主环境提供。此 Skill 包含流程规范、界面配置与图标，没有附带独立绘图脚本或成品示例图。

## PPT 结构检查脚本

脚本位置：[`audit_pptx.py`](../skills/build-editable-pptx-from-references/scripts/audit_pptx.py)。

脚本使用 Python 标准库。使用兼容的 Python 3 环境运行；本次未测定最低支持版本。

查看参数：

```bash
python3 skills/build-editable-pptx-from-references/scripts/audit_pptx.py --help
```

检查自己提供的 PPTX，并将结构报告写入指定位置：

```bash
python3 skills/build-editable-pptx-from-references/scripts/audit_pptx.py ./example.pptx --expected-slides 5 --require-notes --output ./audit.json
```

其中 `example.pptx` 是用户自己提供的输入文件，不是仓库附带样例。页数和其他限制应改成该项目的实际约定。

脚本可检查对象类型、表格、图片、字体声明、行距和备注等结构证据。它不渲染页面、不验证事实、不判断字体是否已安装，也不代表已经在 PowerPoint 客户端检查。

## 测试用例示例中的参数

[`retail-robot-example.md`](../skills/test-case-generator/references/retail-robot-example.md) 使用商品 A/B/C/D 和 `T_delivery`、`T_dialogue` 作为教学变量。执行真实测试前，需要用已确认的产品参数、设备能力和安全流程替换它们。

模板和示例用于编写测试方案；本仓库不会连接设备、执行现场测试或统计真实成功率。

## 版本选择

行业案例更新器当前采用 `embodied-industry-case-updater`。`archive/embodied-industry-case-update/` 保留其原版，用于了解工作流演进。两者属于同一类工作流，通常选择主版本即可。

仓库中的日更/周更措辞描述适用场景；定时执行需由外部调度工具另行配置。

