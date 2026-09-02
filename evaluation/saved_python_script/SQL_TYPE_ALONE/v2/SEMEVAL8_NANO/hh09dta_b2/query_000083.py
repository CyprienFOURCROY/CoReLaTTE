def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import pandas as pd

    # Extract tables
    portad = tables["ii_portad"]
    ah = tables["ii_ah"]
    vlh = tables["ii_vlh"]
    
    # Filter households with at least one adult member (edad >= 18)
    # First, get households with at least one adult
    adults = portad[portad["edad"] >= 18]
    households_with_adults = adults["folio"].drop_duplicates()

    # Filter households where at least one member reports owning the dwelling they live in
    # Join ah with portad to get 'folio' and 'ah03a'
    ah_with_folio = ah[["folio", "ah03a"]]
    households_with_dwelling_owner = ah_with_folio[ah_with_folio["ah03a"] == 1]["folio"].drop_duplicates()

    # Filter households that report feeling unsafe or very unsafe at home
    # 'vlh04' values: 3 (Unsafe), 4 (Very unsafe)
    unsafe_households = vlh[vlh["vlh04"].isin([3, 4])]["folio"].drop_duplicates()

    # Filter households where 'vlh01b' (district gather gangs/factions) indicates 'No' (3)
    # and 'vlh01b' == 3
    households_close_locality = vlh[vlh["vlh01b"] == 3]["folio"].drop_duplicates()

    # Combine all conditions
    result_folios = (
        set(households_with_adults)
        & set(households_with_dwelling_owner)
        & set(unsafe_households)
        & set(households_close_locality)
    )

    # Count the number of such households
    count = len(result_folios)

    return pd.DataFrame({"households_meeting_criteria": [count]})