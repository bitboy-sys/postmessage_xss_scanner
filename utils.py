import re
import hashlib
from urllib.parse import urlparse, urlunparse, quote, unquote


def normalize_url(url):
    """标准化URL，处理可能的解析异常"""
    try:
        parsed = urlparse(url)

        scheme = parsed.scheme or ''
        netloc = parsed.netloc or ''
        path = re.sub(r'//+', '/', parsed.path) or ''
        params = parsed.params or ''
        query = parsed.query or ''
        fragment = ''  # 强制去除锚点

        url_components = (scheme, netloc, path, params, query, fragment)
        return urlunparse(url_components)
    except Exception as e:
        print(f"URL标准化失败 {url}: {str(e)}")
        return url

def get_domain(url):
    """从URL中提取域名（含端口）"""
    parsed = urlparse(url)
    return parsed.netloc

def is_same_origin(url1, url2):
    """判断两个URL是否同源"""
    parsed1 = urlparse(url1)
    parsed2 = urlparse(url2)
    return (parsed1.scheme == parsed2.scheme and
            parsed1.netloc == parsed2.netloc)

def get_url_hash(url):
    """生成URL的MD5哈希值，用于去重"""
    normalized = normalize_url(url)
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def extract_js_functions(html, function_name):
    """从HTML中提取指定名称的JavaScript函数体"""
    pattern = re.compile(
        rf'{function_name}\s*\([^)]*\)\s*{{([^}}]*)}}',
        re.IGNORECASE | re.DOTALL
    )
    return pattern.findall(html)

def escape_payload(payload):
    """对XSS Payload进行URL编码"""
    return quote(payload).replace('+', '%20')

# 新增：HTML转义函数，防止生成POC时破坏HTML结构
def html_escape(s):
    """HTML转义处理"""
    if not s:
        return ""
    return (s.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))