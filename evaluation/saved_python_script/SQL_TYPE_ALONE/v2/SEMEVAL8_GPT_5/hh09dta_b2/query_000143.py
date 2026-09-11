import pandas as pd
import numpy as np

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_vlh = tables["ii_vlh"].copy()
    df_ah = tables["ii_ah"].copy()

    # Adults (18+) in Oaxaca (ent == 20)
    adults_oax = df_portad[
        (df_portad["ent"] == 20.0) &
        (pd.to_numeric(df_portad["edad"], errors="coerce") >= 18)
    ][["folio", "edad"]].copy()

    # Household safety: very safe or safe
    df_vlh_use = df_vlh[["folio", "vlh04", "vlh12a_a", "vlh12a_b", "vlh14a", "vlh16a", "vlh18a"]].copy()
    df_vlh_use["safe"] = df_vlh_use["vlh04"].isin([1.0, 2.0])

    # Forced entry/robbery since 2005 (any of house/business/parcel indicators or total > 0)
    cond12 = (df_vlh_use["vlh12a_a"] == 1.0) | (df_vlh_use["vlh12a_b"] == 2.0)
    cond14 = (df_vlh_use["vlh14a"] == 1.0)
    cond16 = (df_vlh_use["vlh16a"] == 1.0)
    cond18 = pd.to_numeric(df_vlh_use["vlh18a"], errors="coerce").fillna(0) > 0
    df_vlh_use["since2005"] = (cond12 | cond14 | cond16 | cond18).fillna(False)

    df_vlh_use = df_vlh_use[["folio", "safe", "since2005"]]

    # Household has at least one member who owns a motor vehicle (ah03d == 1)
    df_ah_motor = df_ah[["folio", "ah03d"]].copy()
    df_ah_motor["has_motor"] = (df_ah_motor["ah03d"] == 1.0)
    df_ah_motor = df_ah_motor.groupby("folio", as_index=False)["has_motor"].max()

    # Merge individual adults with household conditions
    merged = adults_oax.merge(df_vlh_use, on="folio", how="left").merge(df_ah_motor, on="folio", how="left")

    merged["safe"] = merged["safe"].fillna(False)
    merged["has_motor"] = merged["has_motor"].fillna(False)
    base_group = merged[(merged["safe"]) & (merged["has_motor"])].copy()

    # Compute group's average age
    avg_age = base_group["edad"].mean()

    # Count individuals older than group's average age and in households with forced entry/robbery since 2005
    count = int(base_group[(base_group["edad"] > avg_age) & (base_group["since2005"].fillna(False))].shape[0])

    return pd.DataFrame({"count": [count]})