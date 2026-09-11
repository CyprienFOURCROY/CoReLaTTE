import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    df_su = tables["ii_su"][["folio", "su01"]].copy()
    df_ah = tables["ii_ah"][["folio", "ah03d"]].copy()
    df_in = tables["ii_in"][["folio", "in02a10"]].copy()

    # Households with at least one member aged 60+
    df_portad["has60"] = (df_portad["edad"] >= 60).fillna(False)
    hh_age = (
        df_portad.groupby("folio", as_index=False)
        .agg(ent=("ent", "first"), has60=("has60", "max"))
    )
    hh_age = hh_age[hh_age["has60"]].dropna(subset=["ent"]).copy()
    hh_age["ent"] = hh_age["ent"].astype("int64")

    # Households that use land for farming
    su_use_land = df_su[df_su["su01"] == 1.0][["folio"]].drop_duplicates()

    # Households that own a motor vehicle
    ah_motor = df_ah[df_ah["ah03d"] == 1.0][["folio"]].drop_duplicates()

    # Merge filters
    eligible = (
        hh_age.merge(su_use_land, on="folio", how="inner")
        .merge(ah_motor, on="folio", how="inner")
        .merge(df_in, on="folio", how="left")
    )

    result = (
        eligible.groupby("ent", as_index=False)
        .agg(avg_amount=("in02a10", "mean"))
        .sort_values("avg_amount", ascending=True)
    )

    return result