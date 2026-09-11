import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_crh = tables["ii_crh"]
    df_vlh = tables["ii_vlh"]
    df_ah = tables["ii_ah"]

    # Household size by counting individuals per household
    hh_size = df_portad.groupby("folio").size().rename("hh_size")
    avg_hh_size = hh_size.mean()

    # Households with at least one member who owns a motor vehicle
    owns_vehicle = (
        (df_ah["ah03d"] == 1.0)
        .groupby(df_ah["folio"])
        .any()
        .rename("owns_vehicle")
    )

    # Households reporting feeling very safe at home
    very_safe = (
        (df_vlh["vlh04"] == 1.0)
        .groupby(df_vlh["folio"])
        .any()
        .rename("very_safe")
    )

    # Total debt plus interest (pesos)
    debt = (
        df_crh.loc[(df_crh["crh04_1"] == 1.0) & (df_crh["crh04_2"].notna())]
        .groupby("folio")["crh04_2"]
        .mean()
        .rename("total_debt_plus_interest")
    )

    # Merge all conditions
    df = (
        hh_size.to_frame()
        .merge(owns_vehicle, on="folio", how="left")
        .merge(very_safe, on="folio", how="left")
        .merge(debt, on="folio", how="left")
    )

    # Apply filters
    cond = (
        (df["hh_size"] > avg_hh_size)
        & df["owns_vehicle"].fillna(False)
        & df["very_safe"].fillna(False)
    )

    avg_debt = df.loc[cond, "total_debt_plus_interest"].mean()

    return pd.DataFrame({"average_total_debt_plus_interest": [avg_debt]})