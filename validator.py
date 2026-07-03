import yaml
from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Dict, Any, Optional, Union

class ConnType(BaseModel):
    type: Literal['hybrid', 'postgres', 'local']
    param: Dict[str, Any]

    @field_validator('param')
    @classmethod
    def validate_param(cls, v, info):
        conn_type = info.data.get('type')
        if conn_type in ['hybrid', 'local']:
            if 'url' not in v or 'local_file' not in v:
                raise ValueError("'url' and 'local_file' required for hybrid/local")
        if conn_type in ['hybrid', 'postgres']:
            required = ['host', 'port', 'database', 'user', 'password']
            missing = [f for f in required if f not in v]
            if missing:
                raise ValueError(f"Missing fields: {missing}")
        return v

class Tables(BaseModel):
    data: str
    log: str

class Parse(BaseModel):
    rows: List[int]

    @field_validator('rows')
    @classmethod
    def validate_rows(cls, v):
        if not v or any(r < 0 for r in v):
            raise ValueError("Rows must be non-empty list of positive integers")
        return v

class Output(BaseModel):
    enabled: bool = True
    format: Literal['csv', 'excel', 'json']
    path: str
    csv_delimiter: Optional[str] = ','
    csv_encoding: Optional[str] = 'utf-8-sig'
    json_orient: Optional[str] = 'records'
    json_force_ascii: Optional[bool] = False

class Logging(BaseModel):
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR']
    format: str

class RenameItem(BaseModel):
    oldname: str
    newname: str

    @field_validator('oldname')
    @classmethod
    def validate_oldname(cls, v):
        allowed = ['fio', 'summa', 'chel', 'sheet_name']
        if v not in allowed:
            raise ValueError(f"Invalid oldname: {v}. Allowed: {allowed}")
        return v

class Transform(BaseModel):
    dfselector: Dict[str, List[str]]
    dfrename: Dict[str, List[RenameItem]]

    @field_validator('dfselector')
    @classmethod
    def validate_dfselector(cls, v):
        if 'columns' not in v:
            raise ValueError("dfselector must have 'columns' key")
        return v

    @field_validator('dfrename')
    @classmethod
    def validate_dfrename(cls, v):
        if 'coolname' not in v:
            raise ValueError("dfrename must have 'coolname' key")
        return v

class ConfigModel(BaseModel):
    conn_type: ConnType
    tables: Tables
    parse: Parse
    output: Output
    logging: Logging
    columns: List[str]
    transform: Optional[Transform] = None

    @field_validator('columns')
    @classmethod
    def validate_columns(cls, v):
        allowed = ['fio', 'summa', 'chel', 'sheet_name']
        for col in v:
            if col not in allowed:
                raise ValueError(f"Invalid column: {col}. Allowed: {allowed}")
        if len(set(v)) != len(v):
            raise ValueError("Duplicate columns")
        return v

def validate_yaml(file_path: str) -> ConfigModel:
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    return ConfigModel(**data)