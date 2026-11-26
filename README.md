# 个人记账小程序

基于 Python + Streamlit 的本地个人收支记账工具，使用 TRAE 辅助开发，并通过 DeepSeek API 提供月度消费分析建议。

## 一、功能说明

- 新增账目：记录日期、类型（收入/支出）、分类、金额、备注
- 表单校验：金额为空、非数字、小于等于 0 时给出错误提示，不写入数据
- 账目筛选：按月份、收支类型筛选明细
- 月度统计：自动计算当月总收入、总支出与结余
- 删除账目：按编号删除单条记录
- 本地持久化：数据保存到 `data/records.json`，关闭程序后重新打开数据不丢失
- AI 分析：调用 DeepSeek API（`deepseek-chat`），根据当月收支汇总生成消费建议

## 二、运行环境

- Python 3.10 及以上
- 依赖见 `requirements.txt`

## 三、安装与运行

```bash
pip install -r requirements.txt
streamlit run main.py
```

浏览器会自动打开本地页面（默认地址 http://localhost:8501）。

## 四、配置 DeepSeek API Key

API Key 从环境变量读取，不写入代码仓库：

- Windows（PowerShell）：

```powershell
$env:DEEPSEEK_API_KEY="你的密钥"
```

- macOS / Linux：

```bash
export DEEPSEEK_API_KEY="你的密钥"
```

未配置密钥时，程序仍可正常记账，AI 分析功能会给出跳过提示，不影响其他功能。

## 五、目录结构

```
account-book/
├── main.py              # Streamlit 主程序（界面、校验、筛选、统计）
├── storage.py           # JSON 本地读写模块
├── deepseek_client.py   # DeepSeek API 调用封装
├── data/
│   └── records.json     # 账目数据文件（首次运行自动生成）
├── requirements.txt     # 依赖清单
└── README.md            # 项目说明
```

## 六、验收标准对照

| 编号 | 验收标准 | 对应实现 |
| --- | --- | --- |
| A1 | 输入空金额或非数字、负数时弹出错误提示，不能存入数据 | `main.py` 表单校验分支 |
| A2 | 关闭重启程序后，已录入账目可正常加载 | `storage.py` 读写 `records.json` |
| A3 | 按收入/支出分类筛选，列表只展示对应类型记录 | 主区域类型筛选逻辑 |
| A4 | 统计模块自动计算选中月份总收入、总支出、结余 | 月度统计三栏指标 |
| A5 | 可调用 DeepSeek API 生成本月消费分析 | `deepseek_client.py` |
