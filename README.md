# 产品场景分镜制作

`create-product-storyboards` 把产品需求、用户旅程和工作流转成可评审的分镜。适用于硬件作业、软件界面和人机协作场景，覆盖资料核对、拆镜、构图、画面一致性与交付验收。

## 使用方式

将完整的 `create-product-storyboards/` 目录复制到支持技能的工作环境所使用的技能目录。选用「产品场景分镜制作」，提供当前流程、产品实拍或界面截图，以及希望沿用的画风和交付格式。

- 请根据附件中的取件流程和设备实拍制作**硬件操作分镜**，画清操作人员、设备、物件及关键接触点。标出人员接手的时机，保持设备外形和物件位置前后连贯。
- 请根据附件中的用户旅程和界面稿制作**移动端退货分镜**，覆盖提交申请、等待反馈、提交成功与失败重试，逐镜标明用户动作和系统反馈。

## 仓库内容

| 文件 | 用途 |
|---|---|
| [SKILL.md](create-product-storyboards/SKILL.md) | 技能入口与制作流程 |
| [agents/openai.yaml](create-product-storyboards/agents/openai.yaml) | 技能显示名称和起始提示 |
| [references/visual-qa.md](create-product-storyboards/references/visual-qa.md) | 构图、视觉一致性和验收标准 |
| [references/templates.md](create-product-storyboards/references/templates.md) | 可复制的资料清单、镜头表与画面描述模板 |

## 上传到 GitHub

先解压源码包。将解压后的 `README.md` 和整个 `create-product-storyboards/` 目录上传到仓库根目录，保留 `agents/` 和 `references/` 的相对路径。上传后打开仓库首页，确认本页的文件链接可以访问。
