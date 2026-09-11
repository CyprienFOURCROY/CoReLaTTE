import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent", "edad"]].copy()
    # Aggregate to household level: state and max age among interviewed in household
    hh_demo = (
        df_portad.groupby("folio", as_index=False)
        .agg(ent=("ent", "first"), max_age=("edad", "max"))
    )
    # Households in Oaxaca (ent==20) with at least one adult (18+)
    hh_oax_adult = hh_demo[(hh_demo["ent"] == 20.0) & (hh_demo["max_age"] >= 18.0)][["folio"]]

    # Liconsa milk received in last 12 months
    df_in = tables["ii_in"][["folio", "in03a"]].copy()
    hh_liconsa = df_in[df_in["in03a"] == 1.0][["folio"]].drop_duplicates()

    # Target households: Oaxaca + adult + received Liconsa
    target_hh = hh_oax_adult.merge(hh_liconsa, on="folio", how="inner")

    # Ownership of motor vehicle by any member in the household
    df_ah = tables["ii_ah"][["folio", "ah03d"]].copy()
    df_ah["veh"] = df_ah["ah03d"] == 1.0
    hh_vehicle = df_ah.groupby("folio", as_index=False)["veh"].any()

    target = target_hh.merge(hh_vehicle, on="folio", how="left")
    target["veh"] = target["veh"].fillna(False)

    counts = target["veh"].value_counts().to_dict()
    yes = int(counts.get(True, 0))
    no = int(counts.get(False, 0))

    return pd.DataFrame({"owns_motor_vehicle": ["Yes", "No"], "households": [yes, no]})