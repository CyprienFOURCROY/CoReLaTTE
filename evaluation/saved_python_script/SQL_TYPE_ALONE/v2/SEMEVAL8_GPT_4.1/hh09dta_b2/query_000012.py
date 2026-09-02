def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_crh = tables["ii_crh"]

    # 1. Households that use a plot/land for sowing/farming/vegetables (su01 == 1)
    df_su_plot = df_su[df_su["su01"] == 1]

    # 2. Merge with crh to get total debts + interests (crh04_2)
    df_merged = df_su_plot.merge(df_crh[["folio", "crh04_2"]], on="folio", how="inner")

    # 3. Keep only those with positive total debt (crh04_2 > 0)
    df_merged = df_merged[df_merged["crh04_2"].notna() & (df_merged["crh04_2"] > 0)]

    # 4. Merge with portad to get state and household size
    # Household size: count of unique 'ls' per 'folio'
    hh_size = df_portad.groupby("folio")["ls"].nunique().reset_index().rename(columns={"ls": "hh_size"})
    df_merged = df_merged.merge(df_portad[["folio", "ent"]].drop_duplicates(), on="folio", how="left")
    df_merged = df_merged.merge(hh_size, on="folio", how="left")

    # 5. Group by state (ent)
    result = (
        df_merged.groupby("ent")
        .agg(
            avg_total_debt=("crh04_2", "mean"),
            avg_hh_size=("hh_size", "mean"),
            n_households=("folio", "nunique"),
        )
        .reset_index()
    )

    # 6. Rank by average total debt descending
    result = result.sort_values("avg_total_debt", ascending=False).reset_index(drop=True)

    # 7. Rename 'ent' to 'state'
    result = result.rename(columns={"ent": "state"})

    return result