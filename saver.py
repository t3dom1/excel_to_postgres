import pandas as pd

def save_output(df, output_config):
    if not output_config.enabled:
        print("Output disabled")
        return
    
    output_type = output_config.format
    
    if output_type == 'csv':
        delimiter = output_config.csv_delimiter or ','
        encoding = output_config.csv_encoding or 'utf-8-sig'
        df.to_csv(output_config.path, index=False, sep=delimiter, encoding=encoding)
        print(f"Data exported to CSV: {output_config.path}")
        
    elif output_type == 'excel':
        df.to_excel(output_config.path, index=False)
        print(f"Data exported to Excel: {output_config.path}")
        
    elif output_type == 'json':
        orient = output_config.json_orient or 'records'
        force_ascii = output_config.json_force_ascii or False
        df_to_export = df.copy()
        df_to_export.index = df_to_export.index + 1
        df_to_export = df_to_export.reset_index().rename(columns={'index': '№'})
        df_to_export.to_json(output_config.path, orient=orient, force_ascii=force_ascii)
        print(f"Data exported to JSON: {output_config.path}")
    
    else:
        print(f"Unknown output type: {output_type}")