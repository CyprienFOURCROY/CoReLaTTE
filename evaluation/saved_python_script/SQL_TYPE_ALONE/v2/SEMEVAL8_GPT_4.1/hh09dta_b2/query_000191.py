def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_nna = tables["ii_nna"]

    # 1. Households that feel very safe or safe at home (vlh04 == 1 or 2)
    # 2. Have a member who owns or shares a non-ag business (nna01 == 1)
    # 3. Consider only states with at least 50 such households
    # 4. For these, get average vlh18a (number of break-ins/robberies since 2005)
    # 5. Only states with average above national average for this group
    # 6. Output: state code, average, count, ordered by average desc

    # Merge portad and nna on folio to get state and business ownership
    df_nna_filt = df_nna[df_nna["nna01"] == 1]
    # Only keep one row per household (folio) for nna
    df_nna_filt = df_nna_filt.drop_duplicates(subset=["folio"])

    # Merge with vlh to get safety and break-in info
    df = pd.merge(df_nna_filt[["folio"]], df_vlh[["folio", "vlh04", "vlh18a"]], on="folio", how="inner")
    # Keep only those who feel very safe or safe at home
    df = df[df["vlh04"].isin([1, 2])]

    # Merge with portad to get state
    df = pd.merge(df, df_portad[["folio", "ent"]], on="folio", how="inner")

    # Only one row per household (folio)
    df = df.drop_duplicates(subset=["folio"])

    # Only keep states with at least 50 such households
    state_counts = df.groupby("ent")["folio"].nunique()
    valid_states = state_counts[state_counts >= 50].index

    df = df[df["ent"].isin(valid_states)]

    # Compute national average (for this group)
    national_avg = df["vlh18a"].mean()

    # Compute state averages and counts
    result = (
        df.groupby("ent")
        .agg(
            avg_vlh18a=("vlh18a", "mean"),
            household_count=("folio", "nunique")
        )
        .reset_index()
    )

    # Only states with average above national average
    result = result[result["avg_vlh18a"] > national_avg]

    # Order from highest to lowest average
    result = result.sort_values(by="avg_vlh18a", ascending=False).reset_index(drop=True)

    return result