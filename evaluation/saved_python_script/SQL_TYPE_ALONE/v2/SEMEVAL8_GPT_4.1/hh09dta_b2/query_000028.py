def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_se = tables["ii_se"]
    df_nna = tables["ii_nna"]

    # 1. Adults (18+)
    df_adults = df_portad[df_portad["edad"] >= 18].copy()

    # 2. Age above overall average (of all individuals)
    overall_avg_age = df_portad["edad"].mean()
    df_adults = df_adults[df_adults["edad"] > overall_avg_age]

    # 3. Households that use land for farming (su01 == 1)
    df_su_land = df_su[df_su["su01"] == 1][["folio"]]

    # 4. Households that experienced total crop loss in last 5 years (se01e == 1)
    df_se_crop_loss = df_se[df_se["se01e"] == 1][["folio"]]

    # 5. Households that have a non-agricultural business (nna01 == 1)
    df_nna_biz = df_nna[df_nna["nna01"] == 1][["folio"]]

    # 6. Merge all household-level filters
    eligible_folios = set(df_su_land["folio"]) & set(df_se_crop_loss["folio"]) & set(df_nna_biz["folio"])

    # 7. Filter adults by eligible households
    df_adults = df_adults[df_adults["folio"].isin(eligible_folios)].copy()

    # 8. For average household expense on seeds, need su234 from ii_su (expense in seeds)
    # Merge adults with su234 by folio
    df_adults = df_adults.merge(df_su[["folio", "su234"]], on="folio", how="left")

    # 9. Group by state (ent), count individuals, and average su234 (household expense on seeds)
    result = (
        df_adults.groupby("ent")
        .agg(
            num_individuals=("folio", "count"),
            avg_household_expense_on_seeds=("su234", "mean")
        )
        .reset_index()
        .rename(columns={"ent": "state"})
    )

    return result