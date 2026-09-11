import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"][["folio", "ent"]].copy()
    df_su = tables["ii_su"][["folio", "su01", "su231"]].copy()

    # Compute average chemical fertilizer expense among all land-using households
    mask_land_all = (df_su["su01"] == 1.0) & (df_su["su231"].notna())
    avg_expense = df_su.loc[mask_land_all, "su231"].mean()

    # Oaxaca households (ent == 20)
    df_portad = df_portad[df_portad["ent"].notna()]
    oaxaca_folios = df_portad.loc[df_portad["ent"] == 20.0, "folio"].dropna().drop_duplicates()

    # Filter Oaxaca households that use land and have expense above average
    df_oax = df_su[df_su["folio"].isin(oaxaca_folios)].copy()
    mask_oax = (df_oax["su01"] == 1.0) & (df_oax["su231"].notna()) & (df_oax["su231"] > avg_expense)
    result = df_oax.loc[mask_oax, ["folio", "su231"]].drop_duplicates(subset=["folio"])

    result = result.sort_values(by="su231", ascending=False).reset_index(drop=True)
    return result