def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]

    # Households with positive direct amount from '70 y más'
    df_in_70ymas = df_in[df_in["in02a11"].notna() & (df_in["in02a11"] > 0)]
    folios_70ymas = df_in_70ymas["folio"].unique()

    # Get state and age info for these households
    df_portad_70ymas = df_portad[df_portad["folio"].isin(folios_70ymas)][["folio", "ent", "edad"]]

    # For each household, check if any member is aged 70 or older
    df_portad_70ymas["is_70_or_older"] = df_portad_70ymas["edad"] >= 70

    # Group by folio to get household-level info
    hh_70ymas = df_portad_70ymas.groupby(["folio", "ent"]).agg(
        has_70_or_older=("is_70_or_older", "any")
    ).reset_index()

    # Now, by state, count households with and without members aged 70+
    result = hh_70ymas.groupby("ent").agg(
        households_with_70_or_older=("has_70_or_older", lambda x: np.sum(x)),
        households_without_70_or_older=("has_70_or_older", lambda x: np.sum(~x))
    ).reset_index().rename(columns={"ent": "state"})

    return result