def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_vlh = tables["ii_vlh"]

    # States: Oaxaca (20), Puebla (21)
    states = [20.0, 21.0]

    # Filter portad: age >= 25, state in [20, 21]
    dfp = df_portad[
        (df_portad["edad"] >= 25) &
        (df_portad["ent"].isin(states))
    ][["folio", "ent", "edad"]]

    # Filter crh: crh04_1 == 1 (Value), crh04_2 >= 5000 (not null)
    dfc = df_crh[
        (df_crh["crh04_1"] == 1.0) &
        (df_crh["crh04_2"].notnull()) &
        (df_crh["crh04_2"] >= 5000)
    ][["folio", "crh04_2"]]

    # Merge on folio
    dfm = dfp.merge(dfc, on="folio", how="inner")

    # Merge with vlh for 'feel safe at home'
    dfm = dfm.merge(
        df_vlh[["folio", "vlh04"]],
        on="folio",
        how="inner"
    )

    # Only keep rows with non-null vlh04
    dfm = dfm[dfm["vlh04"].notnull()]

    # Group by state
    result = (
        dfm.groupby("ent")
        .agg(
            avg_feel_safe_at_home=("vlh04", "mean"),
            avg_total_debt=("crh04_2", "mean"),
            n_households=("folio", "nunique")
        )
        .reset_index()
    )

    # Map state codes to names
    state_map = {20.0: "Oaxaca", 21.0: "Puebla"}
    result["state"] = result["ent"].map(state_map)

    # Reorder columns
    result = result[["state", "avg_feel_safe_at_home", "avg_total_debt", "n_households"]]

    # Sort by avg_feel_safe_at_home ascending (safest to least safe)
    result = result.sort_values("avg_feel_safe_at_home", ascending=True).reset_index(drop=True)

    return result