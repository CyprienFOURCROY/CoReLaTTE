def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]

    # Step 1: Filter df_in for households that participated and received income from Other Government Program
    # in01a10_1 == 1
    df_in_filtered = df_in[df_in["in01a10_1"] == 1]

    # Step 2: Merge with df_portad to get age, state, ls
    df_merged = df_in_filtered.merge(df_portad, on="folio", how="inner")

    # Step 3: Filter for age 30-50 (inclusive), and ls in ["01", "02"]
    # ls in df_portad is object, but in df_ah it's float32, so we need to be careful
    # In df_portad, ls is object, so compare as string
    df_merged = df_merged[
        (df_merged["edad"] >= 30) &
        (df_merged["edad"] <= 50) &
        (df_merged["ls"].isin(["01", "02"]))
    ]

    # Step 4: Merge with df_ah to get ah04f_2 (value of washing machine/stove)
    # In df_ah, ls is float32, in df_merged it's object, so cast both to string for merge
    df_merged = df_merged.merge(
        df_ah[["folio", "ls", "ah04f_2"]],
        left_on=["folio", "ls"],
        right_on=["folio", df_ah["ls"].astype(str)],
        how="inner"
    )

    # Step 5: Remove rows where ah04f_2 is missing or not positive
    df_merged = df_merged[df_merged["ah04f_2"].notna() & (df_merged["ah04f_2"] > 0)]

    # Step 6: Group by state (ent), calculate mean ah04f_2 per state
    state_means = df_merged.groupby("ent")["ah04f_2"].mean()

    # Step 7: Calculate overall mean across all states
    overall_mean = state_means.mean()

    # Step 8: Filter states with mean above overall mean
    state_means_above = state_means[state_means > overall_mean]

    # Step 9: Sort descending by mean
    state_means_above = state_means_above.sort_values(ascending=False)

    # Step 10: Prepare output DataFrame
    result = state_means_above.reset_index()
    result.columns = ["state", "avg_ah04f_2"]

    return result