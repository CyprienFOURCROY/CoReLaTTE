import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_in = tables["ii_in"][["folio", "in02a10"]].copy()
    df_in = df_in[df_in["in02a10"].notna() & (df_in["in02a10"] > 0)]

    df_vlh = tables["ii_vlh"][["folio", "vlh18a"]].copy()
    df = pd.merge(df_in, df_vlh, on="folio", how="inner")

    df_portad = tables["ii_portad"][["folio", "ent"]].copy().drop_duplicates(subset=["folio"])
    df = pd.merge(df, df_portad, on="folio", how="left")
    df = df[df["ent"].notna()]

    overall_avg = df["vlh18a"].mean()

    grp = (
        df.groupby("ent", as_index=False)
          .agg(household_count=("folio", "nunique"),
               avg_robberies=("vlh18a", "mean"))
    )

    grp = grp[grp["household_count"] >= 30]
    res = grp[grp["avg_robberies"] > overall_avg].copy()

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

    res["ent_code"] = res["ent"].astype("Int64")
    res["state"] = res["ent_code"].map(state_map)
    res = res.rename(columns={"avg_robberies": "avg_robberies_since_2005"})
    res = res.sort_values(by="avg_robberies_since_2005", ascending=False)
    return res[["ent_code", "state", "household_count", "avg_robberies_since_2005"]].reset_index(drop=True)