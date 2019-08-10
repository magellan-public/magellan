# assume the pipeline schema does not change
# then this diff will return the tables  in pitNew that have different entries with pitOld
def diff(pitOld, pitNew):
    pass

class FlowRulesGenerator:
    def __init__(self, dsProxy):
        self.dsProxy = dsProxy
        self.existingPITs = {} # portTag -> pit

    # pit: a list of tables
    def accept_new_pit(self, portTag, pit):
        if portTag in self.existingPITs:
            existingPIT = self.existingPITs[portTag]

