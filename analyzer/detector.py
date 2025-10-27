import re
from .parser import PageParser


class PostMessageVulnerabilityDetector:
    def __init__(self, url, html_content):
        self.url = url
        self.parser = PageParser(html_content)
        self.vulnerabilities = []
        # 常见的不安全origin验证模式
        self.insecure_origin_patterns = [
            r'event\.origin\.indexOf\(["\'].*?["\']\)',  # 包含匹配
            r'event\.origin\s*==?\s*["\']http',         # 不完整协议匹配
            r'event\.origin\s*!=?\s*["\']',             # 仅否定检查
            r'[^!]event\.origin'                        # 无验证逻辑
        ]

    def analyze(self):
        """增强分析逻辑：检查postMessage调用和处理全链路"""
        if not self.parser.has_post_message():
            return self.vulnerabilities

        # 分析postMessage调用（增加data参数来源检查）
        self._analyze_post_message_calls()
        # 分析message事件处理（增强origin验证和data处理检查）
        self._analyze_message_handlers()
        # 分析iframe嵌套中的postMessage
        self._analyze_iframe_contexts()

        return self.vulnerabilities

    def _analyze_post_message_calls(self):
        calls = self.parser.get_post_message_calls()
        for call in calls:
            data_param, target_origin = call

            # 检测targetOrigin="*"
            if re.search(r'["\']\*["\']', target_origin):
                self.vulnerabilities.append({
                    'type': 'insecure_postmessage',
                    'description': 'postMessage使用了不安全的targetOrigin="*"，允许向任何域发送消息',
                    'code_snippet': f'postMessage({data_param}, {target_origin})',
                    'severity': 'high',
                    'hint': '可能利用场景：跨域发送恶意数据到未验证origin的接收方'
                })

            # 检查targetOrigin动态控制
            if re.search(r'location\.href|document\.referrer|window\.origin', target_origin, re.IGNORECASE):
                self.vulnerabilities.append({
                    'type': 'dynamic_target_origin',
                    'description': 'postMessage的targetOrigin由动态值控制，可能被篡改',
                    'code_snippet': f'postMessage({data_param}, {target_origin})',
                    'severity': 'medium'
                })

            # 检查data参数是否来自不可信源
            if re.search(r'location\.hash|document\.cookie|window\.name|localStorage', data_param, re.IGNORECASE):
                self.vulnerabilities.append({
                    'type': 'untrusted_data_source',
                    'description': 'postMessage的data参数来自不可信源（如URL哈希、cookie）',
                    'code_snippet': f'postMessage({data_param}, {target_origin})',
                    'severity': 'medium'
                })

    def _analyze_message_handlers(self):
        handlers = self.parser.get_message_event_handlers()
        for handler in handlers:
            # 检查origin验证
            if not re.search(r'event\.origin', handler, re.IGNORECASE):
                self.vulnerabilities.append({
                    'type': 'missing_origin_check',
                    'description': 'message事件处理未验证event.origin，可能接收恶意消息',
                    'severity': 'high',
                    'fix建议': '使用精确匹配验证event.origin，如event.origin === "https://trusted.com"'
                })
            else:
                # 检测不安全的origin验证模式
                for pattern in self.insecure_origin_patterns:
                    if re.search(pattern, handler, re.IGNORECASE | re.DOTALL):
                        self.vulnerabilities.append({
                            'type': 'weak_origin_check',
                            'description': 'message事件使用宽松的origin验证（如indexOf包含匹配）',
                            'code_snippet': re.search(pattern, handler, re.IGNORECASE | re.DOTALL).group(0),
                            'severity': 'medium',
                            'fix建议': '使用严格的精确相等比较（===）验证origin'
                        })

            # 检查data处理是否存在危险操作
            dangerous_ops = [
                (r'document\.write\s*\(.*event\.data.*\)', '使用document.write插入未经处理的消息数据'),
                (r'innerHTML\s*=.*event\.data', '使用innerHTML插入未经处理的消息数据'),
                (r'eval\s*\(.*event\.data.*\)', '使用eval执行消息数据'),
                (r'new Function\(.*event\.data.*\)', '使用new Function执行消息数据'),
                (r'location\s*=.*event\.data', '将消息数据用于页面跳转')
            ]
            for pattern, desc in dangerous_ops:
                if re.search(pattern, handler, re.IGNORECASE | re.DOTALL):
                    self.vulnerabilities.append({
                        'type': 'unsafe_data_handling',
                        'description': f'message事件处理存在危险操作：{desc}',
                        'code_snippet': re.search(pattern, handler, re.IGNORECASE | re.DOTALL).group(0),
                        'severity': 'high',
                        'fix建议': '对event.data进行严格过滤和转义，避免直接用于DOM操作或代码执行'
                    })

    def _analyze_iframe_contexts(self):
        """分析iframe中的postMessage交互"""
        iframes = self.parser.soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '')
            if src:
                self.vulnerabilities.append({
                    'type': 'iframe_interaction',
                    'description': f'页面包含iframe（{src}），可能存在跨帧postMessage交互风险',
                    'severity': 'info',
                    'hint': '需确认iframe与父页面间的消息传递是否安全'
                })