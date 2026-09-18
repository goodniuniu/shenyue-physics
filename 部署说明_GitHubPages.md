# 部署到 GitHub Pages 的说明

网站成品已生成在 `docs/` 目录（含 `.nojekyll`，无需额外配置）。按以下步骤发布：

## 第一步：在 GitHub 创建仓库

1. 打开 https://github.com/new ，新建一个仓库，例如命名为 `shenyue-physics`
2. 设为 Public（GitHub Pages 免费版要求公开仓库；如用 Private 需 GitHub Pro）

## 第二步：推送项目到 GitHub

在项目文件夹中执行（已装 Git 的情况下）：

```bash
cd "E:\MyOutput\MyOutput\AI_Project\申悦学习-AI指导物理学习"
git init
git add .
git commit -m "初始版本：中秋物理辅导网站 + 知识库"
git branch -M main
git remote add origin https://github.com/<你的用户名>/shenyue-physics.git
git push -u origin main
```

> 提示：`node_modules/` 体积大且不需要上传，项目中的 `.gitignore` 已排除它。
> 如果不熟命令行，也可以安装 GitHub Desktop，用图形界面把本文件夹提交上传。

## 第三步：开启 GitHub Pages

1. 打开仓库页面 → 顶部 **Settings** → 左侧 **Pages**
2. **Source** 选择 `Deploy from a branch`
3. Branch 选择 `main`，目录选择 `/docs`，点 **Save**
4. 等待 1~3 分钟，刷新该页面，上方会显示访问地址，形如：
   `https://<你的用户名>.github.io/shenyue-physics/`

## 日常更新流程

1. 修改 `知识库/`、`家长支持/` 或辅导计划 Markdown 文件（或让 AI 入库新错题）
2. 运行 `python build_site.py` 重新生成 `docs/`
3. `git add . && git commit -m "更新内容" && git push`
4. 网站约 1 分钟后自动更新

## 备注

- 数学公式由 KaTeX（CDN 加载）在浏览器端渲染，访问时需要联网。
- 若以后想绑定自己的域名（如 `physics.example.com`），在 Pages 设置里填域名，
  并在 DNS 添加 CNAME 记录指向 `<你的用户名>.github.io` 即可。
