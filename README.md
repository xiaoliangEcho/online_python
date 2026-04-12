# Python 在线练习平台

一个基于 Flask 的 Python 算法练习平台，支持代码运行、提交评测和访问统计。

## 功能特性

- 🎯 **20道算法题** - 简单/中等/困难/非常困难四个难度
- ▶️ **代码运行** - 在线运行 Python 代码，即时查看结果
- ✅ **提交评测** - 自动测试用例验证
- 📊 **代码分析** - 检查注释、代码质量评分
- 🆓 **自由编辑** - 独立的代码编辑器，支持保存代码
- 📈 **访问统计** - 访问量统计（需密码登录）
- 🔒 **安全沙箱** - Docker 容器隔离，防止恶意代码

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 构建沙箱镜像（必须）

```bash
cd sandbox && docker build -t python-sandbox:latest .
```

### 3. 配置环境变量（可选）

```bash
export STATS_PASSWORD="your_password"  # 统计页面密码
export STATS_TOKEN="your_token"        # 登录token
```

默认密码：`admin123`

### 4. 启动服务

```bash
python3 app.py
```

访问地址：
- 主页：http://localhost:5088
- 自由编辑：http://localhost:5088/free
- 访问统计：http://localhost:5088/stats

## 安全说明

用户代码在 Docker 沙箱中执行，具有以下安全措施：

| 措施 | 说明 |
|------|------|
| 网络隔离 | 禁止网络访问 |
| 内存限制 | 128MB |
| CPU 限制 | 0.5 核 |
| 进程限制 | 最多 50 个进程 |
| 权限控制 | 非 root 用户，无 Linux capabilities |

## 项目结构

```
online_python/
├── app.py              # Flask 主应用
├── requirements.txt    # 依赖列表
├── .gitignore
├── README.md
├── sandbox/
│   └── Dockerfile      # 沙箱镜像
└── templates/
    ├── index.html      # 算法练习页面
    ├── free.html       # 自由编辑页面
    ├── stats.html      # 访问统计页面
    └── stats_login.html # 登录页面
```

## 技术栈

- **后端**：Flask, SQLite
- **前端**：原生 HTML/CSS/JavaScript
- **代码执行**：Docker 沙箱

## License

MIT
