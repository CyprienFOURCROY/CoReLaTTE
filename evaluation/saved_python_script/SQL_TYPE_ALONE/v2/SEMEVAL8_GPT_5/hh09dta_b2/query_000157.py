import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_in = tables["ii_in"].copy()
    df_nna = tables["ii_nna"].copy()

    # Identify households where any member owns/shares a non-ag business
    nna_flag = (
        df_nna.assign(nna01_yes=df_nna["nna01"] == 1)
        .groupby("folio", as_index=False)["nna01_yes"]
        .max()
    )

    # Merge flags into income table
    df = df_in.merge(nna_flag, on="folio", how="left")
    df["nna01_yes"] = df["nna01_yes"].fillna(False)

    # Filter: owns/shares non-ag business AND participated and received income from Other Government Program
    mask = (df["nna01_yes"]) & (df["in01a10_1"] == 1)
    group_df = df.loc[mask, ["folio", "in02a10"]].copy()
    group_df = group_df[group_df["in02a10"].notna()]

    if group_df.empty:
        return pd.DataFrame(columns=["folio", "in02a10"])

    avg_amount = group_df["in02a10"].mean()

    res = group_df[group_df["in02a10"] > avg_amount].copy()
    res = res.sort_values(by="in02a10", ascending=False).reset_index(drop=True)

    return res