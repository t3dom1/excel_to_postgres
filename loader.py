import requests
import base64
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def download_from_github(url, local_file):
    try:
        logger.info("Attempting to download file from GitHub")
        response = requests.get(url, headers={'Accept': 'application/vnd.github.v3+json'})
        
        if response.status_code == 200:
            data = response.json()
            content = base64.b64decode(data['content'])
            with open(local_file, 'wb') as f:
                f.write(content)
            logger.info(f"File downloaded from GitHub: {local_file}")
            return True
        else:
            logger.warning(f"GitHub file not found (status: {response.status_code})")
            return False
    except Exception as e:
        logger.warning(f"GitHub download failed: {e}")
        return False

def parse_excel_file(local_file, rows_to_parse):
    logger.info("Parsing Excel file")
    xl = pd.ExcelFile(local_file)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(local_file, sheet_name=sheet, header=None)
        for row in rows_to_parse:
            if row < len(df):
                name = df.iloc[row, 0]
                amount = df.iloc[row, 3]
                people = df.iloc[row, 6]
                if pd.notna(name) and pd.notna(amount):
                    all_data.append({
                        'fio': str(name).strip(),
                        'summa': float(str(amount).replace(' ₽', '').replace('₽', '').replace(' ', '').replace(',', '.')),
                        'chel': int(people) if pd.notna(people) else 0,
                        'sheet_name': sheet
                    })
    
    df_result = pd.DataFrame(all_data)
    df_result.index = df_result.index + 1
    return df_result