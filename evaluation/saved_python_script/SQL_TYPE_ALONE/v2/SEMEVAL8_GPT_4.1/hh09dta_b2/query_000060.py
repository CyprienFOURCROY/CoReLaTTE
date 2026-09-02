def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_ah = tables["ii_ah"]

    # 1. Filter Oaxaca households (ent == 20)
    oaxaca_portad = df_portad[df_portad["ent"] == 20.0]

    # 2. Households that own/share a non-ag business (nna01 == 1)
    nna_yes = df_nna[df_nna["nna01"] == 1.0]

    # 3. Oaxaca households with non-ag business
    oaxaca_nna_yes = oaxaca_portad.merge(nna_yes[["folio"]], on="folio", how="inner")

    # 4. Get all adults (age >= 18) in these households
    adults = oaxaca_nna_yes[oaxaca_nna_yes["edad"] >= 18]

    # 5. Count adults per household
    adults_per_hh = adults.groupby("folio").size().reset_index(name="num_adults")

    # 6. For each household, determine if at least one member owns a domestic appliance (ah03g == 1)
    ah_domestic = df_ah[df_ah["folio"].isin(adults_per_hh["folio"])]
    owns_domestic = ah_domestic.groupby("folio")["ah03g"].apply(lambda x: (x == 1.0).any()).reset_index()
    owns_domestic["owns_domestic_appliance"] = np.where(owns_domestic["ah03g"], "Yes", "No")
    owns_domestic = owns_domestic[["folio", "owns_domestic_appliance"]]

    # 7. Merge adult counts with domestic appliance ownership
    adults_domestic = adults_per_hh.merge(owns_domestic, on="folio", how="left")

    # 8. Group by domestic appliance ownership, calculate average adults and household count
    result = adults_domestic.groupby("owns_domestic_appliance").agg(
        average_num_adults=("num_adults", "mean"),
        num_households=("folio", "nunique")
    ).reset_index()

    return result