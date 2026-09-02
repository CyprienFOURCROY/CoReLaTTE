def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_nna = tables["ii_nna"]

    # 1. Households that use a plot/land for farming (su01 == 1)
    df_su_farm = df_su[df_su["su01"] == 1][["folio"]].drop_duplicates()

    # 2. Members aged 18–24
    df_portad_18_24 = df_portad[(df_portad["edad"] >= 18) & (df_portad["edad"] <= 24)][["folio"]].drop_duplicates()

    # 3. Compute average household age for each household
    df_portad_age = df_portad[["folio", "edad"]].copy()
    df_hh_avg_age = df_portad_age.groupby("folio", as_index=False)["edad"].mean().rename(columns={"edad": "avg_hh_age"})

    # 4. Compute overall average household age (across all households)
    overall_avg_age = df_hh_avg_age["avg_hh_age"].mean()

    # 5. Households with avg age >= overall average
    df_hh_avg_age_ge = df_hh_avg_age[df_hh_avg_age["avg_hh_age"] >= overall_avg_age][["folio"]]

    # 6. Households that own/share non-ag business (nna01 == 1 for any member)
    df_nna_business = df_nna[df_nna["nna01"] == 1][["folio"]].drop_duplicates()

    # 7. Merge all filters: farming, at least one 18–24, avg age >= overall
    df_selected = (
        df_su_farm
        .merge(df_portad_18_24, on="folio")
        .merge(df_hh_avg_age_ge, on="folio")
    )

    # 8. Add state info
    df_selected = df_selected.merge(df_portad[["folio", "ent"]].drop_duplicates(), on="folio", how="left")

    # 9. For each state, count households matching criteria
    df_selected_state = df_selected.groupby("ent").agg(
        households=("folio", "nunique")
    ).reset_index()

    # 10. For each state, count households with non-ag business
    df_selected_with_business = df_selected.merge(df_nna_business, on="folio", how="inner")
    df_selected_state_business = df_selected_with_business.groupby("ent").agg(
        households_with_nonag_business=("folio", "nunique")
    ).reset_index()

    # 11. Merge results
    result = df_selected_state.merge(df_selected_state_business, on="ent", how="left")
    result["households_with_nonag_business"] = result["households_with_nonag_business"].fillna(0).astype(int)

    # 12. Rename ent to state for clarity
    result = result.rename(columns={"ent": "state"})

    # 13. Sort by state
    result = result.sort_values("state").reset_index(drop=True)

    return result[["state", "households", "households_with_nonag_business"]]