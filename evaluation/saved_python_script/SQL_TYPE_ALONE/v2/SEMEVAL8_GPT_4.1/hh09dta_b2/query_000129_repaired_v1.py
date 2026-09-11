def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]

    # Filter to Oaxaca (ent == 20)
    df_oax = df_portad[df_portad["ent"] == 20.0]

    # For each household, check if at least one member >=60 and at least one <30
    hh_age = df_oax.groupby("folio")["edad"].agg(
        has_60plus=lambda x: np.any(x >= 60),
        has_under30=lambda x: np.any(x < 30)
    ).reset_index()

    hh_age = hh_age[(hh_age["has_60plus"]) & (hh_age["has_under30"])]

    # Merge with ii_nna to get business ownership
    df_nna_sel = df_nna[["folio", "nna01"]].drop_duplicates("folio")
    merged = hh_age.merge(df_nna_sel, on="folio", how="left")

    # nna01: 1=Yes, 2=No, nan=missing
    def nna01_label(val):
        if val == 1.0:
            return "Yes"
        elif val == 2.0:
            return "No"
        else:
            return "No"  # treat missing as No (conservative)

    merged["owns_nonag_biz"] = merged["nna01"].apply(nna01_label)

    # Group and count
    result = merged.groupby("owns_nonag_biz").size().reset_index(name="household_count")
    result = result.sort_values("owns_nonag_biz").reset_index(drop=True)
    return result