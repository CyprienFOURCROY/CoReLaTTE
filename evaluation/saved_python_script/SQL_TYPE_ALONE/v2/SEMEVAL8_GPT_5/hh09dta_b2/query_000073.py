import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_in = tables["ii_in"][["folio", "in03a"]].copy()
    liconsa = (
        df_in.assign(liconsa=lambda d: d["in03a"] == 1.0)
        .groupby("folio", as_index=False)["liconsa"]
        .max()
    )
    liconsa_yes = liconsa[liconsa["liconsa"]].drop(columns=["liconsa"])

    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()
    unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])][["folio"]].drop_duplicates()

    eligible = liconsa_yes.merge(unsafe, on="folio", how="inner")

    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    ent_by_folio = (
        df_portad.dropna(subset=["ent"])
        .assign(ent=lambda d: d["ent"].astype("int64"))
        .groupby("folio", as_index=False)
        .agg(ent=("ent", "first"))
    )

    eligible_ent = eligible.merge(ent_by_folio, on="folio", how="inner")

    counts = (
        eligible_ent.groupby("ent", as_index=False)
        .agg(households_count=("folio", "nunique"))
    )

    if counts.empty:
        return pd.DataFrame(columns=["state", "households_count"])

    avg = counts["households_count"].mean()
    counts_filtered = counts[counts["households_count"] >= avg]

    counts_sorted = counts_filtered.sort_values(
        by=["households_count", "ent"], ascending=[False, True]
    )
    top5 = counts_sorted.head(5).copy()

    ent_mapping = {
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

    top5["state"] = top5["ent"].map(ent_mapping).fillna(top5["ent"].astype(str))
    return top5[["state", "households_count"]]