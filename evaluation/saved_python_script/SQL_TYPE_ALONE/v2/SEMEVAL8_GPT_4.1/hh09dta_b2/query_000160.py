def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd

    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_in = tables["ii_in"]

    # Households that produced/sold dairy products in last 12 months
    dairy_hh = df_inr[df_inr["inr02a"] == 1][["folio"]].drop_duplicates()

    # Merge with state info
    dairy_hh_state = pd.merge(dairy_hh, df_portad[["folio", "ent"]], on="folio", how="left").drop_duplicates(subset=["folio"])

    # For each household, check if any member received Liconsa milk in last 12 months
    liconsa = df_in[df_in["in03a"] == 1][["folio"]].drop_duplicates()
    dairy_hh_state["received_liconsa"] = dairy_hh_state["folio"].isin(liconsa["folio"])

    # Group by state
    result = (
        dairy_hh_state.groupby("ent")
        .agg(
            households_produce_sell_dairy=("folio", "nunique"),
            households_produce_sell_dairy_and_liconsa=("received_liconsa", "sum")
        )
        .reset_index()
        .rename(columns={"ent": "state"})
    )

    return result