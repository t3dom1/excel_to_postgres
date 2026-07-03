# Excel to PostgreSQL ETL Pipeline

**Version:** 1.0.0  
**Status:** Production  
**License:** MIT

---

## 1. Overview

The Excel to PostgreSQL ETL Pipeline is an enterprise-grade data integration solution designed for automated extraction, transformation, and loading of structured Excel data into PostgreSQL databases. The system features YAML-based configuration, comprehensive logging, and robust error handling, making it suitable for production environments.

---

## 2. Core Functionality

| Component | Description |
|-----------|-------------|
| **Data Sources** | GitHub repository, local filesystem, direct PostgreSQL read |
| **Data Processing** | Multi-sheet Excel parsing, custom row mapping, data type conversion, currency symbol cleaning |
| **Data Transformation** | Column selection, column renaming, data validation |
| **Data Output** | CSV export (configurable delimiters/encoding), Excel workbook generation, JSON export |
| **Database Operations** | Automatic table creation, full data refresh (truncate and load), connection management |

---

## 3. System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      CONFIGURATION LAYER                       │
│                         yaml_file.yml                          │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                        VALIDATION LAYER                        │
│                          validator.py                          │
│                  (Pydantic schema validation)                  │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────┐                               
│                                               │
│                    Config                     │
│                                               │
└────────────────────────┬──────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                        DATA LOADING LAYER                      │
│                            loader.py                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐   │
│  │  GitHub Client  │  │  Local Reader   │  │  PostgreSQL   │   │
│  └─────────────────┘  └─────────────────┘  │    Reader     │   │
│                                            └───────────────┘   │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────┐                               
│                                               │
│                 Date Frame                    │
│                                               │
└────────────────────────┬──────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                      TRANSFORMATION LAYER                      │
│                         transformer.py                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐   │
│  │  Column Select  │  │  Column Rename  │  │  Data Clean   │   │
│  └─────────────────┘  └─────────────────┘  └───────────────┘   │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────┐                               
│                                             │
│                 Date Frame                  │
│                                             │
└────────────────────────┬────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                          OUTPUT LAYER                          │
│                            saver.py                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐   │
│  │  CSV Export     │  │  Excel Export   │  │  JSON Export  │   │
│  └─────────────────┘  └─────────────────┘  └───────────────┘   │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                          DATABASE LAYER                        │
│                              db.py                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐   │
│  │  Table Create   │  │  Data Insert    │  │  Log Write    │   │
│  └─────────────────┘  └─────────────────┘  └───────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

---

## 4. Project Structure

```
excel_to_postgres/
│
├── src/
│   ├── validator.py          # YAML configuration validation
│   ├── transformer.py        # Data transformation logic
│   ├── loader.py             # Data loading from sources
│   ├── saver.py              # Data export utilities
│   ├── db.py                 # PostgreSQL operations
│   └── logger_setup.py       # Logging configuration
│
├── main.py                   # ETL pipeline entry point
├── yaml_file.yml             # Configuration file
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
└── LICENSE                   # MIT License
```

---

## 5. Installation Guide

### 5.1. System Requirements

| Component | Minimum Version |
|-----------|-----------------|
| Python | 3.8+ |
| PostgreSQL | 11+ |
| Operating System | Linux, Windows, macOS |

### 5.2. Installation Steps

**Step 1: Clone Repository**
```bash
git clone https://github.com/t3dom1/excel_to_postgres.git
cd excel_to_postgres
```

**Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 3: Configure PostgreSQL**
```sql
CREATE DATABASE spark_db;
CREATE USER spark_user WITH PASSWORD 'spark_pass';
GRANT ALL PRIVILEGES ON DATABASE spark_db TO spark_user;
```

**Step 4: Create Required Tables**
```sql
CREATE TABLE excel_data (
    fio VARCHAR(255),
    summa NUMERIC(15,2),
    chel INTEGER,
    sheet_name VARCHAR(50)
);

CREATE TABLE etl_log (
    id SERIAL PRIMARY KEY,
    run_id INTEGER,
    run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20),
    stage VARCHAR(30),
    records_processed INTEGER DEFAULT 0,
    total_sum NUMERIC(15,2) DEFAULT 0,
    duration_seconds NUMERIC(10,2) DEFAULT 0,
    error_message TEXT
);
```

---

## 6. Configuration

### 6.1. YAML Configuration File

Edit `yaml_file.yml`:

```yaml
conn_type:
  type: "hybrid"
  param:
    url: "https://api.github.com/repos/t3dom1/Excel_Auto_Updater/contents/Book.xlsx"
    local_file: "Book.xlsx"
    host: "postgres"
    port: 5432
    database: "spark_db"
    user: "spark_user"
    password: "spark_pass"

tables:
  data: "excel_data"
  log: "etl_log"

parse:
  rows: [7, 11, 15, 19, 23]

output:
  enabled: true
  format: "csv"
  path: "output_data.csv"
  csv_delimiter: ","
  csv_encoding: "utf-8-sig"

columns: ["fio", "summa", "chel", "sheet_name"]

transform:
  dfselector:
    columns: ["fio", "summa", "chel", "sheet_name"]
  dfrename:
    coolname:
      - oldname: "fio"
        newname: "ФИО"
      - oldname: "summa"
        newname: "Сумма"
      - oldname: "chel"
        newname: "Чел"
      - oldname: "sheet_name"
        newname: "Название_листа"
```

### 6.2. Configuration Parameters

| Section | Parameter | Description |
|---------|-----------|-------------|
| **conn_type** | type | Connection mode: `postgres`, `local`, `hybrid` |
| | url | GitHub API URL for file download |
| | local_file | Local file path |
| | host, port, database, user, password | PostgreSQL credentials |
| **tables** | data | Name of data table |
| | log | Name of logging table |
| **parse** | rows | Row numbers to extract data from |
| **output** | enabled | Enable/disable export |
| | format | Output format: `csv`, `excel`, `json` |
| | path | Output file path |
| **columns** | - | Columns to include in output |
| **transform** | dfselector.columns | Columns to select |
| | dfrename.coolname | Column renaming mapping |

---

## 7. Usage

### 7.1. Running the Pipeline

```bash
python main.py
```

### 7.2. Expected Output

```
====================================================================
                             RESULT
====================================================================
   №                         ФИО     Сумма     Чел   Название_листа
   1       Иванов Иван Иванович      45000      1        Лист 1
   2     Петрова Анна Сергеевна      67500      1        Лист 1
   3   Смирнов Дмитрий Алексеевич    123000     3        Лист 1
   4  Кузнецова Ольга Владимировна   89200      2        Лист 1
   5     Попов Андрей Викторович     34800      1        Лист 1
   6  Соколова Екатерина Дмитриевна  56300      2        Лист 2
   7   Васильев Павел Александрович  92750      4        Лист 2
   8   Михайлова Ирина Викторовна    41200      1        Лист 2
   9     Новиков Денис Сергеевич     78400      3        Лист 2
  10   Федорова Наталья Андреевна    104500     5        Лист 2
  11  Григорьев Евгений Олегович     37450.5    1        Лист 3
  12      Зайцева Мария Петровна     63281      2        Лист 3
  13  Морозов Александр Игоревич     88000      3        Лист 3
  14    Волкова Юлия Владимировна    52000      2        Лист 3
  15    Павлов Роман Валерьевич      72340      4        Лист 3
===================================================================
```

### 7.3. Logging Output

```
[2026-07-03 10:00:00] INFO: Run 1734567890
[2026-07-03 10:00:00] INFO: Hybrid mode: checking GitHub first
[2026-07-03 10:00:01] INFO: File downloaded from GitHub: Book.xlsx
[2026-07-03 10:00:01] INFO: Parsed 15 records from Excel
[2026-07-03 10:00:02] INFO: Loaded 15 records to PostgreSQL
[2026-07-03 10:00:02] INFO: Success. Records: 15, Total sum: 1,046,321.49
```

---

## 8. Dependencies

```txt
pandas>=1.3.0
openpyxl>=3.0.9
psycopg2-binary>=2.9.0
sqlalchemy>=1.4.0
requests>=2.25.0
pydantic>=2.0.0
pyyaml>=6.0
```

---

## 9. Error Handling

The pipeline implements comprehensive error handling:

| Error Type | Handling |
|------------|----------|
| Configuration errors | Validated by Pydantic schema |
| File not found | Fallback to local file or raises exception |
| Database connection | Logs error and raises exception |
| Data parsing errors | Catches and logs with detailed message |
| Transformation errors | Validates column existence before applying |

All errors are logged to both console and the `etl_log` database table.

---

## 10. Logging

Logs are written to two locations:

| Location | Content |
|----------|---------|
| **Console** | Real-time execution status with timestamps |
| **PostgreSQL (etl_log)** | Persistent log with run_id, status, stage, records_processed, total_sum, duration_seconds, error_message |

### 10.1. Log Query Examples

```sql
-- View all logs
SELECT * FROM etl_log ORDER BY run_timestamp DESC;

-- View logs for specific run
SELECT * FROM etl_log WHERE run_id = 1734567890;

-- View error logs
SELECT * FROM etl_log WHERE status = 'ERROR';
```

---

## 11. License

This project is distributed under the MIT License.

```
MIT License

Copyright (c) 2026 t3dom1

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 12. Contact

- **Author:** t3dom1
- **Repository:** https://github.com/t3dom1/excel_to_postgres
- **Issues:** https://github.com/t3dom1/excel_to_postgres/issues
