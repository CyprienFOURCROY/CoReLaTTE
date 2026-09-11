def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_su = tables["ii_su"]

    # Households that use land for farming (su01 == 1)
    su_land = df_su[df_su["su01"] == 1][["folio"]].drop_duplicates()

    # Households that produced/sold honey in last 12 months (inr02i == 1)
    inr_honey = df_inr[df_inr["inr02i"] == 1][["folio"]].drop_duplicates()

    # Intersection: households that use land for farming AND produced/sold honey
    land_honey_folios = pd.merge(su_land, inr_honey, on="folio")

    # Get all individuals in these households
    portad_land_honey = pd.merge(df_portad, land_honey_folios, on="folio")

    # Remove missing ages
    portad_land_honey = portad_land_honey[portad_land_honey["edad"].notnull()]

    # Compute overall average age
    overall_avg_age = portad_land_honey["edad"].mean()

    # Compute average age per state
    avg_age_by_state = (
        portad_land_honey.groupby("ent")["edad"]
        .mean()
        .reset_index()
        .rename(columns={"edad": "average_age"})
    )

    # Filter states with average age > overall average
    result = avg_age_by_state[avg_age_by_state["average_age"] > overall_avg_age]

    # Sort from highest to lowest average age
    result = result.sort_values("average_age", ascending=False).reset_index(drop=True)

    return result