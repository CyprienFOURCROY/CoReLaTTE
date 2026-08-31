import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_vlh = tables["ii_vlh"]

    # Filter households in Oaxaca (20) and Puebla (21) with interviewee aged 25+
    df_p = df_portad[
        df_portad["ent"].isin([20.0, 21.0]) & (df_portad["edad"] >= 25)
    ][["folio", "ent"]].drop_duplicates(subset=["folio"])

    # Merge required info
    df = (
        df_p.merge(df_crh[["folio", "crh04_1", "crh04_2"]], on="folio", how="left")
            .merge(df_vlh[["folio", "vlh04"]], on="folio", how="left")
    )

    # Keep only numeric total debt (including interest) and at least 5,000 pesos
    df = df[(df["crh04_1"] == 1.0) & df["crh04_2"].notna() & (df["crh04_2"] >= 5000)]

    # Map state codes to names
    state_map = {20.0: "Oaxaca", 21.0: "Puebla"}
    df["state"] = df["ent"].map(state_map)

    # Group by state and compute aggregates
    result = (
        df.groupby("state", as_index=False)
        .agg(
            avg_feel_safe_at_home=("vlh04", "mean"),
            avg_total_debt=("crh04_2", "mean"),
            n_households=("folio", "nunique"),
        )
        .sort_values(by="avg_feel_safe_at_home", ascending=True)
        .reset_index(drop=True)
    )

    return result