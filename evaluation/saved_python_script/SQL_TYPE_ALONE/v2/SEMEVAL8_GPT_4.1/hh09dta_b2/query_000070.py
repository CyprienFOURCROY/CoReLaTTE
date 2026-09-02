def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    df_ah = tables["ii_ah"]
    df_portad = tables["ii_portad"]

    # Filter households with a positive value for electronic device(s)
    mask = (df_ah["ah04e_2"].notna()) & (df_ah["ah04e_2"] > 0)
    hh_with_electronics = df_ah.loc[mask, "folio"].unique()

    # Count household members per household
    hh_member_counts = df_portad.groupby("folio").size().reset_index(name="num_members")

    # Filter to only those households with positive electronic device value
    filtered_counts = hh_member_counts[hh_member_counts["folio"].isin(hh_with_electronics)]

    # Compute average number of household members
    avg_members = filtered_counts["num_members"].mean() if not filtered_counts.empty else float("nan")

    return pd.DataFrame({"average_num_household_members": [avg_members]})