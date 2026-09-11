def run_query(tables: dict[str, 'pd.DataFrame']) -> 'pd.DataFrame':
    import pandas as pd
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]

    # Step 1: Oaxaca households that own/share a non-ag business
    # ent==20 is Oaxaca, nna01==1 means owns/shares non-ag business
    oaxaca_households = df_portad[df_portad["ent"] == 20.0][["folio"]].drop_duplicates()
    nna_owners = df_nna[df_nna["nna01"] == 1.0][["folio"]].drop_duplicates()
    oaxaca_nna_households = pd.merge(oaxaca_households, nna_owners, on="folio", how="inner")

    # Step 2: All individuals in those households
    oaxaca_nna_folios = oaxaca_nna_households["folio"].unique()
    df_people = df_portad[df_portad["folio"].isin(oaxaca_nna_folios)].copy()

    # Step 3: Compute overall average age of such individuals (in these households)
    avg_age = df_people["edad"].mean()

    # Step 4: Split into A and B
    # A: Result Interview == 20
    df_A = df_people[df_people["rel"] == 20.0]
    # B: edad > avg_age
    df_B = df_people[df_people["edad"] > avg_age]

    # Step 5: For each household, count ordered pairs (A, B)
    # Only pairs where A and B are different individuals (ls)
    def count_pairs(group):
        n_A = (group["rel"] == 20.0).sum()
        n_B = (group["edad"] > avg_age).sum()
        # Remove overlap: if a person is both A and B, don't pair with self
        # But since A: rel==20, B: edad>avg_age, so overlap is possible
        overlap = ((group["rel"] == 20.0) & (group["edad"] > avg_age)).sum()
        # For each A, can pair with each B except self if overlap
        # Total pairs = n_A * n_B - overlap
        return n_A * n_B - overlap

    pairs_per_household = (
        df_people.groupby("folio").apply(count_pairs)
    )

    total_pairs = pairs_per_household.sum()

    return pd.DataFrame({"count_ordered_pairs": [int(total_pairs)]})