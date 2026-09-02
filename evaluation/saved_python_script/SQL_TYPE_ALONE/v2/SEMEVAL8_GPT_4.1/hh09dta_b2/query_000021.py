def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]

    # Merge to get state info per household
    df = pd.merge(df_vlh, df_portad[["folio", "ent"]], on="folio", how="left")

    # Only keep rows with valid state
    df = df[df["ent"].notna()]

    # Count total households per state
    total_households = df.groupby("ent")["folio"].nunique().reset_index()
    total_households = total_households.rename(columns={"folio": "total_households"})

    # Households that reported knowing a family/friend robbed in last 12 months (vlh10a == 1)
    robbed = df[df["vlh10a"] == 1]
    robbed_households = robbed.groupby("ent")["folio"].nunique().reset_index()
    robbed_households = robbed_households.rename(columns={"folio": "households_knowing_robbery"})

    # Merge counts
    result = pd.merge(total_households, robbed_households, on="ent", how="left")
    result["households_knowing_robbery"] = result["households_knowing_robbery"].fillna(0).astype(int)

    # Only states with at least 100 surveyed households
    result = result[result["total_households"] >= 100]

    # Sort by households_knowing_robbery descending
    result = result.sort_values(by="households_knowing_robbery", ascending=False).reset_index(drop=True)

    # Convert ent to int for clarity
    result["ent"] = result["ent"].astype(int)

    return result[["ent", "households_knowing_robbery", "total_households"]]