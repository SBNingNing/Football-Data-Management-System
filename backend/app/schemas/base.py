"""
Pydantic 基础模型配置
"""
from pydantic import BaseModel


class SchemaBase(BaseModel):
    class Config:
        orm_mode = True
        anystr_strip_whitespace = True
        validate_assignment = True
        # 兼容字段别名（如前端 studentId 等）
        allow_population_by_field_name = True

