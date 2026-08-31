import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]

    # Adults (18+)
    adults = df_portad[df_portad["edad"] >= 18][["folio", "ent"]].copy()

    # Households with reported total debts + interests
    crh = df_crh[["folio", "crh04_1", "crh04_2"]].copy()
    mask_reported = (crh["crh04_1"] == 1) & crh["crh04_2"].notna()
    avg_debt = crh.loc[mask_reported, "crh04_2"].mean()

    # Households above average debt
    high_debt_hh = crh.loc[mask_reported & (crh["crh04_2"] > avg_debt), ["folio"]].drop_duplicates()

    # Adults living in high-debt households
    adults_high_debt = adults.merge(high_debt_hh, on="folio", how="inner")

    # Count adults by state and return top 10
    result = (
        adults_high_debt.groupby("ent", dropna=False)
        .size()
        .reset_index(name="adult_count")
        .sort_values(["adult_count", "ent"], ascending=[False, True])
        .head(10)
        .reset_index(drop=True)
    )

    return result