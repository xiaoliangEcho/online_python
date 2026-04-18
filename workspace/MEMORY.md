# MEMORY.md - Long-Term Memory

## 项目信息

- **位置**: `~/online_python/`
- **端口**: 5088
- **服务**: `online-python.service`
- **Git**: `git@github.com:xiaoliangEcho/online_python.git`
- **题目数**: 69 道
- **测试用例**: 161 个

---

## 功能特性

- 在线编辑运行 Python 代码
- 经典算法题（类似 LeetCode）
- 测试用例自动验证
- 帮助功能显示参考答案

---

## 服务管理

```bash
sudo systemctl status online-python
sudo systemctl restart online-python
sudo systemctl stop online-python
```

---

## 服务依赖

**必须先构建 Docker 沙箱镜像：**
```bash
cd ~/online_python/sandbox && docker build -t python-sandbox:latest .
```

> ⚠️ 不构建镜像会导致代码执行/提交失败（超时）

---

## Notes

- Created: 2026-04-12
- 2026-04-18: Python 升级到 3.11.13（dnf 安装）
- 2026-04-18: 教训 - 部署服务前必须先读 README.md，检查依赖和构建步骤
