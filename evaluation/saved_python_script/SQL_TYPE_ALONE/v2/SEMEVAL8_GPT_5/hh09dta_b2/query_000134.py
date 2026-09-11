import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "edad"]].copy()
    df_crh = tables["ii_crh"][["folio", "crh02_1"]].copy()

    # Determine households with at least one adult (>=18) and at least one child (<18)
    df_portad["is_adult"] = df_portad["edad"] >= 18
    df_portad["is_child"] = df_portad["edad"] < 18
    hh_age_comp = (
        df_portad.groupby("folio")[["is_adult", "is_child"]]
        .any()
        .reset_index()
    )
    hh_with_both = hh_age_comp[(hh_age_comp["is_adult"]) & (hh_age_comp["is_child"])][["folio"]]

    # Households that reported owing money on credit/loans in the last 12 months
    owed_hh = df_crh[df_crh["crh02_1"] == 1][["folio"]].dropna().drop_duplicates()

    # Intersection
    result = hh_with_both.merge(owed_hh, on="folio", how="inner").drop_duplicates()
    count = len(result)

    return pd.DataFrame({"households_count": [int(count)]})