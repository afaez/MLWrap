class Logger:
    """ Logger wraps a models.Result instance and allows to append or set its result text. Used when doing training or prediciton.
    """
    def __init__(self, result):
        self.result = result
        self.replace("")

    def append(self, string):
        if string is not None:
            self.result.result_text += f"\n{string}"
            self.result.save()

    def replace(self, string):
        if string is None:
            self.result.result_text = ""
        else:
            self.result.result_text = string
        self.result.save()

    def getlog(self):
        return self.result.result_text