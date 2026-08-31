import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_su = tables["ii_su"][["folio", "su01"]].copy()
    df_in = tables["ii_in"][["folio", "in02a10"]].copy()

    # Households that use a plot/land for farming
    su_yes = df_su.loc[df_su["su01"] == 1, ["folio"]].drop_duplicates()

    # Households that received a positive amount directly from Other Government Program
    in_pos = df_in.loc[df_in["in02a10"].notna() & (df_in["in02a10"] > 0), ["folio"]].drop_duplicates()

    # Households satisfying both conditions
    eligible_folios = su_yes.merge(in_pos, on="folio", how="inner")

    # Map households to state
    ent_by_folio = df_portad.dropna(subset=["ent"]).drop_duplicates(subset=["folio"])[["folio", "ent"]]
    hh_with_state = eligible_folios.merge(ent_by_folio, on="folio", how="inner")

    if hh_with_state.empty:
        return pd.DataFrame(columns=["state", "num_households"])

    # Count households per state code
    counts = hh_with_state.groupby("ent").size().reset_index(name="num_households")

    # Filter states with at least 50 such households
    counts_50 = counts[counts["num_households"] >= 50].copy()
    if counts_50.empty:
        return pd.DataFrame(columns=["state", "num_households"])

    # Compute average among these states and filter above-average
    avg_count = counts_50["num_households"].mean()
    res = counts_50[counts_50["num_households"] > avg_count].copy()

    if res.empty:
        return pd.DataFrame(columns=["state", "num_households"])

    # Map state codes to names
    ent_map = {
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

    res = res.assign(
        ent_int=res["ent"].astype("Int64"),
        state=lambda d: d["ent_int"].map(ent_map).fillna(d["ent_int"].astype(str))
    ).sort_values("num_households", ascending=False)

    return res[["state", "num_households"]].reset_index(drop=True)