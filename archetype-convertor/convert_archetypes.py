import pandas as pd
import geopandas as gpd
import json


def create_mapped_result(inventory_path: str, dmg_result_path: str, archetype_mapping_path: str):
    """

    Args:
        inventory_path: Path to the zip file containing the inventory example: /Users/myuser/5f9091df3e86721ed82f701d.zip
        dmg_result_path: Path to the damage result output file
        archetype_mapping_path: Path to the arechetype mappings

    Returns: JSON of the results ordered by cluster and category. Also creates a csv file with max damage state

    """
    buildings = pd.DataFrame(gpd.read_file("zip://" + inventory_path))
    dmg_result = pd.read_csv(dmg_result_path)
    arch_mapping = pd.read_csv(archetype_mapping_path)

    unique_categories = arch_mapping.groupby(by=['cluster', 'category'], sort=False).count().reset_index()

    guids = dmg_result[['guid']]
    max_val = dmg_result[['insignific', 'moderate', 'heavy', 'complete']].max(axis=1)
    max_key = dmg_result[['insignific', 'moderate', 'heavy', 'complete']].idxmax(axis=1)
    dmg_concat = pd.concat([guids, max_val, max_key], axis=1)
    dmg_concat.rename(columns={0: 'max_prob', 1: 'max_state'}, inplace=True)
    dmg_merged = pd.merge(buildings, dmg_concat, on='guid')[['guid', 'geometry', 'archetype', 'max_prob', 'max_state']]
    mapped = pd.merge(dmg_merged, arch_mapping, on='archetype')

    mapped.to_csv("bldDmgMaxDamageState.csv", columns=['guid', 'max_state'], index=False)

    group_by = mapped.groupby(by=['max_state', 'cluster', 'category']).count().reset_index()
    group_by = group_by.loc[:, ['guid', 'max_state', 'cluster', 'category']]
    group_by.rename(columns={'guid': 'count'}, inplace=True)

    pivot = group_by.pivot_table(values='count', index=['cluster', 'category'], columns='max_state', fill_value=0)

    table = pd.DataFrame()
    table[['category', 'cluster']] = unique_categories[['category', 'cluster']]
    result_by_cluster = pd.merge(table, pivot, how='left', on=['cluster', 'category'])
    result_by_category = result_by_cluster.groupby(by=['category'], sort=False).sum().reset_index()

    result_by_cluster[['insignific', 'moderate', 'heavy', 'complete']] = result_by_cluster[
        ['insignific', 'moderate', 'heavy', 'complete']].fillna(-1).astype(int)
    result_by_category[['insignific', 'moderate', 'heavy', 'complete']] = result_by_category[
        ['insignific', 'moderate', 'heavy', 'complete']].fillna(-1).astype(int)

    cluster_records = result_by_cluster.to_json(orient="records")
    category_records = result_by_category.to_json(orient="records")
    json_by_cluster = json.loads(cluster_records)
    json_by_category = json.loads(category_records)

    ret_json = json.dumps({"by_cluster": json_by_cluster, "by_category": json_by_category})
    return ret_json


if __name__ == '__main__':
    res = create_mapped_result(inventory_path="/Users/vnarah2/incore-data/scripts/joplin.zip",
                               dmg_result_path="/Users/vnarah2/incore-data/scripts/joplin_bldg_dmg.csv",
                               archetype_mapping_path="/Users/vnarah2/incore-data/scripts/archetype-mapping.csv"
                               )
    print(res)
