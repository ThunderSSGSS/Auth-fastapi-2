class Transaction():
    type=None
    def __init__(self, tablename:str):
        self.tablename = tablename

    def dict(self):
        data = {}
        for attribute, value in self.__dict__.items():
            if value is not None: data[attribute] = value
        data['type']= self.type
        return data


class Create(Transaction):
    type='create'
    def __init__(self, tablename:str, data:dict):
        self.data = data
        super().__init__(tablename)


class Update(Transaction):
    type='update'
    def __init__(self, tablename:str, id:dict, data:dict):
        self.id = id
        self.data = data
        super().__init__(tablename)


class Delete(Transaction):
    type='delete'
    def __init__(self, tablename:str, id:dict):
        self.id = id
        super().__init__(tablename)


class DeleteManyBy(Transaction):
    type='delete_many_by'
    def __init__(self, tablename:str, id:dict):
        self.id = id
        super().__init__(tablename)
