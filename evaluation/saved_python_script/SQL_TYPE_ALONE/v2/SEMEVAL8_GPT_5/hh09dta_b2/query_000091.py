import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()

    # Unique state per household
    port = df_portad[["folio", "ent"]].drop_duplicates(subset=["folio"])

    # Merge to attach state to household-level program info
    df = df_in[["folio", "in03a", "in02a10"]].merge(port, on="folio", how="left")

    # Filter households that received Liconsa milk
    df_rec = df[df["in03a"] == 1.0].copy()
    df_rec = df_rec[~df_rec["ent"].isna()].copy()

    # Count households per state
    counts = (
        df_rec.groupby("ent", as_index=False)["folio"]
        .nunique()
        .rename(columns={"folio": "num_households"})
    )

    # States with at least 25 such households
    eligible_ents = counts[counts["num_households"] >= 25]["ent"]

    # Mean amount received directly from Other Government Program per state
    means = df_rec.groupby("ent", as_index=False)["in02a10"].mean()

    # Combine and keep eligible states
    st_all = means.merge(counts, on="ent", how="left")
    st_all = st_all[st_all["ent"].isin(eligible_ents)].copy()

    # Overall average across those states (mean of state means)
    overall_avg = st_all["in02a10"].mean(skipna=True)

    # Rank states by their average (descending) among eligible states
    st_all["rank"] = st_all["in02a10"].rank(method="dense", ascending=False).astype("Int64")

    # Filter states above the overall average
    st = st_all[st_all["in02a10"] > overall_avg].copy()

    # Map state names
    mapping = {
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

    st["state_code"] = st["ent"].astype("Int64")
    st["state"] = st["state_code"].map(mapping)
    st = st.rename(columns={"in02a10": "avg_in02a10"})
    st["overall_avg"] = overall_avg

    st = st.sort_values(["avg_in02a10", "state_code"], ascending=[False, True]).reset_index(drop=True)

    return st[["state_code", "state", "num_households", "avg_in02a10", "overall_avg", "rank"]]