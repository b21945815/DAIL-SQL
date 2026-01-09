import json
import os
import shutil

INPUT_DEV_PATH = "./data/dev_20240627/dev.json"
INPUT2_DEV_PATH = "./data/dev_20240627/dev_tied_append.json"
INPUT_TABLES_PATH = "./data/dev_20240627/dev_tables.json"
INPUT_DEV_DB_ROOT = "./data/dev_20240627/dev_databases"

INPUT_TRAIN_PATH = "./data/train/train.json"
INPUT_TRAIN_TABLES_PATH = "./data/train/train_tables.json"
INPUT_TRAIN_DB_ROOT = "./data/train/train_databases"

OUTPUT_ROOT = "./dataset"
OUTPUT_DIR = os.path.join(OUTPUT_ROOT, "bird")
OUTPUT_DB_DIR = os.path.join(OUTPUT_DIR, "database")
OUTPUT_DEV_DIR = os.path.join(OUTPUT_DIR, "dev")
OUTPUT_TRAIN_DIR = os.path.join(OUTPUT_DIR, "train")

def copy_databases(source_root, target_root, db_list=None):
    if not os.path.exists(source_root):
        print(f"Warning: Database source {source_root} not found.")
        return

    for db_name in os.listdir(source_root):
        if db_list and db_name not in db_list:
            continue
            
        src_path = os.path.join(source_root, db_name)
        dst_path = os.path.join(target_root, db_name)
        
        if os.path.isdir(src_path):
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)

def main():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DB_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DEV_DIR, exist_ok=True)
    os.makedirs(OUTPUT_TRAIN_DIR, exist_ok=True)

    all_financial_dev = []
    
    if os.path.exists(INPUT_DEV_PATH):
        with open(INPUT_DEV_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_financial_dev.extend([x for x in data if x.get('db_id') == 'financial'])

    if os.path.exists(INPUT2_DEV_PATH):
        with open(INPUT2_DEV_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_financial_dev.extend([x for x in data if x.get('db_id') == 'financial'])
    
    with open(os.path.join(OUTPUT_DEV_DIR, "dev.json"), 'w', encoding='utf-8') as f:
        json.dump(all_financial_dev, f, indent=4, ensure_ascii=False)
    
    with open(os.path.join(OUTPUT_DEV_DIR, "dev.sql"), 'w', encoding='utf-8') as f:
        for item in all_financial_dev:
            sql = item.get('SQL', item.get('query', ''))
            f.write(sql.replace('\n', ' ') + '\n')

    if os.path.exists(INPUT_TRAIN_PATH):
        shutil.copy(INPUT_TRAIN_PATH, os.path.join(OUTPUT_TRAIN_DIR, "train.json"))
        
        with open(INPUT_TRAIN_PATH, 'r', encoding='utf-8') as f:
            train_data = json.load(f)
        with open(os.path.join(OUTPUT_TRAIN_DIR, "train_gold.sql"), 'w', encoding='utf-8') as f:
             for item in train_data:
                sql = item.get('SQL', item.get('query', ''))
                f.write(sql.replace('\n', ' ') + '\n')

    all_tables = []
    train_tables = []
    financial_tables = []
    train_db_names = []
    
    if os.path.exists(INPUT_TRAIN_TABLES_PATH):
        with open(INPUT_TRAIN_TABLES_PATH, 'r', encoding='utf-8') as f:
            train_tables = json.load(f)
            all_tables.extend(train_tables)
            train_db_names = [t['db_id'] for t in train_tables]
            
        with open(os.path.join(OUTPUT_TRAIN_DIR, "train_tables.json"), 'w', encoding='utf-8') as f:
            json.dump(train_tables, f, indent=4, ensure_ascii=False)
    
    if os.path.exists(INPUT_TABLES_PATH):
        with open(INPUT_TABLES_PATH, 'r', encoding='utf-8') as f:
            dev_tables = json.load(f)
        financial_tables = [t for t in dev_tables if t.get('db_id') == 'financial']
        all_tables.extend(financial_tables)

        with open(os.path.join(OUTPUT_DEV_DIR, "dev_tables.json"), 'w', encoding='utf-8') as f:
            json.dump(financial_tables, f, indent=4, ensure_ascii=False)
        
    with open(os.path.join(OUTPUT_DIR, "tables.json"), 'w', encoding='utf-8') as f:
        json.dump(all_tables, f, indent=4, ensure_ascii=False)

    copy_databases(INPUT_TRAIN_DB_ROOT, OUTPUT_DB_DIR, train_db_names)
    copy_databases(INPUT_DEV_DB_ROOT, OUTPUT_DB_DIR, ['financial'])

if __name__ == "__main__":
    main()