def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import numpy as np
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_ah = tables["ii_ah"]

    # 1. Filter Oaxaca households with interviewee aged 30–60
    oaxaca_portad = df_portad[
        (df_portad["ent"] == 20.0) &
        (df_portad["edad"] >= 30) &
        (df_portad["edad"] <= 60)
    ][["folio"]]

    # 2. Households that received a positive amount from Other Government Program
    # in01a10_2: amount received, in01a10_1: participation
    df_in_ogp = df_in[
        (df_in["folio"].isin(oaxaca_portad["folio"])) &
        (df_in["in01a10_2"].notnull()) &
        (df_in["in01a10_2"] > 0)
    ][["folio", "in01a10_2"]]

    # 3. Join with ah table for individual 2 (ls == 2)
    df_ah2 = df_ah[
        (df_ah["ls"] == 2.0)
    ][["folio", "ah04e_2"]]

    # 4. Merge to get only relevant households
    merged = (
        df_in_ogp
        .merge(df_ah2, on="folio", how="inner")
    )

    # 5. Compute Oaxaca average for this group (electronic device value, ah04e_2)
    oaxaca_avg = merged["ah04e_2"].mean()

    # 6. Filter to those whose value exceeds the Oaxaca average
    filtered = merged[merged["ah04e_2"] > oaxaca_avg]

    # 7. Top 10 households by electronic device value (ah04e_2)
    top10 = filtered.sort_values("ah04e_2", ascending=False).head(10)

    # 8. Return folio and ah04e_2
    return top10[["folio", "ah04e_2"]].reset_index(drop=True)