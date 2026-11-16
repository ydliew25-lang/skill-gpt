# Skills 三处自动同步

## 单一来源

`skills-catalog.json` 是公开展示的唯一清单。三处输出为本仓 README 的目录、GitHub 个人主页的 Skills 区域、作品集网站的 Skills 列表和数量。其他个人介绍、作品和照片不由同步程序维护。

## 下次新增 Skill

1. 上传新技能的完整文件夹至 `skills/英文短名称/`，保留入口 `SKILL.md` 与引用目录。原分镜技能的根目录位置兼容保留。
2. 编辑 `skills-catalog.json`，复制一个已有条目，填写 `id`、`name`、`path`、`summary`、`inputs`、`outputs`、`profile_summary`、`website_summary`，确认适合公开展示后设 `published: true`。`path` 应为 `skills/<id>/SKILL.md`。
3. 一起提交到 `main`。本仓 push 会生成总目录；两个主页每小时各检查一次公共清单，发现变化才提交。不是即时同步，GitHub 排队可能延迟。
4. 查看三个仓库 Actions 的 `Sync Skills catalog`。也可点击该工作流的 `Run workflow` 手动立即检查。

不要覆盖根 README，不要修改 `SKILLS:...:START/END` 标记或在生成区手工改文案。要修改说明文字，请改清单。技能包中的 README 应保留在其自身文件夹内。

## 公开范围与安全

`published: false` 只是不展示，不会使公开仓库里的文件保密。不要把任何机密或私人材料上传到公开仓库。

脚本只读数据，不执行远程 Skill 或脚本。目标仓库读取同一不可变提交下的清单与入口文件，检查字段、路径、重名、链接文件、数量及标记，再原子替换生成区。读取失败、JSON 错误、入口不存在或标记缺失时不写文件；保留原页面。HTML 与 Markdown 内容转义，照片数据不可改动。

三个工作流只使用各自短期 `GITHUB_TOKEN`，不需要跨仓库 PAT 或长期密钥。源码复制在各仓库中，不会从源仓下载执行程序。网站工作流在更新后显式打包并部署 Pages，不依赖机器人提交触发另一个工作流。第一次启用需确认 Pages 发布来源为 GitHub Actions，并核验一次成功部署。

## 故障与维护

- 公共仓库的计划任务可能在连续 60 天无活动后被 GitHub 停用。若长时间未使用，在每个目标仓库的 Actions 中确认工作流已启用，再手动运行。
- 没有变化时不会产生空提交；自动提交不会循环触发同步。
- 推送发生冲突时不强推，等待下一次运行重新读取当前内容。
- 检查失败请查看 Actions 日志。此方案未额外订阅通知；通知依你的 GitHub 通知设置。
- 三个仓库并非同一事务，可能短暂显示不同版本；下一次成功检查后会收敛。
- 若需上传后立即跨仓库触发，另行配置限定仓库范围的 GitHub App；当前方案不使用此权限。

参考：[GITHUB_TOKEN 范围](https://docs.github.com/en/actions/concepts/security/github_token)、[计划任务](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)、[Pages 自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。
