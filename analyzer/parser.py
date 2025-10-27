import re
from bs4 import BeautifulSoup
from utils import extract_js_functions


class PageParser:
    def __init__(self, html_content):
        self.html = html_content
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.scripts = self._extract_scripts()
        self.event_listeners = self._extract_event_listeners()

    def _extract_scripts(self):
        """提取所有JavaScript代码"""
        scripts = []

        # 提取<script>标签内容
        for script_tag in self.soup.find_all('script'):
            if script_tag.string:
                scripts.append(script_tag.string)

        # 提取事件处理函数中的JavaScript
        for tag in self.soup.find_all():
            for attr in tag.attrs:
                if attr.startswith(('on', 'href')):
                    scripts.append(tag[attr])

        return '\n'.join(scripts)

    def _extract_event_listeners(self):
        """提取所有事件监听器"""
        pattern = re.compile(r'addEventListener\s*\(\s*["\']message["\']\s*,\s*([^,]+)\s*', re.IGNORECASE)
        return pattern.findall(self.scripts)

    def has_post_message(self):
        """检查页面是否使用postMessage"""
        # 直接调用检查
        if re.search(r'postMessage\s*\(', self.scripts, re.IGNORECASE):
            return True

         # 事件监听器检查
        if self.event_listeners:
            return True

        return False

    def get_post_message_calls(self):
        """提取所有postMessage调用"""
        pattern = re.compile(
            r'postMessage\s*\(\s*(.+?)\s*,\s*(.+?)\s*\)',
            re.IGNORECASE | re.DOTALL
        )
        return pattern.findall(self.scripts)

    def get_message_event_handlers(self):
        """提取所有message事件处理函数"""
        handlers = []

        # 从addEventListener提取
        for handler in self.event_listeners:
            # 处理匿名函数
            if handler.strip().startswith('function') or handler.strip().startswith('('):
                handlers.append(handler)
            else:
                # 处理命名函数
                func_code = extract_js_functions(self.scripts, handler)
                if func_code:
                    handlers.extend(func_code)

        # 处理window.onmessage
        onmessage_pattern = re.compile(r'window\.onmessage\s*=\s*(.+?);', re.IGNORECASE | re.DOTALL)
        onmessage_matches = onmessage_pattern.findall(self.scripts)
        handlers.extend(onmessage_matches)

        return handlers