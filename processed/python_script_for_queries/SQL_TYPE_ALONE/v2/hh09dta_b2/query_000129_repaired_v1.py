import pandas as pd


def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # Initialize result structure in case of early return
    result_cols = ["nna01", "households_count"]

    # Retrieve tables safely
    portad = tables.get("ii_portad", pd.DataFrame()).copy()
    vlh = tables.get("ii_vlh", pd.DataFrame()).copy()
    nna = tables.get("ii_nna", pd.DataFrame()).copy()

    # Basic validations
    if portad.empty or vlh.empty or nna.empty:
        return pd.DataFrame(columns=result_cols)
    if "folio" not in portad.columns or "folio" not in vlh.columns or "folio" not in nna.columns:
        return pd.DataFrame(columns=result_cols)

    # Filter households to Oaxaca (ent == 20)
    if "ent" in portad.columns:
        ent_num = pd.to_numeric(portad["ent"], errors="coerce")
        oax_folios = portad.loc[ent_num == 20, ["folio"]].drop_duplicates()
    else:
        # If 'ent' is missing, proceed with all households (conservative fallback)
        oax_folios = portad[["folio"]].drop_duplicates()

    if oax_folios.empty:
        return pd.DataFrame(columns=result_cols)

    # Restrict persons to Oaxaca households
    persons = vlh.merge(oax_folios, on="folio", how="inner")

    # Find an age column
    age_col = None
    for c in persons.columns:
        if c.lower() == "edad":
            age_col = c
            break
    if age_col is None:
        for c in persons.columns:
            if c.lower() == "age":
                age_col = c
                break
    if age_col is None:
        for c in persons.columns:
            if "edad" in c.lower():
                age_col = c
                break
    if age_col is None:
        return pd.DataFrame(columns=result_cols)

    # Clean and compute age flags
    persons["_age"] = pd.to_numeric(persons[age_col], errors="coerce")
    persons = persons.dropna(subset=["_age"]).copy()
    if persons.empty:
        return pd.DataFrame(columns=result_cols)

    hh_flags = (
        persons.assign(
            _is_old=lambda d: d["_age"] >= 60,
            _is_young=lambda d: d["_age"] < 30,
        )
        .groupby("folio", as_index=False)
        .agg(has_old=("_is_old", "max"), has_young=("_is_young", "max"))
    )

    qualifying = hh_flags.loc[hh_flags["has_old"] & hh_flags["has_young"], ["folio"]].drop_duplicates()
    if qualifying.empty:
        return pd.DataFrame(columns=result_cols)

    # Identify nna01 column
    nna_col = None
    for c in nna.columns:
        if c.lower() == "nna01":
            nna_col = c
            break
    if nna_col is None:
        for c in nna.columns:
            if "nna01" in c.lower():
                nna_col = c
                break
    if nna_col is None:
        return pd.DataFrame(columns=result_cols)

    nna_status = nna[["folio", nna_col]].drop_duplicates(subset=["folio"]).copy()

    merged = qualifying.merge(nna_status, on="folio", how="inner")
    if merged.empty:
        return pd.DataFrame(columns=result_cols)

    merged["_nna01"] = pd.to_numeric(merged[nna_col], errors="coerce")

    # Prefer standard categories 1/2 if available
    filtered = merged[merged["_nna01"].isin([1, 2])].copy()
    if filtered.empty:
        counts = (
            merged.groupby(nna_col, as_index=False)
            .agg(households_count=("folio", "nunique"))
            .rename(columns={nna_col: "nna01"})
        )
        return counts[["nna01", "households_count"]]

    counts = (
        filtered.groupby("_nna01", as_index=False)
        .agg(households_count=("folio", "nunique"))
        .rename(columns={"_nna01": "nna01"})
    )

    return counts[["nna01", "households_count"]]
