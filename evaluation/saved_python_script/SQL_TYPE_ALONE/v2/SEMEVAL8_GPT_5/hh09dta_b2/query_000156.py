import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]

    # Households where at least one member owns a motor vehicle
    veh_folios = (
        df_ah.loc[df_ah["ah03d"] == 1.0, "folio"]
        .dropna()
        .drop_duplicates()
    )

    # Map household to state
    ent_per_folio = df_portad[["folio", "ent"]].drop_duplicates("folio")

    # Count vehicle-owning households per state
    veh_df = pd.DataFrame({"folio": veh_folios}).merge(ent_per_folio, on="folio", how="left")
    veh_df = veh_df.dropna(subset=["ent"])
    state_counts = veh_df.groupby("ent", as_index=False)["folio"].nunique().rename(columns={"folio": "veh_hh_count"})
    valid_states = state_counts.loc[state_counts["veh_hh_count"] >= 50, "ent"]

    # Households with positive amount received directly from Other Government Program
    pos_in = df_in[["folio", "in02a10"]].copy()
    pos_in = pos_in[pos_in["in02a10"] > 0]

    # Restrict to households that own a vehicle and belong to valid states
    target = (
        pos_in[pos_in["folio"].isin(veh_folios)]
        .merge(ent_per_folio, on="folio", how="left")
    )
    target = target[target["ent"].isin(valid_states)]

    # Compute average by state and sort descending
    result = (
        target.groupby("ent", as_index=False)["in02a10"]
        .mean()
        .rename(columns={"in02a10": "avg_in02a10"})
        .sort_values(by="avg_in02a10", ascending=False)
        .reset_index(drop=True)
    )

    return result