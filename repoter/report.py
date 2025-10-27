import json
import os
import matplotlib.pyplot as plt
from config import REPORT_CONFIG
from datetime import datetime
import numpy as np
from matplotlib import font_manager  # 新增：导入字体管理模块




class ReportGenerator:
    def __init__(self, results):
        self.results = results
        self.report_path = os.path.join(
            REPORT_CONFIG["output_dir"],
            f"{REPORT_CONFIG['report_name']}.{REPORT_CONFIG['format']}"
        )
        # 统计数据
        self.stats = self._calculate_stats()

    def _calculate_stats(self):
        """计算漏洞统计数据"""
        stats = {'total': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0, 'types': {}}
        for url, vulns in self.results.items():
            for vuln in vulns:
                severity = vuln['severity']
                stats['total'] += 1
                stats[severity] += 1
                # 按类型统计
                vuln_type = vuln['type']
                stats['types'][vuln_type] = stats['types'].get(vuln_type, 0) + 1
        return stats

    def generate(self):
        """生成多格式报告（支持图表）"""
        if REPORT_CONFIG["format"] == "html":
            self._generate_html()
        elif REPORT_CONFIG["format"] == "json":
            self._generate_json()
        elif REPORT_CONFIG["format"] == "pdf":
            self._generate_pdf()  # 需要安装pdfkit和wkhtmltopdf
        else:
            self._generate_text()

        print(f"报告已生成: {self.report_path}")
        return self.report_path

    def _generate_html(self):
        """生成带图表的HTML报告"""
        # 生成漏洞分布图表
        chart_path = self._generate_chart()

        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>PostMessage XSS漏洞扫描报告</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                :root {{
                    --primary: #3498db;
                    --secondary: #2c3e50;
                    --high: #e74c3c;
                    --medium: #f39c12;
                    --low: #27ae60;
                    --info: #1abc9c;
                    --light: #f8f9fa;
                    --dark: #343a40;
                    --border: #dee2e6;
                }}
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                body {{
                    background-color: #f5f7fa;
                    color: var(--dark);
                    line-height: 1.6;
                    padding: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    background-color: white;
                    padding: 25px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    margin-bottom: 30px;
                    border-top: 4px solid var(--primary);
                }}
                .header h1 {{
                    color: var(--secondary);
                    margin-bottom: 10px;
                    font-size: 1.8rem;
                }}
                .stats {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    margin-bottom: 30px;
                }}
                .stats h2 {{
                    color: var(--secondary);
                    margin-bottom: 15px;
                    font-size: 1.4rem;
                    border-bottom: 1px solid var(--border);
                    padding-bottom: 10px;
                }}
                .stat-cards {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    margin-top: 15px;
                }}
                .stat-card {{
                    flex: 1;
                    min-width: 120px;
                    padding: 15px;
                    border-radius: 8px;
                    color: white;
                    text-align: center;
                }}
                .stat-card.total {{ background-color: var(--primary); }}
                .stat-card.high {{ background-color: var(--high); }}
                .stat-card.medium {{ background-color: var(--medium); }}
                .stat-card.low {{ background-color: var(--low); }}
                .stat-card.info {{ background-color: var(--info); }}
                .stat-card .value {{
                    font-size: 1.8rem;
                    font-weight: bold;
                    margin: 5px 0;
                }}
                .stat-card .label {{ font-size: 0.9rem; opacity: 0.9; }}
                .chart {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    margin-bottom: 30px;
                    text-align: center;
                }}
                .chart h3 {{
                    color: var(--secondary);
                    margin-bottom: 20px;
                    font-size: 1.2rem;
                }}
                .chart img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 5px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .vulnerability {{
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                    transition: transform 0.2s;
                }}
                .vulnerability:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                .vulnerability.high {{ border-left: 5px solid var(--high); }}
                .vulnerability.medium {{ border-left: 5px solid var(--medium); }}
                .vulnerability.low {{ border-left: 5px solid var(--low); }}
                .vulnerability.info {{ border-left: 5px solid var(--info); }}
                .vulnerability h3 {{
                    color: var(--secondary);
                    margin-bottom: 10px;
                    font-size: 1.3rem;
                }}
                .url-section {{
                    margin-bottom: 30px;
                }}
                .url-section h2 {{
                    color: var(--primary);
                    margin-bottom: 15px;
                    font-size: 1.5rem;
                    padding-bottom: 8px;
                    border-bottom: 2px solid var(--light);
                }}
                .url {{
                    color: var(--primary);
                    text-decoration: none;
                    font-weight: 500;
                }}
                .url:hover {{
                    text-decoration: underline;
                }}
                .code {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    font-family: 'Consolas', monospace;
                    white-space: pre-wrap;
                    overflow-x: auto;
                    margin: 10px 0;
                    border: 1px solid var(--border);
                    font-size: 0.9rem;
                }}
                .fix {{
                    background-color: #e8f5e9;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 10px;
                    border: 1px solid #c3e6cb;
                }}
                .fix strong {{
                    color: #28a745;
                }}
                .vuln-meta {{
                    margin: 10px 0;
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                }}
                .vuln-meta p {{
                    margin: 0;
                }}
                .severity-badge {{
                    display: inline-block;
                    padding: 3px 8px;
                    border-radius: 4px;
                    color: white;
                    font-size: 0.8rem;
                    font-weight: 500;
                }}
                .badge-high {{ background-color: var(--high); }}
                .badge-medium {{ background-color: var(--medium); }}
                .badge-low {{ background-color: var(--low); }}
                .badge-info {{ background-color: var(--info); }}
                footer {{
                    text-align: center;
                    margin-top: 50px;
                    color: #6c757d;
                    font-size: 0.9rem;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>PostMessage XSS漏洞扫描报告</h1>
                <p>扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <div class="stats">
                <h2>漏洞统计</h2>
                <div class="stat-cards">
                    <div class="stat-card total">
                        <div class="label">总漏洞数</div>
                        <div class="value">{self.stats['total']}</div>
                    </div>
                    <div class="stat-card high">
                        <div class="label">高危</div>
                        <div class="value">{self.stats['high']}</div>
                    </div>
                    <div class="stat-card medium">
                        <div class="label">中危</div>
                        <div class="value">{self.stats['medium']}</div>
                    </div>
                    <div class="stat-card low">
                        <div class="label">低危</div>
                        <div class="value">{self.stats['low']}</div>
                    </div>
                    <div class="stat-card info">
                        <div class="label">信息</div>
                        <div class="value">{self.stats['info']}</div>
                    </div>
                </div>
            </div>

            <div class="chart">
                <h3>漏洞类型分布</h3>
                <img src="{chart_path}" alt="漏洞类型分布">
            </div>
        """

        # 添加漏洞详情（含修复建议）
        for url, vulns in self.results.items():
            if not vulns:
                continue
            html += f"<div class='url-section'><h2>URL: <a class='url' href='{url}'>{url}</a></h2>"

            for vuln in vulns:
                html += f"""
                <div class="vulnerability {vuln['severity']}">
                    <h3>{vuln['description']}</h3>
                    <div class="vuln-meta">
                        <p><strong>类型:</strong> {vuln['type']}</p>
                        <p><strong>严重程度:</strong> <span class="severity-badge badge-{vuln['severity']}">{vuln['severity']}</span></p>
                    </div>
                """
                if 'code_snippet' in vuln:
                    html += f"<p><strong>代码片段:</strong></p><div class='code'>{vuln['code_snippet']}</div>"
                if 'exploit' in vuln and vuln['exploit']['exploitable']:
                    html += f"<p><strong>可利用:</strong> 是</p>"
                    html += f"<p><strong>成功Payload:</strong> <div class='code'>{vuln['exploit']['payload']}</div></p>"
                    html += f"<p><strong>利用证明:</strong> {vuln['exploit']['proof']}</p>"
                if 'fix建议' in vuln:
                    html += f"<div class='fix'><strong>修复建议:</strong> {vuln['fix建议']}</div>"
                html += "</div>"
            html += "</div>"  # 关闭url-section

        html += """
            <footer>
                <p>PostMessage XSS漏洞扫描工具生成报告</p>
            </footer>
        </body>
        </html>
        """

        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def _generate_chart(self):
        """生成漏洞类型分布图表（修复中文字体）"""
        # --------------------------
        # 新增：设置中文字体（关键修复）
        # --------------------------
        try:
            # 方案1：优先使用 Windows 自带的“黑体”（SimHei）
            font_manager.fontManager.addfont("C:/Windows/Fonts/simhei.ttf")
            plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # 中文用SimHei，英文用DejaVu
            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示异常问题
        except FileNotFoundError:
            # 方案2：若黑体不存在，使用“微软雅黑”（Microsoft YaHei）备选
            try:
                font_manager.fontManager.addfont("C:/Windows/Fonts/msyh.ttc")
                plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'DejaVu Sans']
                plt.rcParams['axes.unicode_minus'] = False
            except Exception:
                # 方案3：若均不存在，提示用户手动指定字体
                print("[!] 未找到系统自带中文字体，图表中文可能显示异常")
                print("[!] 建议手动安装 SimHei 字体，或在代码中指定字体路径")

        # --------------------------
        # 原有图表生成逻辑（保持不变）
        # --------------------------
        # 1. 统计漏洞类型数据（示例，需与你的实际数据结构匹配）
        vuln_types = ["未验证漏洞", "已验证高危", "已验证中危", "已验证低危"]
        vuln_counts = [
            self.stats.get("unverified", 0),
            self.stats.get("high", 0),
            self.stats.get("medium", 0),
            self.stats.get("low", 0)
        ]

        # 2. 创建图表
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = ["#95a5a6", "#e74c3c", "#f39c12", "#27ae60"]  # 灰、红、橙、绿

        # 3. 绘制柱状图（示例，也可能是饼图等其他类型）
        bars = ax.bar(vuln_types, vuln_counts, color=colors, alpha=0.8)

        # 4. 设置图表标题和标签（中文 now 可正常显示）
        ax.set_title("漏洞类型分布统计", fontsize=14, pad=20)
        ax.set_xlabel("漏洞类型", fontsize=12, labelpad=10)
        ax.set_ylabel("漏洞数量", fontsize=12, labelpad=10)

        # 5. 在柱子上添加数值标签
        for bar, count in zip(bars, vuln_counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                    str(count), ha='center', va='bottom', fontsize=11)

        # 6. 保存图表（警告产生的位置）
        chart_dir = os.path.join(os.path.dirname(__file__), "charts")
        os.makedirs(chart_dir, exist_ok=True)
        chart_path = os.path.join(chart_dir, "vuln_distribution.png")

        # 保存时关闭警告（可选，避免残留警告）
        with plt.rc_context({'axes.unicode_minus': False}):
            plt.tight_layout()  # 自动调整布局，防止标签被截断
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')  # bbox_inches解决标签截断问题
        plt.close()  # 关闭图表，释放内存

        return chart_path

    def _generate_json(self):
        """生成JSON报告"""
        with open(self.report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

    def _generate_text(self):
        """生成文本报告"""
        text = "PostMessage XSS漏洞扫描报告\n"
        text += "=" * 50 + "\n\n"

        for url, vulns in self.results.items():
            if not vulns:
                continue

            text += f"URL: {url}\n"
            text += "-" * 50 + "\n"

            for i, vuln in enumerate(vulns, 1):
                text += f"漏洞 #{i}:\n"
                text += f"  描述: {vuln['description']}\n"
                text += f"  类型: {vuln['type']}\n"
                text += f"  严重程度: {vuln['severity']}\n"

                if 'code_snippet' in vuln:
                    text += f"  代码片段: {vuln['code_snippet']}\n"

                if 'exploit' in vuln and vuln['exploit']['exploitable']:
                    text += f"  可利用: 是\n"
                    text += f"  成功Payload: {vuln['exploit']['payload']}\n"
                else:
                    text += f"  可利用: 否\n"

                text += "\n"

        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(text)