# 高校实验室预约管理 MVP

一个用于课程演示的最小实验室预约系统：查看实验室、提交预约、自动阻止时间冲突、取消预约。后端只用 Python 标准库和 SQLite，前端为原生 HTML/CSS/JavaScript。

本仓库同时保存《开源创新思维》许可证扫描作业报告。`docs/` 包含业务与行业分析、现状线状流程图 JPG、AI 改进流程图 JPG、设计方案、报价估算和扫描证据。

## 运行

需要 Python 3.11 或更新版本。

```bash
python scripts/run.py
```

浏览器打开 `http://127.0.0.1:8000`。首次运行会在 `data/lab.db` 初始化三个示例实验室。可用 `LAB_DB` 指定其他数据库路径，用 `LAB_PORT` 改端口。

## 测试

```bash
python -m unittest discover -s tests -v
```

## 目录

```text
my-tool/
├── README.md  LICENSE  .gitignore  CHANGELOG.md  CONTRIBUTING.md
├── requirements.txt  pyproject.toml
├── src/my_tool/          # 预约规则、SQLite、HTTP 服务和页面
├── docs/                 # 业务与行业分析、流程图、设计、报价、扫描报告
├── tests/                # 预约冲突、数据校验和取消测试
├── examples/             # API 调用示例
├── scripts/              # 运行脚本
├── config/               # 示例配置
├── data/                 # 初始化样例；运行数据库已忽略
└── .github/              # CI、Issue 与 PR 模板
```

## MVP 边界

此版本在本机演示预约闭环，不包含学校单点登录、审批、安全准入、设备控制、支付或正式部署能力。界面中的示例实验室和报价均为课程方案假设，正式落地前需与真实管理部门核实。

## API

见 [API 文档](docs/api.md)。

## 作业材料

- [现状线状流程图](docs/线状流程图-现状.jpg)
- [AI 改进流程图](docs/AI改进流程图.jpg)
- [项目设计方案](docs/design.md)
- [行业分析](docs/industry-analysis.md)
- [许可证扫描原始证据](docs/commons-csv-scancode-32.5.0.json)

