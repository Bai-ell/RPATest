from pathlib import Path
from loguru import logger
from logger import setup_logger
from parsers import parse_rpa_report, parse_pindodo_report
from proces import reconcile_reports
import pandas as pd

@logger.catch 
def main():
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    output_dir = base_dir / "output"

    setup_logger(output_dir)
    logger.info("--- СТАРТ ПРОЦЕССА СВЕРКИ ---")

    rpa_df = parse_rpa_report(data_dir /"RPA" / "RpaBank_report.txt")
    pindodo_df = parse_pindodo_report(data_dir / "PINDODO" / "Pindodo_report.txt")

    success, rpa_fail, pindo_fail = reconcile_reports(rpa_df, pindodo_df)
    rpa_df.to_excel(
    output_dir / "RpaBank_report.xlsx",
    index=False
    )

    pindodo_df.to_excel(
    output_dir / "Pindodo_report.xlsx",
    index=False
    )

    with pd.ExcelWriter(output_dir / "reconciliation_report.xlsx") as writer:
        success.to_excel(writer, sheet_name="Успешные", index=False)
        rpa_fail.to_excel(writer, sheet_name="RpaBank_неуспешные", index=False)
        pindo_fail.to_excel(writer, sheet_name="Pindodo_неуспешные", index=False)

    logger.info(f"Сверка завершена. Отчет: {output_dir / 'reconciliation_report.xlsx'}")

if __name__ == "__main__":
    main()