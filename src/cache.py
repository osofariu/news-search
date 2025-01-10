import json

class NewsCache:
    def __init__(self):
        pass
    
    def get_by_date(self, year, month):
        key = f"{year}-{month}"
        return self.get(key)
    
    def get(self, key):
        """get item from cache
    
        Args:
            key (str): "YYYY-MM" formatted date
            
        Returns:
            - None if cache item not found
            - List[ArchiveItem]: a list of ArchiveItem objects
        """
        try:
            with open(f'data/{key}.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def put_by_date(self, year, month, value):
        key = f"{year}-{month}"
        self.put(key, value)   
    
    
    def put(self, key, value):
        """add item to cache if not already present

        Args:
            key (str): "YYYY-MM" formatted date
            value (List[ArchiveItem]:): archive items matching the key
        """

        with open(f'data/{key}.json', 'w') as f:
            json.dump(value, f)