def serialize_item_dict(a) -> dict:
    return {**{i:str(a[i]) for i in a if i=='_id'}, **{i:a[i] for i in a if i !='_id'}}

def serialize_items_list(entity) -> list:
    return [serialize_item_dict(a) for a in entity]