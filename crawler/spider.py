import threading
import requests
from queue import Queue
import time
import os
from .utils import extract_links, is_valid_url
from utils import normalize_url, get_url_hash, get_domain
from config import SCAN_CONFIG
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Spider:
    def __init__(self, start_url):
        self.start_url = normalize_url(start_url)
        self.base_domain = get_domain(self.start_url)
        self.queue = Queue()
        self.queue.put((self.start_url, 0))  # (url, depth)
        self.visited = set()
        self.pages = {}  # 存储URL和对应的页面内容
        self.lock = threading.Lock()
        self.threads = []
        self.stop_event = threading.Event()  # 线程退出信号

    def crawl(self):
        """开始爬取（修复线程安全和退出机制）"""
        # 创建并启动线程
        for i in range(SCAN_CONFIG["max_threads"]):
            thread = threading.Thread(target=self._worker, name=f"Spider-Thread-{i+1}")
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
            print(f"启动线程: {thread.name}")  # 调试日志

        # 等待所有任务完成
        self.queue.join()
        print(f"所有队列任务处理完成，总爬取页面数: {len(self.pages)}")  # 调试日志

        # 发送退出信号并等待线程结束
        self.stop_event.set()
        for thread in self.threads:
            thread.join()
            print(f"线程 {thread.name} 已退出")  # 调试日志

        return self.pages

    def _worker(self):
        """工作线程（修复task_done调用和退出逻辑）"""
        while not self.stop_event.is_set():  # 检查退出信号
            try:
                # 非阻塞获取任务（超时1秒，避免永久阻塞）
                url, depth = self.queue.get(timeout=1)
                print(f"\n{threading.current_thread().name} 处理任务: {url} (深度: {depth})")  # 调试日志
            except Exception:
                continue  # 超时后继续检查退出信号

            try:
                url_hash = get_url_hash(url)

                # 检查是否已访问或超过最大深度
                if url_hash in self.visited or depth > SCAN_CONFIG["max_depth"]:
                    print(f"{threading.current_thread().name} 跳过任务: 已访问或超深度")  # 调试日志
                    continue

                # 加锁标记为已访问
                with self.lock:
                    self.visited.add(url_hash)
                print(f"{threading.current_thread().name} 标记已访问: {url}")  # 调试日志

                # 速率控制
                time.sleep(SCAN_CONFIG["request_delay"])

                # 获取页面内容
                content, content_type = self._fetch_page(url)
                if not content:
                    print(f"{threading.current_thread().name} 未获取到内容: {url}")  # 调试日志
                    continue

                # 存储HTML内容
                if 'text/html' in content_type:
                    with self.lock:
                        self.pages[url] = content
                    print(f"{threading.current_thread().name} 存储页面: {url}")  # 调试日志

                # 提取新链接（未超深度时）
                if depth < SCAN_CONFIG["max_depth"]:
                    self._extract_and_enqueue_links(content, url, depth)

            except Exception as e:
                print(f"{threading.current_thread().name} 爬取错误 {url}: {str(e)}")
            finally:
                # 每个任务只调用一次task_done()
                self.queue.task_done()
                print(f"{threading.current_thread().name} 完成任务: {url} (剩余任务数: {self.queue.qsize()})")  # 调试日志

    def _fetch_page(self, url):
        """获取页面内容（静态+动态渲染）"""
        try:
            # 静态请求
            headers = {"User-Agent": SCAN_CONFIG["user_agent"]}
            response = requests.get(url, headers=headers, timeout=SCAN_CONFIG["timeout"])
            print(f"静态请求成功: {url} (状态码: {response.status_code})")  # 调试日志
            return response.text, response.headers.get("content-type", "")
        except Exception as e:
            print(f"静态请求失败 {url}: {str(e)}，尝试动态渲染...")  # 调试日志
            if SCAN_CONFIG["enable_js_rendering"]:
                try:
                    chrome_options = Options()
                    chrome_options.add_argument("--headless=new")
                    chrome_options.add_argument("--disable-gpu")
                    chrome_options.add_argument("--no-sandbox")  # 增加兼容性
                    chrome_options.add_argument("--disable-dev-shm-usage")  # 解决内存问题

                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    driver.get(url)
                    time.sleep(SCAN_CONFIG["js_render_delay"])
                    content = driver.page_source
                    driver.quit()
                    print(f"动态渲染成功: {url}")  # 调试日志
                    return content, "text/html"
                except Exception as e:
                    print(f"动态渲染失败 {url}: {str(e)}")
        return None, None

    def _extract_and_enqueue_links(self, content, base_url, current_depth):
        """提取链接并加入队列（增加调试日志）"""
        links = extract_links(content, base_url)
        print(f"从 {base_url} 提取到 {len(links)} 个原始链接")  # 调试日志

        valid_links = 0
        for link in links:
            normalized_link = normalize_url(link)
            link_hash = get_url_hash(normalized_link)

            # 检查链接有效性
            if (link_hash not in self.visited and
                    is_valid_url(normalized_link, self.base_domain,
                                 SCAN_CONFIG["allowed_domains"],
                                 SCAN_CONFIG["exclude_paths"])):
                with self.lock:
                    self.visited.add(link_hash)
                self.queue.put((normalized_link, current_depth + 1))
                valid_links += 1
                print(f"加入队列: {normalized_link} (新深度: {current_depth + 1})")  # 调试日志

        print(f"从 {base_url} 筛选出 {valid_links} 个有效链接加入队列")  # 调试日志