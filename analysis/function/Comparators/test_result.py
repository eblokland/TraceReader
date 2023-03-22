class TestResult(object):
    def __init__(self, identifier: str, val1, val2, res):
        self.identifier = identifier
        self.val1 = val1
        self.val2 = val2
        self.result = res

    def get_csv_header(self):
        return [str(self.identifier) + ' ' + 'trace1 mean', str(self.identifier) + ' trace2 mean',
                str(self.identifier) + ' p-value']

    def get_csv_fields(self):
        return [self.val1, self.val2, self.result.pvalue]

    def __str__(self):
        return f'Identifier: {self.identifier}, t1 mean = {self.val1}, ' \
               f't2 mean = {self.val2}, p-val = {self.result.pvalue}'

