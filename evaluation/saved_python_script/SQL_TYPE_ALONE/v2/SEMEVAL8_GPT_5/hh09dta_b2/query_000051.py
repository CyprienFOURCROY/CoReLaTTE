import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()
    df_nna = tables["ii_nna"][["folio", "nna01"]].copy()

    # Deduplicate by household
    df_portad = df_portad.dropna(subset=["folio"]).drop_duplicates(subset=["folio"], keep="first")
    df_vlh = df_vlh.dropna(subset=["folio"]).drop_duplicates(subset=["folio"], keep="first")
    df_nna = df_nna.dropna(subset=["folio"]).drop_duplicates(subset=["folio"], keep="first")

    # Filter households that feel unsafe or very unsafe
    df_vlh_filt = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])]

    # Filter households that do not report owning/sharing a non-ag business
    df_nna_filt = df_nna[df_nna["nna01"] == 2.0]

    # Merge datasets
    m = df_vlh_filt.merge(df_nna_filt, on="folio", how="inner")
    m = m.merge(df_portad[["folio", "ent"]], on="folio", how="inner")

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
    m["ent_code"] = pd.to_numeric(m["ent"], errors="coerce").astype("Int64")
    m["state"] = m["ent_code"].map(state_map)
    # Fallback to code as string if not in map but present
    mask_missing = m["state"].isna() & m["ent_code"].notna()
    if mask_missing.any():
        m.loc[mask_missing, "state"] = m.loc[mask_missing, "ent_code"].astype(int).astype(str)
    # Drop rows with missing state entirely
    m = m.dropna(subset=["state"])

    # Count unique households by state
    counts = m.groupby("state", as_index=False)["folio"].nunique().rename(columns={"folio": "household_count"})

    # States with at least 30 households
    qualifying = counts[counts["household_count"] >= 30].copy()

    if qualifying.empty:
        return counts.iloc[0:0][["state", "household_count"]]

    avg_count = qualifying["household_count"].mean()
    result = qualifying[qualifying["household_count"] >= avg_count].copy()
    result = result.sort_values(by="household_count", ascending=False).reset_index(drop=True)

    return result