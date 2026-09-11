import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_vlh = tables["ii_vlh"][["folio", "vlh04", "vlh18a"]].drop_duplicates(subset=["folio"]).copy()
    df_nna = tables["ii_nna"][["folio", "nna01"]].drop_duplicates(subset=["folio"]).copy()
    df_portad = tables["ii_portad"][["folio", "ent"]].drop_duplicates(subset=["folio"]).copy()

    df = df_vlh.merge(df_nna, on="folio", how="inner").merge(df_portad, on="folio", how="inner")

    cond = df["vlh04"].isin([1.0, 2.0]) & (df["nna01"] == 1.0)
    df_sel = df.loc[cond].copy()
    df_sel = df_sel[df_sel["vlh18a"].notna()].copy()

    if df_sel.empty:
        return pd.DataFrame(columns=["state", "average_vlh18a", "household_count"])

    df_sel["ent"] = df_sel["ent"].astype("Int64")

    national_avg = df_sel["vlh18a"].mean()

    grp = (
        df_sel.groupby("ent")
        .agg(average_vlh18a=("vlh18a", "mean"), household_count=("folio", "size"))
        .reset_index()
    )

    grp = grp[(grp["household_count"] >= 50) & (grp["average_vlh18a"] > national_avg)].copy()

    if grp.empty:
        return pd.DataFrame(columns=["state", "average_vlh18a", "household_count"]).astype(
            {"state": "object", "average_vlh18a": "float64", "household_count": "int64"}
        )

    ent_to_state = {
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

    grp["state"] = grp["ent"].astype("Int64").map(ent_to_state)
    grp["state"] = grp["state"].fillna(grp["ent"].astype(str))

    grp = grp.sort_values(by=["average_vlh18a", "state"], ascending=[False, True]).reset_index(drop=True)

    return grp[["state", "average_vlh18a", "household_count"]]