import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()
    df_vlh = tables["ii_vlh"].copy()

    # Households in Oaxaca with at least one adult (18+)
    df_oax = df_portad[df_portad["ent"] == 20].copy()
    df_oax["is_adult"] = df_oax["edad"] >= 18
    adult_oax = (
        df_oax.groupby("folio", as_index=False)["is_adult"]
        .any()
        .rename(columns={"is_adult": "has_adult"})
    )
    adult_oax = adult_oax[adult_oax["has_adult"]]

    # Merge with income data (Other Government Program direct amount)
    df_income = adult_oax.merge(df_in[["folio", "in02a10"]], on="folio", how="left")

    # Filter households with positive direct amount
    df_pos = df_income[(df_income["in02a10"].notna()) & (df_income["in02a10"] > 0)].copy()

    # Compute average direct amount among such households (Oaxaca adult households with positive amount)
    avg_amount = df_pos["in02a10"].mean()

    # Merge with safety perception and filter very safe or safe at home
    df_safe = df_pos.merge(df_vlh[["folio", "vlh04"]], on="folio", how="left")
    mask_safe = df_safe["vlh04"].isin([1.0, 2.0])

    # Count households with amount above average and safe/very safe
    count = df_safe.loc[mask_safe & (df_safe["in02a10"] > avg_amount), "folio"].nunique()

    return pd.DataFrame({"households_count": [int(count)]})