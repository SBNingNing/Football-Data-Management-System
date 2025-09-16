"""
Pydantic 基础模型与通用构件（v2）
"""
from typing import Generic, List, Optional, TypeVar
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class SchemaBase(BaseModel):
    """项目中所有 Schema 的基类（v2）。"""
    # v2: 使用 model_config 代替内部 Config
    model_config = ConfigDict(
        from_attributes=True,  # v1 的 orm_mode
        str_strip_whitespace=True,  # v1 的 anystr_strip_whitespace
        validate_assignment=True,
        populate_by_name=True,  # v1 的 allow_population_by_field_name
    )


class ErrorResponse(SchemaBase):
    """标准错误响应结构（与现有 `status: error` 保持一致）。"""
    status: Literal['error'] = 'error'
    message: str
    code: Optional[str] = None


T = TypeVar('T')


class Success(SchemaBase, Generic[T]):
    """标准成功响应结构，兼容当前后端 envelope。

    注意：当前路由仍使用 jsonify 手工返回；此类型用于逐步接线与类型化。
    """
    status: Literal['success'] = 'success'
    data: Optional[T] = None
    message: Optional[str] = None


class PageMeta(SchemaBase):
    """分页元信息。"""
    total: int
    page: int = Field(..., alias='pageNum')
    page_size: int = Field(..., alias='pageSize')


class Page(SchemaBase, Generic[T]):
    """通用分页返回类型。"""
    items: List[T]
    meta: PageMeta


