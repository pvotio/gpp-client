def generate_table_name(name):
    return f"etl.gpp_{name.split('_')[-1].split('.')[0].lower()}"
