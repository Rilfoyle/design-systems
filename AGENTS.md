# 工作约定

本仓库是四套设计系统的官方资料索引和选定文件快照，用于在其他项目中选择和应用设计系统。

- 先确认用户选中的系统，再阅读根目录 `README.md` 对应入口及其官方文档。按照该系统自己的组件、token、排版、布局、交互、动效和无障碍规范工作，不混用其他系统的默认设计。
- `*/official/` 是上游内容：不要手工改写、翻译、补充或声称它们是完整的上游仓库。不要创建或冒充官方 Skill、DESIGN.md 或 token。仓库级说明、来源清单和辅助脚本不属于官方内容。
- 保持原始许可证、版权声明与上游路径。更新时运行 `python3 scripts/update.py` 或带 `--system` 的命令，检查 `sources.lock.json` 和 Git diff；不要直接覆盖官方目录中的本地变更。
- Atlassian 官网资料使用 README 中的官方直链，不要把官网文档转载进这个公开仓库；网站许可和开源仓库、npm 包的许可应分别辨认。公开 `atlassian-design` Skill 面向产物和原型，与 Atlassian 内部的 `atlassian-design-system` Skill 不同；正式开发优先依据官方组件文档、公开 CLI 和 MCP。
- Radix 未收录经确认的官方通用 Skill，使用本地官方文档和官网；HeroUI 按 v3 文档实现；coss 按官方 registry 和 Skill 指引实现。
- 帮用户引入其他项目时，保留上游原文，使用 `scripts/use.py` 安装官方 Skill，并保护目标项目已有文件。该脚本不会安装运行依赖；遵循所选系统的官方安装说明。
- 区分 Git 分支快照、npm 包版本和官网实时文档。上游源码快照可能缺少完整 monorepo 上下文，不应将其描述为独立可运行项目；使用后的验证应与实际改动相符。
