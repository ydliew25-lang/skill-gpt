# Skill 整理清单

整理日期：2026-11-10（北京时间）。

本次按实际可取得的个人 Skill 文件与历史文件包整理，收录 **4 项主 Skill、1 个历史版本**。同一 Skill 的独立 `SKILL.md` 附件与完整包内容一致时，以完整包收录。

## 主 Skill

| 仓库目录 | 中文名称 | 来源与整理方式 |
|---|---|---|
| [skills/build-editable-pptx-from-references](../skills/build-editable-pptx-from-references/) | 原图构图可编辑 PPT 工作流 | 现有个人 Skill，保留全部 8 个源文件和相对引用 |
| [skills/analyze-retail-partnerships](../skills/analyze-retail-partnerships/) | 零售合作模式分析 | 现有个人 Skill，保留全部 3 个文件；将一处具体公司背景泛化为零售企业与机器人产品规划 |
| [skills/test-case-generator](../skills/test-case-generator/) | 测试用例生成 | 从既有 `test-case-generator-skill.zip` 恢复完整 5 个文件；参数化案例，并同步说明文档 |
| [skills/embodied-industry-case-updater](../skills/embodied-industry-case-updater/) | 具身智能合作案例增量更新器 | 采用 `embodied-industry-case-updater-shareable-v1.0.zip` 中的 3 个文件；将固定平台安装步骤改为通用加载说明 |

上述来源记录说明文件从哪里整理而来，不代表本次重新安装或启用了技能。

## 历史版本

[`archive/embodied-industry-case-update/`](../archive/embodied-industry-case-update/) 保存原版文件包中的 `SKILL.md` 与 `references/schema.md`，共 2 个文件。

原版技能名为 `embodied-industry-case-update`，分享版为 `embodied-industry-case-updater`。两版使用相同的 14 字段 Schema 和五维去重思路；分享版补充了触发条件、证据边界、重复候选处理和结果说明。两版参考 Schema 的内容相同。

原版作为历史资料保留，不计为第 5 项独立功能。

## 公开副本的调整

1. **零售分析**：将一处具体公司名替换为通用企业/产品规划表述，保留分析流程。
2. **测试用例生成**：商品名替换为 A/B/C/D；实际项目超时值替换为参数；原案例中的具体装配方式、设备运动细节和供应商实施状态移除，改为参数化教学配置。
3. **示例口径**：同步修改测试 Skill 主文、README 和示例，让说明与示例保持一致，不将教学假设写成特定设备的事实。
4. **加载说明**：移除行业案例分享包中未经本次验证的固定平台菜单路径，说明按运行环境的实际方式加载完整文件夹。

整理只调整公开表达、示例与使用说明，没有借机增加新工作流功能。尤其是测试用例的独立“关键场景筛选与合并”步骤，以及零售图的后续配色细则，本次不宣称已经固化在源文件中。

## 本次整理范围

- 主目录共有 19 个 Skill 配套文件，历史目录共有 2 个源文件；另有仓库级介绍、使用说明和变更记录。
- 个人定时任务与 Skill 文件分开管理。本次未将缺少独立源文件的“AI具身PM行业雷达”“具身智能周报”重建为新 Skill，也未修改其调度设置。
- 内置工具技能、第三方插件技能、原始项目数据库、私人对话和凭据不属于本仓库内容。
- 原始 ZIP 不作为公开附件再次上传，避免公开副本之外的历史业务细节被一并发布。

## 验证范围

整理时检查文件完整性、内部链接与相对引用、YAML/SVG/Python 语法，以及 PPT 检查脚本的命令行入口。发布时比对上传文件与本地整理稿的内容摘要。

上述检查针对文件包和发布内容，不代表已执行行业数据库更新、真实机器人测试或完整 PPT 生成任务。
