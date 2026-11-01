# GitHub 托管与后续更新

这个网站把个人主页和博客放在一起，使用 GitHub Pages 托管。
自动部署配置位于 `.github/workflows/pages.yml`，线上地址为 https://jinglunzhao.github.io/ 。

## 第一次发布

1. 登录 GitHub 的 `jinglunzhao` 账号。
2. 创建公开仓库 `jinglunzhao.github.io`。保持仓库为空，不勾选生成 README、License 或 .gitignore。
3. 把这个项目文件夹的**内容**上传到仓库根目录，默认分支使用 `main`。
   根目录应该直接看到 `build.py`、`site.json`、`assets/`、`content/` 和 `.github/`，不要再套一层项目文件夹。
   尤其要包含 `.github/workflows/pages.yml`，它负责构建和发布。
   不需要上传 `_site/`、`preview/` 或 ZIP 压缩包。
4. 在仓库中打开 **Settings → Pages → Build and deployment → Source**，选择 **GitHub Actions**。
5. 打开 **Actions → Build and deploy website** 查看部署结果。
   如果第一次运行发生在启用 Pages 之前而失败，启用后点击 **Run workflow** 重新运行。
6. 部署成功后访问 https://jinglunzhao.github.io/ 。

不需要购买服务器或域名。以后可以另外绑定自己的域名。

### 用 Git 上传源码

如果由我帮你发布，我可以在你授权后处理建仓、上传、配置和部署检查；
需要你亲自完成的账号登录或验证会单独提示。

如果想自己用终端上传，在创建好上面的空仓库后，从项目的父目录第一次执行：

```sh
cd jinglunzhao.github.io
git init -b main
git add .
git commit -m "Publish personal website"
git remote add origin https://github.com/jinglunzhao/jinglunzhao.github.io.git
git push -u origin main
```

这些命令假设本地项目尚未初始化 Git，远程仓库为空。
推送时按 GitHub 提示完成认证；GitHub 不接受直接用账号密码进行 HTTPS Git 推送。

## 以后怎样让我修改

继续在当前对话描述修改即可。如果新开对话，把网站文件夹作为 Codex 的本地项目打开，
并说明这是 `jinglunzhao.github.io` 个人网站。源文件可访问时，我就能直接修改。

可以这样提需求：

- “把首页简介换成下面这段，保持现在的排版，先给我本地预览。”
- “增加这篇论文：标题、作者、会议、年份、论文链接和代码链接如下。”
- “把这份笔记整理成英文博客，先作为草稿。”
- “这次修改可以发布，请推送到 GitHub Pages 并检查线上结果。”

通常流程是：描述修改 → 修改源码 → 构建与检查 → 本地预览 → 按你的指示发布。
推送到 `main` 后，GitHub Actions 会自动更新线上网页，无需每次重新配置 Pages。
修改本地文件本身不会更新线上网站。

换电脑后，先克隆 GitHub 仓库，再在 Codex 中打开该文件夹。
对话同步与本地文件访问是两件事；新环境仍需能访问网站源码。

## 内容在哪里

| 要修改的内容 | 源文件 |
| --- | --- |
| 姓名、邮箱、头像、外部链接 | `site.json` |
| 首页与 About 的文字、模块 | `build.py` 的 `home()` / `about()` |
| 论文列表 | `content/publications.json` |
| 博客 | `content/posts/` 中的 Markdown 文件 |
| 字体、颜色、布局 | `assets/site.css` |

应修改源码，不直接修改自动生成的 `_site/`。

本地检查和预览命令见 `README.md`。
Codex 本地项目说明：https://learn.chatgpt.com/docs/projects
