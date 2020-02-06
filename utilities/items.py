
class Item:
    def __init__(self, reference, threshold=None):
        self.reference = reference
        self.threshold = threshold
    

    def has_unique_threshold(self):
        return self.threshold is not None
