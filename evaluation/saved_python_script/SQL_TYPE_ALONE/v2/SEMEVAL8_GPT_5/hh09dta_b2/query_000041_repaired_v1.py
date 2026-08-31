import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].dropna(subset=["folio"]).drop_duplicates(subset=["folio"])
    df_vlh = tables["ii_vlh"][["folio", "vlh12a_a", "vlh12a_c"]].dropna(subset=["folio"]).drop_duplicates(subset=["folio"])
    df_ah = tables["ii_ah"][["folio", "ah03g"]].dropna(subset=["folio"])

    # Households with at least one member owning a domestic appliance
    hh_domestic = (
        df_ah.assign(has_domestic=lambda d: d["ah03g"] == 1.0)
            .groupby("folio", as_index=False)["has_domestic"]
            .any()
    )

    merged = (
        hh_domestic.merge(df_vlh, on="folio", how="left")
                   .merge(df_portad[["folio", "ent"]], on="folio", how="left")
    )

    merged = merged[merged["has_domestic"]].copy()
    merged = merged[~merged["ent"].isna()].copy()
    merged["ent"] = merged["ent"].astype("Int64")

    merged["no_since_2005"] = (merged["vlh12a_c"] == 3.0).fillna(False)
    merged["yes_current_since_2005"] = (merged["vlh12a_a"] == 1.0).fillna(False)

    agg = (
        merged.groupby("ent")
        .agg(
            total_households=("folio", "nunique"),
            no_since_2005=("no_since_2005", "sum"),
            yes_current_since_2005=("yes_current_since_2005", "sum"),
        )
        .reset_index()
    )

    # Filter states meeting criteria
    result = agg[(agg["total_households"] >= 25) & (agg["no_since_2005"] > agg["yes_current_since_2005"])].copy()

    # Optional: add state names
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
    result["state"] = result["ent"].map(state_map)

    result = result.sort_values(["ent"]).reset_index(drop=True)
    return result[["ent", "state", "total_households", "no_since_2005", "yes_current_since_2005"]]