"""context_middleware.py
为请求提供一个统一的 g.ctx 容器: 结构 { attached: {<模块>: 任意} }
中间件和路由之间通过 g.ctx.attached 传递派生数据, 避免随意向 g 挂载散乱属性。
使用方式:
  在需要的地方: from flask import g; g.ctx.attach('team', team_obj)
  读取: team = g.ctx.get('team')
"""
from dataclasses import dataclass, field
from flask import g

@dataclass
class RequestContext:
    attached: dict = field(default_factory=dict)

    def attach(self, key: str, value):
        self.attached[key] = value

    def get(self, key: str, default=None):
        return self.attached.get(key, default)


def ensure_request_context():
    if not hasattr(g, 'ctx'):
        g.ctx = RequestContext()  # type: ignore[attr-defined]
    return g.ctx
