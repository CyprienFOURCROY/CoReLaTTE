import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_nna = tables["ii_nna"].copy()
    df_ah = tables["ii_ah"].copy()

    # Households in Oaxaca
    oax_folios = df_portad.loc[df_portad["ent"] == 20.0, "folio"].unique()

    # Households that own/share a non-ag business
    nna_hh = (
        df_nna.loc[df_nna["folio"].isin(oax_folios), ["folio", "nna01"]]
        .drop_duplicates(subset=["folio"])
    )
    nna_hh = nna_hh[nna_hh["nna01"] == 1.0]
    target_folios = set(nna_hh["folio"])

    # Count adults (age 18+) per household
    adults = df_portad[df_portad["folio"].isin(target_folios)].copy()
    adults["is_adult"] = adults["edad"] >= 18
    adults_per_hh = adults.groupby("folio", as_index=False)["is_adult"].sum()
    adults_per_hh = adults_per_hh.rename(columns={"is_adult": "num_adults"})

    # Domestic appliance ownership at household level
    ah_dom = (
        df_ah.loc[df_ah["folio"].isin(target_folios), ["folio", "ah03g"]]
        .drop_duplicates(subset=["folio"])
    )
    mapping = {1.0: "yes", 3.0: "no"}
    ah_dom["owns_domestic_appliance"] = ah_dom["ah03g"].map(mapping)

    # Merge and filter valid groups (yes/no)
    hh = adults_per_hh.merge(ah_dom[["folio", "owns_domestic_appliance"]], on="folio", how="left")
    hh = hh[hh["owns_domestic_appliance"].isin(["yes", "no"])]

    # Aggregate
    result = (
        hh.groupby("owns_domestic_appliance", as_index=False)
        .agg(
            average_adults_per_household=("num_adults", "mean"),
            households=("folio", "nunique"),
        )
    )

    return result