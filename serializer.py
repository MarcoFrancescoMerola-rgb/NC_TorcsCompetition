import pickle

def serialize(path,obj):
    with open(path,'wb') as f:
        pickle.dump(obj,f)

def deserialize(path):
    with open(path,'rb') as f:
        return pickle.load(f)

def fromFloatArrayToStringArray(path,obj):
    pass
    # for o in obj:
    #     if type(o) == list:
            

if __name__ == "__main__":
    pass
