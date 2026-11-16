# 接入与校验

## 建立映射

用实际播放顺序选定页码口径。先确认隐藏页是否参与目录、节内计数和页脚编号，再生成映射。如果演示有既定页码，另记录页脚显示值与放映位置的对应。PowerPoint 包中通过演示文稿的幻灯片列表和关系定位页面，勿以文件名推断播放顺序。

示例采用最终定稿后的九页。第 1–2 页是封面和目录，第 9 页是备查页。

```js
import { createProgressPlan, addProgressAxis } from "./scripts/progress-axis.mjs";

const sections = [
  { title: "问题与材料", first: 3, last: 4, summary: "说明问题与材料范围。" },
  { title: "个案与证据", first: 5, last: 7, summary: "通过核心材料推进论证。" },
  { title: "结论与讨论", first: 8, last: 8, summary: "回应问题并引导讨论。" },
  { title: "资料备查", first: 9, last: 9, summary: "提供档案和文献线索。" },
];

const slides = presentation.slides.items;
const plan = createProgressPlan({ slideCount: slides.length, sections, overviewPages: [1, 2] });
for (const [index, slide] of slides.entries()) {
  addProgressAxis(slide, plan, index + 1, {
    dark: index === 0,
    width: 1280,
    clearance: 44,
  });
}
```

为 Artifact Tool 兼容的幻灯片对象传入模块。模块绘制进度轴并替换由它自己命名的旧组件。打开、复制、导出 PPTX 和生成目录由调用者处理。仅需更新部分页面时，只调用所选页面。接入前确认输出副本与源的页序一致。已有别的工具制作的进度轴时，按对象位置和名称辨认，按修改范围替换。

`overviewPages` 适用于封面、目录或其他独立总览页，使用 1 起始页序索引。每页归属一个章节或总览状态。按需覆盖选项 `palette` 的 `text`、`track`、`done`、`active`。几何选项置于 `layout` 中，支持 `left`、`right`、`gap`、`labelTop`、`labelHeight`、`fontSize`、`trackTop`、`trackHeight`、`fillTop`、`fillHeight`。默认几何以 1280px 为基准按画布宽度缩放，覆盖值采用当前画布像素。设置 `clearance` 为源内容的可用净空底边，发现坐标超出时重新排版再运行。按需指定 `typeface`。

## 目录链接与保留原稿

- 为需要跳转的目录用演示工具的原生幻灯片链接。采用 PPTX 封装级链接时，为目录页设置目标幻灯片的内部关系，在文字或形状上使用对应的关系 ID 和 `ppaction://hlinksldjump`，并检查实际指向。
- 对现有 PPTX 先用支持精细编辑的方式工作。导出后如发现导入转存改变原图、表格、备注或互动链接，沿用原文件并向副本移植经过验证的原生导航对象。保留原幻灯片及关系，核对 ID、母版和演示页序。
- 检查目录章首、章尾与轴的状态。移动页面后重新计算。已有正文计时和备注时，只在确有必要时给目录分配时间。
- 渲染章节边界、最长标签、浅深底、封面和目录。复核页眉净空、页脚页码、目录链接，以及文字框和矩形的可编辑性。修改批量页面时，抽查源正文区域并验证全稿页序、页数、备注和媒体。
