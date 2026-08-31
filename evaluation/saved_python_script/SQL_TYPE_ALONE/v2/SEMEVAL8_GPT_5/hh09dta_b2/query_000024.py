import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()
    df_ah = tables["ii_ah"].copy()

    # Households participating and receiving income from Other Government Program
    prog_folios = (
        df_in.loc[df_in["in01a10_1"] == 1.0, ["folio"]]
        .dropna()
        .drop_duplicates()
    )

    # Individuals aged 30–50 with Individual ID 01 or 02
    df_portad = df_portad.loc[
        (df_portad["edad"] >= 30) & (df_portad["edad"] <= 50) & (df_portad["ls"].isin(["01", "02"])),
        ["folio", "ls", "ent", "edad"]
    ].copy()
    df_portad["ls_str"] = df_portad["ls"].astype(str).str.zfill(2)

    # Asset values (washing machine/stove)
    df_ah = df_ah.loc[:, ["folio", "ls", "ah04f_2"]].copy()
    df_ah = df_ah.loc[~df_ah["ah04f_2"].isna()].copy()
    df_ah["ls_str"] = pd.to_numeric(df_ah["ls"], errors="coerce").astype("Int64").astype(str).str.zfill(2)

    # Join individuals with asset values
    merged = pd.merge(df_portad, df_ah[["folio", "ls_str", "ah04f_2"]], on=["folio", "ls_str"], how="inner")

    # Keep only households participating in Other Government Program
    merged = pd.merge(merged, prog_folios, on="folio", how="inner")

    if merged.empty:
        return pd.DataFrame(columns=["state", "avg_ah04f_2"])

    # Map state codes to names
    state_map = {
        2: "Baja California",
        3: "Baja California Sur",
        4: "Campeche",
        5: "Coahuila",
        6: "Colima",
        7: "Chiapas",
        9: "Distrito Federal",
        10: "Durango",
        11: "Guanajuato",
        12: "Guerrero",
        13: "Hidalgo",
        14: "Jalisco",
        15: "Estado de México",
        16: "Michoacán",
        17: "Morelos",
        18: "Nayarit",
        19: "Nuevo León",
        20: "Oaxaca",
        21: "Puebla",
        22: "Querétaro",
        25: "Sinaloa",
        26: "Sonora",
        28: "Tamaulipas",
        29: "Tlaxcala",
        30: "Veracruz",
        31: "Yucatán",
        32: "Zacatecas",
    }
    ent_int = merged["ent"].astype("Int64")
    state_series = ent_int.map(state_map)
    state_series = state_series.where(~state_series.isna(), ent_int.astype(str))
    merged["state"] = state_series

    # Compute average ah04f_2 per state
    state_avgs = merged.groupby("state", as_index=False)["ah04f_2"].mean()

    # Overall mean across states (mean of state means)
    overall_mean = state_avgs["ah04f_2"].mean()

    # States above overall mean, sorted highest to lowest
    result = (
        state_avgs.loc[state_avgs["ah04f_2"] > overall_mean]
        .sort_values("ah04f_2", ascending=False)
        .rename(columns={"ah04f_2": "avg_ah04f_2"})
        .reset_index(drop=True)
    )

    return result