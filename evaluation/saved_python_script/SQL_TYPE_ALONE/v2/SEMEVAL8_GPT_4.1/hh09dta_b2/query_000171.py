def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_vlh = tables["ii_vlh"]

    # 1. Households with at least one adult (age >= 18)
    df_adult = df_portad[df_portad["edad"] >= 18].copy()
    # Get unique household IDs with at least one adult
    hh_with_adult = set(df_adult["folio"].unique())

    # 2. Households with a member who owns/shares a non-ag business (nna01 == 1)
    df_nna_yes = df_nna[df_nna["nna01"] == 1].copy()
    hh_with_nonag = set(df_nna_yes["folio"].unique())

    # 3. Households that answered the "Feel safe at home" question (vlh04 notna)
    df_vlh_valid = df_vlh[df_vlh["vlh04"].notna()].copy()
    hh_with_vlh04 = set(df_vlh_valid["folio"].unique())

    # 4. Intersection: households that meet all three criteria
    qualifying_hh = hh_with_adult & hh_with_nonag & hh_with_vlh04

    # 5. For these households, get state and year moved in
    # Merge to get state
    df_qual = df_portad[df_portad["folio"].isin(qualifying_hh)][["folio", "ent"]].drop_duplicates("folio")
    # Merge with vlh for year moved in
    df_qual = df_qual.merge(df_vlh[["folio", "vlh02_2"]], on="folio", how="left")

    # 6. For each state, count number of qualifying households and those who moved in since 2005 or later
    df_qual["since_2005"] = df_qual["vlh02_2"].apply(lambda x: 1 if pd.notna(x) and x >= 2005 else 0)

    # Only keep states with at least 30 such households
    state_counts = df_qual.groupby("ent").agg(
        total_households=("folio", "count"),
        post_2005_households=("since_2005", "sum")
    ).reset_index()

    state_counts = state_counts[state_counts["total_households"] >= 30]

    # Compute average post_2005_households across qualifying states
    avg_post_2005 = state_counts["post_2005_households"].mean()

    # Only keep states whose post_2005 count is at or above the average
    result = state_counts[state_counts["post_2005_households"] >= avg_post_2005].copy()

    # Order by post_2005_households descending
    result = result.sort_values("post_2005_households", ascending=False).reset_index(drop=True)

    # Rename columns for clarity
    result = result.rename(columns={
        "ent": "state",
        "total_households": "total_households",
        "post_2005_households": "post_2005_households"
    })

    return result[["state", "total_households", "post_2005_households"]]