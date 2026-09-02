def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]

    # Filter Oaxaca (ent == 20)
    df_portad_oax = df_portad[df_portad["ent"] == 20]

    # Filter Individual ID '01'
    df_portad_oax_01 = df_portad_oax[df_portad_oax["ls"] == "01"]

    # Households in Oaxaca with member '01'
    # Merge with inr to get only those that produced/sold dairy (inr02a == 1)
    df_merged = pd.merge(
        df_portad_oax_01,
        df_inr[["folio", "inr02a"]],
        on="folio",
        how="inner"
    )

    # Only those that produced/sold dairy (inr02a == 1)
    df_final = df_merged[df_merged["inr02a"] == 1]

    # Compute average age
    avg_age = df_final["edad"].mean()

    return pd.DataFrame({"average_age": [avg_age]})