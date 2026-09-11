def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]

    # Step 1: Find households that reported owing money on credit/loans in last 12 months
    # crh02_1 == 1 means "Value" (i.e., they incurred debts)
    df_crh_debt = df_crh[df_crh["crh02_1"] == 1.0][["folio"]].drop_duplicates()

    # Step 2: For those households, check if they have at least one adult (edad >= 18) and at least one child (edad < 18)
    df_portad_debt = df_portad.merge(df_crh_debt, on="folio", how="inner")

    # Group by household and check for at least one adult and one child
    def has_adult_and_child(group):
        has_adult = (group["edad"] >= 18).any()
        has_child = (group["edad"] < 18).any()
        return has_adult and has_child

    grouped = df_portad_debt.groupby("folio").apply(has_adult_and_child)
    count = grouped.sum()

    return pd.DataFrame({"households_with_adult_and_child": [int(count)]})