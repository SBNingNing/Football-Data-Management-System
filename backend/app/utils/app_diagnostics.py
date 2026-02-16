"""应用运行期诊断工具（源自已废弃的 main.py）。

主要功能：
    1. get_app_info(app): 汇总应用的基础信息（名称 / 版本 / 调试模式 / 环境 / 已注册蓝图）。
    2. validate_app_configuration(app): 校验关键配置项与预期蓝图是否完整，返回 (是否通过, 错误列表)。

设计说明：
    - 原先散落在 `app/main.py` 中的辅助函数已迁移到此，保持后端“单一启动入口”(`run.py`) 的清晰性。
    - 不直接抛异常：配置缺失以日志警告形式提示，避免影响开发初期启动。
    - 若未来需要更严格模式，可在 `run.py` 中对返回结果进行强制中断处理。
"""
from __future__ import annotations
from typing import Dict, Any, Tuple, List

REQUIRED_CONFIGS = [
    # Flask / 安全相关
    'SECRET_KEY',
    # 数据库连接
    'SQLALCHEMY_DATABASE_URI',
    # JWT 鉴权密钥
    'JWT_SECRET_KEY'
]

# 期望注册的蓝图（根据当前业务模块列出；若后续新增/裁剪模块，可同步调整）
EXPECTED_BLUEPRINTS = [
    'auth', 'matches', 'events', 'teams', 'tournaments',
    'competitions', 'seasons', 'player_history', 'team_history', 'players', 'stats', 'health'
]


def get_app_info(app) -> Dict[str, Any]:  # type: ignore
    """收集应用基础运行信息（非敏感，供日志或调试用）。"""
    return {
        'app_name': app.config.get('APP_NAME', 'Unknown'),
        'app_version': app.config.get('APP_VERSION', 'Unknown'),
        'debug_mode': app.config.get('DEBUG', False),
        'environment': app.config.get('ENV', 'Unknown'),
        # 仅显示 URI 字符串，不做进一步解析（避免无意打印敏感凭据）
        'database_uri': app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured'),
        'registered_blueprints': list(app.blueprints.keys())
    }


def validate_app_configuration(app) -> Tuple[bool, List[str]]:  # type: ignore
    """校验关键配置 + 蓝图注册完整性。

    返回:
        (passed, errors)
        passed: 全部通过为 True
        errors: 失败原因的字符串列表
    """
    errors: List[str] = []

    # 配置项检查
    for key in REQUIRED_CONFIGS:
        if not app.config.get(key):
            errors.append(f"缺少必要配置: {key}")

    # 蓝图注册检查
    registered = list(app.blueprints.keys())
    missing_bps = [bp for bp in EXPECTED_BLUEPRINTS if bp not in registered]
    if missing_bps:
        errors.append(f"缺少蓝图注册: {', '.join(missing_bps)}")

    return (len(errors) == 0, errors)
