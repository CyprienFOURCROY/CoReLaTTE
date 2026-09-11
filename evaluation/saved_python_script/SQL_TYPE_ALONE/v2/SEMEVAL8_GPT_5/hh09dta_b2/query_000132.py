import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_su = tables["ii_su"][["folio", "su01", "su237"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh01_1b"]].copy()

    df_su_yes = df_su[df_su["su01"] == 1.0]
    df_bank = df_crh[df_crh["crh01_1b"] == 2.0]

    merged = pd.merge(df_su_yes, df_bank, on="folio", how="inner")

    valid = merged["su237"].notna()
    if merged.loc[valid, "su237"].empty:
        return pd.DataFrame({"folio": pd.Series(dtype=df_su["folio"].dtype),
                             "amount": pd.Series(dtype="float64")})

    avg_workers = merged.loc[valid, "su237"].mean()

    result = merged[merged["su237"] > avg_workers].copy()
    result = result[["folio", "su237"]].rename(columns={"su237": "amount"})
    result = result.sort_values(by="amount", ascending=False).reset_index(drop=True)
    return result