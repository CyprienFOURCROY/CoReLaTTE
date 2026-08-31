import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_ah = tables["ii_ah"]
    df_nna = tables["ii_nna"]

    # Oaxaca households (state code 20)
    oax_folios = df_portad.loc[df_portad["ent"] == 20.0, ["folio"]].drop_duplicates()

    # Highest-valued domestic appliance per household (only where value is reported as Yes)
    dom_vals = (
        df_ah.loc[df_ah["ah04g_1"] == 1.0, ["folio", "ah04g_2"]]
        .groupby("folio", as_index=False)["ah04g_2"]
        .max()
        .rename(columns={"ah04g_2": "max_domestic_appliance_value"})
    )

    # Merge with business ownership and Oaxaca filter
    oax = (
        oax_folios.merge(df_nna[["folio", "nna01"]], on="folio", how="left")
        .merge(dom_vals, on="folio", how="left")
    )

    # Average highest-valued domestic appliance among Oaxaca households WITHOUT a non-ag business
    mask_no_bus = (oax["nna01"] == 2.0) & (oax["max_domestic_appliance_value"].notna())
    avg_no_bus = oax.loc[mask_no_bus, "max_domestic_appliance_value"].mean()

    # Households WITH a non-ag business whose value exceeds that average
    if pd.isna(avg_no_bus):
        result = pd.DataFrame(columns=["folio", "max_domestic_appliance_value"])
    else:
        mask_with_bus = (oax["nna01"] == 1.0) & (oax["max_domestic_appliance_value"] > avg_no_bus)
        result = oax.loc[mask_with_bus, ["folio", "max_domestic_appliance_value"]].copy()

    result = result.sort_values("max_domestic_appliance_value", ascending=False).reset_index(drop=True)
    return result