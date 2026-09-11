def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_inr = tables["ii_inr"]

    # 1. Households with a value for total debts + interests (crh04_2 not null)
    crh_debt = df_crh[df_crh["crh04_2"].notnull()].copy()

    # 2. For these households, get the oldest interviewed member's age
    # Merge with portad to get age and household id
    merged = crh_debt.merge(df_portad[["folio", "edad"]], on="folio", how="left")
    # Group by household, get oldest age
    oldest_age = merged.groupby("folio")["edad"].max().reset_index()
    oldest_age = oldest_age.rename(columns={"edad": "oldest_age"})

    # 3. Compute average of oldest ages across these households
    avg_oldest_age = oldest_age["oldest_age"].mean()

    # 4. Mark households where oldest age >= average
    oldest_age["at_least_avg"] = oldest_age["oldest_age"] >= avg_oldest_age

    # 5. For these households, get whether they produced/sold dairy in last 12 months (inr02a: 1=Yes, 3=No)
    # Use only one row per household from inr (any, since inr02a is per household)
    dairy = df_inr[["folio", "inr02a"]].drop_duplicates("folio")
    # Merge with oldest_age
    result = oldest_age.merge(dairy, on="folio", how="left")

    # 6. Only keep households with at_least_avg == True
    result = result[result["at_least_avg"]]

    # 7. Map inr02a to Yes/No
    result["dairy_produced"] = result["inr02a"].map({1.0: "Yes", 3.0: "No"})
    # If inr02a is missing, treat as No (or could drop, but question says Yes vs No)
    result["dairy_produced"] = result["dairy_produced"].fillna("No")

    # 8. Count households by dairy_produced
    counts = result.groupby("dairy_produced").size().reset_index(name="num_households")

    return counts