import pandas as pd
import logging

logger = logging.getLogger(__name__)


def select_columns(df, columns):
    """Выбирает нужные колонки"""
    return df[columns]

def rename_columns(df, rename_mapping):
    """Переименовывает колонки"""
    rename_info = []
    for old_name, new_name in rename_mapping.items():
        rename_info.append(f"Renamed column '{old_name}' to '{new_name}'")
    return df.rename(columns=rename_mapping), rename_info

def apply_transformations(df, config):
    """Применяет все трансформации из YAML"""
    if not config.transform:
        return df, None
    
    transform_config = config.transform
    rename_info = []
    errors = []
    
    if transform_config.dfselector:
        select_columns_list = transform_config.dfselector['columns']
        df = df[select_columns_list]
        logger.info(f"Selected columns: {select_columns_list}")
    
    if transform_config.dfrename:
        rename_items = transform_config.dfrename['coolname']
        rename_mapping = {}
        for item in rename_items:
            old_name = item.oldname
            new_name = item.newname
            
            if old_name not in df.columns:
                error_msg = f"Column '{old_name}' not found in DataFrame. Available: {list(df.columns)}"
                logger.error(error_msg)
                errors.append(error_msg)
            elif new_name in df.columns and new_name != old_name:
                error_msg = f"Cannot rename '{old_name}' to '{new_name}': column already exists"
                logger.error(error_msg)
                errors.append(error_msg)
            else:
                rename_mapping[old_name] = new_name
                rename_info.append(f"Renamed column '{old_name}' to '{new_name}'")
        
        if rename_mapping:
            df = df.rename(columns=rename_mapping)
            for info in rename_info:
                logger.info(info)
    
    if errors:
        raise ValueError("; ".join(errors))
    
    return df, rename_info