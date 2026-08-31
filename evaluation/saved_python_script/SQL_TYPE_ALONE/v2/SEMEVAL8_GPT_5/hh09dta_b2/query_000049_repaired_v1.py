import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_vlh = tables["ii_vlh"]

    # Households with at least one member younger than 30 and their state
    hh_age_state = (
        df_portad.groupby("folio", as_index=False)
        .agg(ent=("ent", "first"), min_edad=("edad", "min"))
    )
    young_hh = hh_age_state.loc[hh_age_state["min_edad"] < 30, ["folio", "ent"]]

    # Households that own/share a non-ag business
    nna_yes = df_nna.loc[df_nna["nna01"] == 1.0, ["folio"]]

    # Households reporting zero robbery/break-in incidents since 2005
    vlh_zero = df_vlh.loc[df_vlh["vlh18a"] == 0.0, ["folio"]]

    # Intersection of conditions
    eligible = young_hh.merge(nna_yes, on="folio", how="inner").merge(vlh_zero, on="folio", how="inner")

    # Count households by state and sort
    result = (
        eligible.groupby("ent", dropna=False)
        .agg(households=("folio", "nunique"))
        .reset_index()
        .sort_values(["households", "ent"], ascending=[False, True])
        .reset_index(drop=True)
    )

    return result