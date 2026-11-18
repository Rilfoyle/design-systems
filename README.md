# Design systems

个人设计系统收藏。按设计系统收录可公开分发的官方 Skill、组件源码、主题、设计 token 和文档，便于在其他项目中选择并使用。`official/` 是按需选取的上游文件快照，不是各个上游仓库的完整镜像；上游文件保持原样。根目录的说明、脚本和来源清单是为本收藏添加的辅助内容。

## 选择一套

| 系统 | 使用方式 | 官方 AI 资源 | 本地入口 |
| --- | --- | --- | --- |
| **coss ui** | React、Base UI、Tailwind CSS v4；通过官方 registry 将组件加入项目 | 官方 `coss` Skill | [Skill](coss-ui/official/coss/apps/ui/skills/coss/SKILL.md) · [文档](coss-ui/official/coss/apps/ui/content/docs) · [组件与示例](coss-ui/official/coss/apps/ui/registry/default) · [样式](coss-ui/official/coss/packages/ui/src/styles/globals.css) |
| **Radix Themes** | React；预设样式的 Themes，与无样式的 Radix Primitives 不同 | 未收录官方通用 Skill；直接使用官方文档 | [入门](radix/official/website/data/themes/docs/overview/getting-started.mdx) · [主题文档](radix/official/website/data/themes/docs/theme) · [组件与样式](radix/official/themes/packages/radix-ui-themes/src) · [颜色](radix/official/colors/src) |
| **HeroUI v3** | React、React Aria、Tailwind CSS v4 | 官方 `heroui-react` Skill 和 `DESIGN.md` | [Skill](heroui/official/heroui/skills/heroui-react/SKILL.md) · [DESIGN.md](heroui/official/heroui/apps/docs/public/react/DESIGN.md) · [文档](heroui/official/heroui/apps/docs/content/docs/en/react) · [主题与样式](heroui/official/heroui/packages/styles) |
| **Atlassian Design System** | React；官方 ADS 组件和 design tokens | 官方公开的 `atlassian-design` Skill 用于产物和原型；正式开发使用公开 CLI、MCP 和文档 | [Skill](atlassian/official/atlassian-mcp-server/skills/atlassian-design/SKILL.md) · [原型亮暗 token](atlassian/official/atlassian-mcp-server/skills/atlassian-design/render_kit/tokens.css) · [官方 token 包](atlassian/official/npm/atlaskit-tokens) |

设计系统的组件 API、布局、交互、动效、无障碍和字体应按所选系统的官方规范判断；不要把另一套系统的规范当成默认值。文档中的部分示例依赖上游站点或 monorepo；这里的源码快照用于查阅，不是可以直接运行的完整项目。

## 在其他项目使用

先克隆本仓库。下面的命令将所选**官方 Skill 原样复制**到已有项目的 `.agents/skills/`；不会安装依赖，也不会覆盖已有文件。coss 和 Atlassian 的 Skill 副本还会附带对应上游仓库的原版许可证。需要 Python 3.10+。

```bash
python3 scripts/use.py coss-ui /path/to/project
python3 scripts/use.py heroui /path/to/project --with-design
python3 scripts/use.py atlassian /path/to/project
```

`--with-design` 可额外复制 HeroUI 官方 `DESIGN.md` 到项目根目录；如果目标文件已存在，命令会停止。coss ui 和 Atlassian 没有通过此参数复制 `DESIGN.md`：coss ui 参考其官方 Skill 与文档，Atlassian 使用下方官网直链。目标项目的 AI 工具若使用不同的 Skill 目录，可将相同的官方 Skill 文件夹放到该工具要求的位置。

再按照相应官方指南配置运行环境和组件：

- **coss ui**：[开始使用](https://coss.com/ui/docs/get-started) · [样式](https://coss.com/ui/docs/styling) · [AI 文档索引](https://coss.com/ui/llms.txt)。可从官方 registry 添加组件；具体命令以官方指南为准。
- **Radix Themes**：[开始使用](https://www.radix-ui.com/themes/docs/overview/getting-started) · [主题配置](https://www.radix-ui.com/themes/docs/theme/overview) · [颜色](https://www.radix-ui.com/colors/docs/overview/usage)。没有虚构 Skill：让 AI 读取本仓库 Radix 官方文档，并依据官方指南安装 `@radix-ui/themes`、引入样式和配置 `Theme`。
- **HeroUI v3**：[React 文档](https://heroui.com/en/docs/react/getting-started/quick-start) · [官方 DESIGN.md](https://heroui.com/react/DESIGN.md)。不要混用 v2 与 v3 的 API。
- **Atlassian**：[开发入口](https://atlassian.design/get-started/develop) · [公开 AI 工具](https://atlassian.design/get-started/with-ai) · [浅色 DESIGN.md](https://atlassian.design/DESIGN.md) · [深色 DESIGN.md](https://atlassian.design/DESIGN.dark.md) · [AI 文档索引](https://atlassian.design/llms.txt) · [Figma 官方主页](https://www.figma.com/@atlassian)。其官网许可对使用范围及资料再分发有明确限制，见 [ADS 许可](https://atlassian.design/license)；因此官网文档以直链引用，未转载到这个公开仓库。此处收录的 Atlassian 开源仓库和 npm 包分别保留其自身许可证。

Atlassian 官网列出的 `atlassian-design-system` 等 Skill 目前属于 Atlassian 内部资源；本仓库中的公开 `atlassian-design` Skill 是另一个面向 artifacts、mockups 和 prototypes 的官方 Skill，不能当作前者。用于产品前端时，应查阅官方组件、token 和开发文档，并可使用公开 CLI 或 MCP。

## 更新官方快照

需要 Git、Python 3.10+ 和网络。`sources.json` 描述来源与选择的文件；`sources.lock.json` 记录实际取得的 Git commit、npm 包版本及完整性信息。Git 源跟踪指定分支的最新提交，npm 源跟踪指定 dist-tag；它们不一定与项目已安装的发布版同步。

```bash
# 查看上游是否有更新；有更新时返回退出码 2，不修改文件
python3 scripts/update.py --check

# 更新全部，或只更新其中一套
python3 scripts/update.py
python3 scripts/update.py --system atlassian

# 检查变化，再按需提交
git diff --stat
git status --short
```

更新先下载并验证所有选中来源，再替换相应的 `official/` 快照与来源记录。如果官方快照有本地改动或新增文件，脚本会停止，避免覆盖；请先保存改动并恢复快照。网络或上游路径失败时不会应用部分更新。官网下载直链会始终指向官网当前版本，不受本仓库快照锁定。

## 来源与许可

各快照的原始上游路径保留在对应 `official/<来源>/` 目录内，许可证随对应来源保存。coss 使用的 Cal Sans 和 Paper Mono 许可证也分别收录于 `coss-ui/official/cal-sans/` 与 `coss-ui/official/paper-mono/`。具体来源、分支、文件范围请查看 [sources.json](sources.json)，实际版本请查看 [sources.lock.json](sources.lock.json)。本仓库不代表或代言各设计系统官方。
