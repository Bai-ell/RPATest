import pandas as pd
from loguru import logger





def build_rpa_match_key(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["match_key"] = list(zip(
        result["Local DateTime"].astype(str).str.strip(),
        result["Transaction Amount"].astype(float),
        result["Currency"].astype(str).str.strip(),
        result["Card Number"].astype(str).str.strip(), 
        result["Terminal ID"].astype(str).str.strip(),
    ))
    return result


def build_pindodo_match_key(df: pd.DataFrame) -> pd.DataFrame:

    result = df.copy()
    result["Transaction Date Normalized"] = (
        pd.to_datetime(result["Transaction Date"], errors="coerce")
        .dt.strftime("%Y%m%d")
    )
    result["match_key"] = list(zip(
        result["Transaction Date Normalized"].astype(str).str.strip(), 
        pd.to_numeric(result["Transaction Amount"], errors="coerce"),
        result["Transaction Currency"].astype(str).str.strip(),   
        result["Retrieval Reference Number"].astype(str).str.strip(),   
        result["Card Acceptor Terminal ID"].astype(str).str.strip(),      
    ))
    return result


def reconcile_reports(rpa_df: pd.DataFrame, pindodo_df: pd.DataFrame):
    logger.info("Начало процесса сверки данных...")
    
    rpa_norm = build_rpa_match_key(rpa_df)
    pindodo_norm = build_pindodo_match_key(pindodo_df)

    rpa_keys = set(rpa_norm["match_key"])
    pindodo_keys = set(pindodo_norm["match_key"])

    success_keys = rpa_keys & pindodo_keys
    rpa_failed_keys = rpa_keys - pindodo_keys
    pindodo_failed_keys = pindodo_keys - rpa_keys

    success_df = rpa_norm[rpa_norm["match_key"].isin(success_keys)].copy()
    rpa_failed_df = rpa_norm[rpa_norm["match_key"].isin(rpa_failed_keys)].copy()
    pindodo_failed_df = pindodo_norm[pindodo_norm["match_key"].isin(pindodo_failed_keys)].copy()

    for df in [success_df, rpa_failed_df, pindodo_failed_df]:
        if "match_key" in df.columns:
            df.drop(columns=["match_key"], inplace=True)
    
    if "Transaction Date Normalized" in pindodo_failed_df.columns:
        pindodo_failed_df.drop(columns=["Transaction Date Normalized"], inplace=True)

    logger.info(f"Сверка завершена: {len(success_df)} успешно, {len(rpa_failed_df)} ошибок RPA, {len(pindodo_failed_df)} ошибок Pindodo.")
    
    return success_df, rpa_failed_df, pindodo_failed_df