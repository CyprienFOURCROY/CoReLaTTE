def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_inr = tables["ii_inr"]

    # 1. Compute number of adults (age 18+) per household
    adults = df_portad[df_portad["edad"] >= 18].groupby("folio").size().rename("n_adults")
    avg_adults = adults.mean()

    # 2. Households with more adults than the overall average
    folios_more_adults = adults[adults > avg_adults].index

    # 3. Members feel unsafe or very unsafe at home (vlh04 == 3 or 4)
    df_vlh_unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])]

    # 4. Have lived in current home since 2005 or earlier (vlh02_2 <= 2005)
    df_vlh_unsafe = df_vlh_unsafe[df_vlh_unsafe["vlh02_2"].notna()]
    df_vlh_unsafe = df_vlh_unsafe[df_vlh_unsafe["vlh02_2"] <= 2005]

    # 5. Restrict to households with more adults than average
    df_vlh_unsafe = df_vlh_unsafe[df_vlh_unsafe["folio"].isin(folios_more_adults)]

    # 6. Get unique household IDs matching all criteria
    folios_final = df_vlh_unsafe["folio"].unique()

    # 7. Of these, how many produced/sold canned goods in last 12 months? (inr02b == 1)
    df_inr_sel = df_inr[df_inr["folio"].isin(folios_final)]
    n_households = len(folios_final)
    n_canned_goods = df_inr_sel[df_inr_sel["inr02b"] == 1.0]["folio"].nunique()

    return __import__("pandas").DataFrame({
        "n_households": [n_households],
        "n_canned_goods_households": [n_canned_goods]
    })