def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np

    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_vlh = tables["ii_vlh"]

    # Adults 18+ in Oaxaca (ent==20), merge with su01==1 (use plot/land for cultivation)
    df_adults_oax = df_portad[
        (df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18)
    ][["folio", "ls"]]

    # Households that use a plot/land for cultivation (su01==1)
    df_su_plot = df_su[df_su["su01"] == 1.0][["folio"]].drop_duplicates()

    # Merge to get adults in Oaxaca in households that use a plot/land
    df_adults_oax_plot = df_adults_oax.merge(df_su_plot, on="folio", how="inner")

    # Merge with ii_vlh to get "Feel safe at home?" (vlh04)
    # Since ii_vlh is at household level, merge on folio
    df_merged = df_adults_oax_plot.merge(
        df_vlh[["folio", "vlh04"]], on="folio", how="left"
    )

    # Valid answers: vlh04 in [1,2,3,4]
    valid_mask = df_merged["vlh04"].isin([1.0, 2.0, 3.0, 4.0])
    n_valid = valid_mask.sum()

    # Unsafe or Very unsafe: vlh04 in [3,4]
    n_unsafe = df_merged.loc[valid_mask, "vlh04"].isin([3.0, 4.0]).sum()

    return pd.DataFrame({
        "n_valid_answers": [int(n_valid)],
        "n_unsafe_or_very_unsafe": [int(n_unsafe)]
    })