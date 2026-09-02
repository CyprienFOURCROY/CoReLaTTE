def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]

    # Only households that use a plot/land for sowing/farming (su01 == 1)
    df_su_plot = df_su[df_su["su01"] == 1]

    # Merge with portad to get state info
    df_merged = df_su_plot.merge(df_portad[["folio", "ent"]], on="folio", how="left")

    # Only consider rows with a valid expense on seeds (su234)
    df_merged = df_merged[~df_merged["su234"].isna()]

    # Compute overall average expense on seeds
    overall_avg = df_merged["su234"].mean()

    # Group by state and compute average expense on seeds
    state_avg = (
        df_merged.groupby("ent")["su234"]
        .mean()
        .reset_index()
        .rename(columns={"su234": "avg_expense_on_seeds"})
    )

    # Filter: average > 1000 and >= overall average
    state_avg = state_avg[
        (state_avg["avg_expense_on_seeds"] > 1000) &
        (state_avg["avg_expense_on_seeds"] >= overall_avg)
    ]

    # Rank by average expense, highest to lowest
    state_avg = state_avg.sort_values("avg_expense_on_seeds", ascending=False).reset_index(drop=True)

    return state_avg