# 📰 AstrBot Plugin: NewsNow

一个适用于 [AstrBot](https://github.com/Soulter/AstrBot) 的新闻获取插件。
基于 [NewsNow](https://github.com/ourongxing/newsnow) 项目，可以从您自建的 NewsNow 服务中获取知乎、微博、36氪、IT之家等平台的实时热点新闻。

## ✨ 功能特性

- **多源支持**：支持知乎、微博、36氪、IT之家、百度热搜、B站、贴吧、少数派等 20+ 个主流平台。
- **实时热点**：直接获取最新榜单和资讯。
- **美观输出**：自动格式化输出，支持链接跳转。
- **灵活配置**：支持在 AstrBot 后台直接配置 API 地址，无需修改代码。

## 📦 安装方法

### 方法一：Web 后台上传（推荐）
1. 将本插件文件夹打包为 `.zip` 压缩包。
2. 打开 AstrBot 管理后台。
3. 进入 **插件 (Plugins)** 页面。
4. 点击右上角 **上传插件**，选择压缩包进行安装。

### 方法二：手动安装
1. 将 `astrbot_plugin_newsnow` 文件夹复制到 AstrBot 的 `data/plugins/` 目录下。
2. 重启 AstrBot。

## ⚙️ 配置说明

安装完成后，请在 AstrBot 后台的插件列表中找到 **NewsNow** 并点击 **配置 (Settings)**。

| 配置项 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `api_url` | `http://192.168.124.8:12444` | **重要**：填写您部署的 NewsNow Docker 服务的地址。请务必包含 `http://` 协议头和端口号。 |
| `timeout` | `10` | 请求超时时间（秒）。网络较慢时可适当调大。 |

## 💻 使用指令

插件注册了 `/news` 指令。

### 基本用法
/news [源ID]


### 示例
- **获取知乎热榜（默认）**：
/news

- **获取微博热搜**：
/news weibo

- **获取 IT 之家新闻**：
/news ithome

- **获取 36氪快讯**：
/news 36kr


## 📋 支持的新闻源

支持 NewsNow 项目的所有数据源，常见的 ID 包括：

| ID | 名称 | ID | 名称 |
| :--- | :--- | :--- | :--- |
| `zhihu` | 知乎热榜 | `weibo` | 微博热搜 |
| `36kr` | 36氪 | `ithome` | IT之家 |
| `baidu` | 百度热搜 | `bilibili` | B站热搜 |
| `douyin` | 抖音热榜 | `tieba` | 贴吧热议 |
| `sspai` | 少数派 | `toutiao` | 今日头条 |
| `thepaper` | 澎湃新闻 | `kr` | 36氪 (同 36kr) |

*(更多源 ID 请参考 NewsNow 项目文档或尝试直接使用)*

## 🛠️ 常见问题

**Q: 提示“连接失败”？**
A: 请检查 AstrBot 所在的机器（或容器）能否访问配置的 `api_url`。如果是 Docker 部署，请确保网络互通。

**Q: 提示“403 Forbidden”？**
A: 如果您使用的是官方演示站或其他公开服务，可能触发了防火墙。建议使用自建的 Docker 服务（本项目设计初衷）。

## 📝 鸣谢

本插件的数据服务基于开源项目 [NewsNow](https://github.com/ourongxing/newsnow) 构建。