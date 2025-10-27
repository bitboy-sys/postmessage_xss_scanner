import re
from urllib.parse import urlparse, urljoin


def extract_links(html, base_url):
    """从HTML中提取所有链接"""
    links = []

    # 提取a标签href
    a_pattern = re.compile(r'<a[^>]+href=["\']([^"\']+)["\']', re.IGNORECASE)
    for match in a_pattern.findall(html):
        if match.startswith(('http://', 'https://')):
            links.append(match)
        elif match.startswith('#'):
            continue  # 跳过锚点链接
        else:
            absolute_url = urljoin(base_url, match)
            links.append(absolute_url)

    # 提取iframe src
    iframe_pattern = re.compile(r'<iframe[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
    for match in iframe_pattern.findall(html):
        if match.startswith(('http://', 'https://')):
            links.append(match)
        else:
            absolute_url = urljoin(base_url, match)
            links.append(absolute_url)

    # 提取frame src
    frame_pattern = re.compile(r'<frame[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
    for match in frame_pattern.findall(html):
        if match.startswith(('http://', 'https://')):
            links.append(match)
        else:
            absolute_url = urljoin(base_url, match)
            links.append(absolute_url)

    return links


def is_valid_url(url, base_domain, allowed_domains, exclude_paths):
    """检查URL是否符合扫描条件"""
    parsed = urlparse(url)

    # 检查协议
    if parsed.scheme not in ('http', 'https'):
        return False

    # 检查域名
    if allowed_domains:
        if parsed.netloc not in allowed_domains:
            return False
    else:
        if parsed.netloc != base_domain and not parsed.netloc.endswith('.' + base_domain):
            return False

    # 检查排除路径
    for path in exclude_paths:
        if parsed.path.startswith(path):
            return False

    return True