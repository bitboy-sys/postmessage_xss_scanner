import os
import sys
import argparse
from tqdm import tqdm  # 需安装tqdm
from crawler.spider import Spider
from analyzer.detector import PostMessageVulnerabilityDetector
from validator.exploit import PostMessageExploiter
from repoter.report import ReportGenerator
from config import SCAN_CONFIG, REPORT_CONFIG

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description='PostMessage XSS漏洞扫描工具')
    parser.add_argument('url', help='目标网站URL')
    parser.add_argument('--no-crawl', action='store_true', help='不进行爬虫，只扫描单个URL')
    parser.add_argument('--no-exploit', action='store_true', help='不进行漏洞验证')
    parser.add_argument('--max-depth', type=int, help=f'爬虫最大深度(默认: {SCAN_CONFIG["max_depth"]})')
    parser.add_argument('--threads', type=int, help=f'线程数(默认: {SCAN_CONFIG["max_threads"]})')
    parser.add_argument('--report-format', help=f'报告格式(html/json/txt/pdf, 默认: {REPORT_CONFIG["format"]})')
    parser.add_argument('--proxy', help='代理服务器(如http://127.0.0.1:8080)')
    parser.add_argument('--headless', action='store_true', help='浏览器无头模式')
    args = parser.parse_args()

    # 覆盖配置
    if args.max_depth:
        SCAN_CONFIG["max_depth"] = args.max_depth
    if args.threads:
        SCAN_CONFIG["max_threads"] = args.threads
    if args.report_format:
        REPORT_CONFIG["format"] = args.report_format
    if args.proxy:
        SCAN_CONFIG["use_proxy"] = True
        SCAN_CONFIG["proxies"] = {"http": args.proxy, "https": args.proxy}
    if args.headless:
        SCAN_CONFIG["headless_mode"] = True

    print("\n" + "=" * 50)
    print(f"开始扫描目标: {args.url}".center(50))
    print("=" * 50 + "\n")

    # 爬取网站（带进度条）
    if args.no_crawl:
        spider = Spider(args.url)
        response = spider._fetch_page(args.url)
        pages = {args.url: response[0]} if response[0] else {}
        print(f"[+] 已加载单个页面: {args.url}")
    else:
        spider = Spider(args.url)
        print("[*] 开始爬取网站...")
        pages = spider.crawl()
        print(f"[+] 爬取完成，共获取 {len(pages)} 个页面")

    # 分析漏洞（带进度条）
    results = {}
    print("\n[*] 开始分析漏洞...")
    for url in tqdm(pages.keys(), desc="分析页面"):
        html = pages[url]
        detector = PostMessageVulnerabilityDetector(url, html)
        vulnerabilities = detector.analyze()
        if vulnerabilities:
            results[url] = vulnerabilities
            # 显示找到的漏洞数量
            tqdm.write(f"[!] 在 {url} 发现 {len(vulnerabilities)} 个潜在漏洞")

    # 漏洞验证
    if not args.no_exploit and results:
        print("\n[*] 开始验证漏洞...")
        for url in tqdm(results.keys(), desc="验证漏洞"):
            for i, vuln in enumerate(results[url]):
                exploiter = PostMessageExploiter()
                exploit_result = exploiter.test_vulnerability(url, vuln)
                if exploit_result and exploit_result['exploitable']:
                    results[url][i]['exploit'] = exploit_result
                    tqdm.write(f"[!] 已验证 {url} 存在可利用漏洞")

    # 生成报告
    print("\n[*] 生成扫描报告...")
    report_generator = ReportGenerator(results)
    report_path = report_generator.generate()

    print("\n" + "=" * 50)
    print("扫描完成！".center(50))
    print(f"报告已保存至: {report_path}".center(50))
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()