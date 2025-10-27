# postmessage_xss_scanner

一款专门用于检测网页中 postMessage 相关 XSS 漏洞的自动化扫描工具，能够爬取目标网站、分析潜在漏洞点并进行验证，最终生成详细的扫描报告。

## 功能特点

- **网站爬取**：支持递归爬取目标网站，可配置爬取深度和线程数
- **漏洞检测**：分析页面中的 postMessage 调用及事件监听，识别潜在的不安全实现
- **漏洞验证**：通过浏览器自动化模拟攻击，验证漏洞的可利用性
- **多格式报告**：支持生成 HTML、JSON、TXT、PDF 格式的扫描报告，包含漏洞统计图表
- **灵活配置**：可自定义扫描参数、XSS 测试 Payload、代理设置等

## 工作原理

1. **爬取阶段**：使用多线程爬虫获取目标网站的页面内容，支持静态页面和动态渲染页面
2. **分析阶段**：解析页面中的 JavaScript 代码，提取 postMessage 调用和 message 事件监听器，检测不安全的实现方式
3. **验证阶段**：对发现的潜在漏洞，使用精心设计的 XSS Payload 进行验证，确认是否可利用
4. **报告阶段**：汇总扫描结果，生成包含漏洞详情、统计数据和修复建议的报告

## 安装说明

### 前置要求

- Python 3.7+
- Chrome 浏览器（用于动态渲染和漏洞验证）
- ChromeDriver（需与 Chrome 版本匹配，会自动安装）

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/postmessage_xss_scanner.git
cd postmessage_xss_scanner
```

1. 安装依赖：

```bash
pip install -r requirements.txt
# 可能需要的额外依赖（根据系统情况）
pip install tqdm requests selenium beautifulsoup4 matplotlib pdfkit
```

1. 对于 PDF 报告生成，需安装 wkhtmltopdf：
   - Ubuntu/Debian: `sudo apt-get install wkhtmltopdf`
   - macOS: `brew install wkhtmltopdf`
   - Windows: 从 [wkhtmltopdf 官网](https://wkhtmltopdf.org/) 下载安装

## 使用方法

### 基本用法

```bash
python main.py https://target-url.com
```

### 常用参数

```bash
# 扫描单个URL（不爬取）
python main.py https://target-url.com --no-crawl

# 不进行漏洞验证
python main.py https://target-url.com --no-exploit

# 指定报告格式（html/json/txt/pdf）
python main.py https://target-url.com --report-format pdf

# 设置爬虫最大深度和线程数
python main.py https://target-url.com --max-depth 2 --threads 10

# 使用代理
python main.py https://target-url.com --proxy http://127.0.0.1:8080

# 浏览器无头模式（默认启用，禁用可去掉此参数）
python main.py https://target-url.com --headless
```

## 配置说明

可通过修改 `config.py` 文件自定义扫描行为：

- **扫描配置**：爬取深度、线程数、请求超时、代理设置等
- **报告配置**：输出目录、报告名称、默认格式等
- **XSS Payloads**：可扩展自定义的 XSS 测试 Payload
- **利用模板**：postMessage 漏洞验证的 HTML 模板

## 项目结构

```plaintext
postmessage_xss_scanner/
├── analyzer/          # 漏洞分析模块
│   ├── detector.py    # 漏洞检测逻辑
│   └── parser.py      # 页面解析器
├── crawler/           # 爬虫模块
│   ├── spider.py      # 网站爬取逻辑
│   └── utils.py       # 爬虫工具函数
├── validator/         # 漏洞验证模块
│   └── exploit.py     # 漏洞利用和验证
├── repoter/           # 报告生成模块
│   └── report.py      # 多格式报告生成
├── config.py          # 配置文件
├── utils.py           # 通用工具函数
├── main.py            # 程序入口
└── README.md          # 项目说明
```

## 报告示例

扫描完成后，报告将生成在 `reports/` 目录下，HTML 报告包含：

- 扫描概况和统计数据
- 漏洞分布图表
- 详细的漏洞信息（URL、严重程度、Payload、修复建议等）

## 注意事项

- 仅用于合法授权的安全测试，禁止用于未授权的攻击行为
- 部分网站可能有反爬机制，可通过调整 `config.py` 中的请求间隔和 User-Agent 规避
- 动态渲染页面可能需要更长的扫描时间，请耐心等待

## 许可证

[MIT](https://www.doubao.com/chat/LICENSE)# postmessage_xss_scanner

一款专门用于检测网页中 postMessage 相关 XSS 漏洞的自动化扫描工具，能够爬取目标网站、分析潜在漏洞点并进行验证，最终生成详细的扫描报告。

## 功能特点

- **网站爬取**：支持递归爬取目标网站，可配置爬取深度和线程数
- **漏洞检测**：分析页面中的 postMessage 调用及事件监听，识别潜在的不安全实现
- **漏洞验证**：通过浏览器自动化模拟攻击，验证漏洞的可利用性
- **多格式报告**：支持生成 HTML、JSON、TXT、PDF 格式的扫描报告，包含漏洞统计图表
- **灵活配置**：可自定义扫描参数、XSS 测试 Payload、代理设置等

## 工作原理

1. **爬取阶段**：使用多线程爬虫获取目标网站的页面内容，支持静态页面和动态渲染页面
2. **分析阶段**：解析页面中的 JavaScript 代码，提取 postMessage 调用和 message 事件监听器，检测不安全的实现方式
3. **验证阶段**：对发现的潜在漏洞，使用精心设计的 XSS Payload 进行验证，确认是否可利用
4. **报告阶段**：汇总扫描结果，生成包含漏洞详情、统计数据和修复建议的报告

## 安装说明

### 前置要求

- Python 3.7+
- Chrome 浏览器（用于动态渲染和漏洞验证）
- ChromeDriver（需与 Chrome 版本匹配，会自动安装）

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/postmessage_xss_scanner.git
cd postmessage_xss_scanner
```

1. 安装依赖：

```bash
pip install -r requirements.txt
# 可能需要的额外依赖（根据系统情况）
pip install tqdm requests selenium beautifulsoup4 matplotlib pdfkit
```

1. 对于 PDF 报告生成，需安装 wkhtmltopdf：
   - Ubuntu/Debian: `sudo apt-get install wkhtmltopdf`
   - macOS: `brew install wkhtmltopdf`
   - Windows: 从 [wkhtmltopdf 官网](https://wkhtmltopdf.org/) 下载安装

## 使用方法

### 基本用法

```bash
python main.py https://target-url.com
```

### 常用参数

```bash
# 扫描单个URL（不爬取）
python main.py https://target-url.com --no-crawl

# 不进行漏洞验证
python main.py https://target-url.com --no-exploit

# 指定报告格式（html/json/txt/pdf）
python main.py https://target-url.com --report-format pdf

# 设置爬虫最大深度和线程数
python main.py https://target-url.com --max-depth 2 --threads 10

# 使用代理
python main.py https://target-url.com --proxy http://127.0.0.1:8080

# 浏览器无头模式（默认启用，禁用可去掉此参数）
python main.py https://target-url.com --headless
```

## 配置说明

可通过修改 `config.py` 文件自定义扫描行为：

- **扫描配置**：爬取深度、线程数、请求超时、代理设置等
- **报告配置**：输出目录、报告名称、默认格式等
- **XSS Payloads**：可扩展自定义的 XSS 测试 Payload
- **利用模板**：postMessage 漏洞验证的 HTML 模板

## 项目结构

```plaintext
postmessage_xss_scanner/
├── analyzer/          # 漏洞分析模块
│   ├── detector.py    # 漏洞检测逻辑
│   └── parser.py      # 页面解析器
├── crawler/           # 爬虫模块
│   ├── spider.py      # 网站爬取逻辑
│   └── utils.py       # 爬虫工具函数
├── validator/         # 漏洞验证模块
│   └── exploit.py     # 漏洞利用和验证
├── repoter/           # 报告生成模块
│   └── report.py      # 多格式报告生成
├── config.py          # 配置文件
├── utils.py           # 通用工具函数
├── main.py            # 程序入口
└── README.md          # 项目说明
```

## 报告示例

扫描完成后，报告将生成在 `reports/` 目录下，HTML 报告包含：

- 扫描概况和统计数据
- 漏洞分布图表
- 详细的漏洞信息（URL、严重程度、Payload、修复建议等）



## 注意事项

- 仅用于合法授权的安全测试，禁止用于未授权的攻击行为
- 部分网站可能有反爬机制，可通过调整 `config.py` 中的请求间隔和 User-Agent 规避
- 动态渲染页面可能需要更长的扫描时间，请耐心等待

## 许可证

[MIT](https://www.doubao.com/chat/LICENSE)

