def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_crh = tables["ii_crh"]

    # Households with no savings: crh01_1a == 1
    df_crh_nosavings = df_crh[df_crh["crh01_1a"] == 1.0][["folio"]]

    # Households not using a plot/land for farming: su01 == 3
    df_su_noland = df_su[df_su["su01"] == 3.0][["folio"]]

    # Intersection: households with both conditions
    folios_nosavings_noland = pd.merge(df_crh_nosavings, df_su_noland, on="folio")["folio"].unique()

    # Get state for these households
    df_portad_sel = df_portad[df_portad["folio"].isin(folios_nosavings_noland)][["folio", "ent"]]

    # Count households per state
    state_counts = df_portad_sel.groupby("ent")["folio"].nunique().reset_index()
    state_counts = state_counts.rename(columns={"ent": "state", "folio": "num_households"})

    # Filter states with at least 50 households
    state_counts = state_counts[state_counts["num_households"] >= 50]

    # Order from highest to lowest
    state_counts = state_counts.sort_values("num_households", ascending=False).reset_index(drop=True)

    return state_counts