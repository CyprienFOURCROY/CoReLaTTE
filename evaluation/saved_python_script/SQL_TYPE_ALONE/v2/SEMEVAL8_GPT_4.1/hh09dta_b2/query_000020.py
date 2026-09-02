def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_inr = tables["ii_inr"]

    # Households that produced/sold eggs in last 12 months: inr02d == 1
    df_eggs = df_inr[df_inr["inr02d"] == 1][["folio"]].drop_duplicates()

    # Households that own/share non-ag business: nna01 == 1
    df_nonag = df_nna[df_nna["nna01"] == 1][["folio"]].drop_duplicates()

    # Intersection: households that satisfy both
    df_both = pd.merge(df_eggs, df_nonag, on="folio", how="inner")

    # For household size, count number of individuals per household in ii_portad
    df_hhsize = df_portad.groupby("folio").size().reset_index(name="hh_size")

    # Get state for each household (take first 'ent' per household)
    df_state = df_portad.groupby("folio")["ent"].first().reset_index()

    # Merge with both filters
    df_both = df_both.merge(df_hhsize, on="folio", how="left").merge(df_state, on="folio", how="left")

    # Group by state and household size, count households
    df_grouped = df_both.groupby(["ent", "hh_size"]).size().reset_index(name="num_households")

    # Find the row with the highest number of households
    idxmax = df_grouped["num_households"].idxmax()
    result = df_grouped.loc[[idxmax]].reset_index(drop=True)

    # Rename columns for clarity
    result = result.rename(columns={"ent": "state", "hh_size": "household_size"})

    return result