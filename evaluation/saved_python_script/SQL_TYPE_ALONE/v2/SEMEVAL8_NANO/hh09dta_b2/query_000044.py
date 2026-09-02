def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract relevant tables
    df_portad = tables["ii_portad"]
    df_se = tables["ii_se"]
    df_in = tables["ii_in"]
    df_su = tables["ii_su"]
    df_su_enriched = tables["ii_su_enriched"]
    df_portad_enriched = tables["ii_portad"]
    
    # Filter households where someone died in the last five years
    households_dead = df_se[df_se["se01a"] == 1]["folio"].unique()

    # Filter households with at least one person aged 65 or older
    households_age_65_plus = df_portad[df_portad["edad"] >= 65]["folio"].unique()

    # Filter households with at least one person under 18
    households_under_18 = df_portad[df_portad["edad"] < 18]["folio"].unique()

    # Find households that satisfy all three conditions
    households_final = set(households_dead) & set(households_age_65_plus) & set(households_under_18)

    # Count the number of such households
    count_households = len(households_final)

    return pd.DataFrame({"households_with_death_and_age": [count_households]})