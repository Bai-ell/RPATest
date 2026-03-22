import re
import pandas as pd
from pathlib import Path
from loguru import logger
from config import RPA_COLUMNS, PINDODO_COLUMNS

def parse_rpa_report(file_path: Path) -> pd.DataFrame:
    rows = []
    pattern = re.compile(
        r"^\s*(\d+)\s+(\d+)\s+(\d{8})(id\d+)\s+(\d+\.\d{2})([A-Z]{3})(\d+)\s+(\d+)\s*$"
    )

    if not file_path.exists():
        logger.error(f"Файл RPA не найден: {file_path}")
        return pd.DataFrame(columns=RPA_COLUMNS)

    with open(file_path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            raw = line.rstrip("\n")
            if not raw.strip(): continue
            match = pattern.match(raw)
            if not match:
                logger.warning(f"RPA: не удалось распарсить строку {line_no}: {raw[:50]}...")
                continue

            rows.append({
                "Number": match.group(1), "Index": match.group(2),
                "Local DateTime": match.group(3), "Transaction ID": match.group(4),
                "Transaction Amount": float(match.group(5)), "Currency": match.group(6),
                "Card Number": match.group(7), "Terminal ID": match.group(8),
            })

    df = pd.DataFrame(rows, columns=RPA_COLUMNS)
    logger.info(f"RPA отчет распарсен: {len(df)} строк")
    return df

def parse_pindodo_report(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        logger.error(f"Файл PINDODO не найден: {file_path}")
        return pd.DataFrame(columns=PINDODO_COLUMNS)

    records, current_record = [], {}
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped or (stripped.startswith("Description") and "Value" in stripped) or stripped == "tor":
                continue
            if set(stripped) == {"-"}:
                if current_record:
                    records.append(current_record)
                    current_record = {}
                continue
            if re.match(r"^\d{4}-\d{2}-\d{2},\s*[A-Z]{3}$", stripped): continue

            parts = re.split(r"\s{2,}", stripped)
            if len(parts) < 2:
                if not stripped.startswith("Electronic Commerce"):
                    logger.warning(f"PINDODO: не удалось распарсить строку {i}: {stripped[:50]}")
                continue
            
            current_record[parts[0].strip()] = parts[-1].strip()

    if current_record: records.append(current_record)
    df = pd.DataFrame(records)
    for col in PINDODO_COLUMNS:
        if col not in df.columns: df[col] = None
    
    df = df[PINDODO_COLUMNS]
    logger.info(f"PINDODO отчет распарсен: {len(df)} строк")
    return df