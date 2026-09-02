import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_ah = tables["ii_ah"]

    # Households in Oaxaca (ent==20) with at least one member aged 18+
    adult_ox = df_portad.loc[
        (df_portad["ent"] == 20.0) & (df_portad["edad"] >= 18),
        "folio"
    ].dropna().unique()

    # Households that use a plot of land for cultivation
    land_use = df_su.loc[df_su["su01"] == 1.0, "folio"].dropna().unique()

    # Households where individual ID 1 reports ownership of a motor vehicle
    motor_vehicle_ls1 = df_ah.loc[
        (df_ah["ls"] == 1.0) & (df_ah["ah03d"] == 1.0),
        "folio"
    ].dropna().unique()

    # Intersection of all conditions
    result_folios = sorted(list(set(adult_ox).intersection(land_use).intersection(motor_vehicle_ls1)))

    return pd.DataFrame({"folio": result_folios})