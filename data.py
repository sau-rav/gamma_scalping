price = [100, 103, 100, 97, 100, 107, 100]

def getVolatility():
    return 0.5

def getSpotPrice(idx):
    # returns spot price for the underlying asset from the dataset
    return price[idx]