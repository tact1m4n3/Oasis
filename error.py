class Error:
    def __init__(self, msg, pos_start, pos_end):
        self.msg = msg
        self.pos_start = pos_start
        self.pos_end = pos_end

    def as_string(self):
        text = "Error: " + self.msg + "\n"
        idx_beg = 0
        lines = self.pos_start.filetext.split('\n')
        for i in range(self.pos_start.line):
            idx_beg += len(lines[i]) + 1
        line = lines[self.pos_start.line]
        line = line.replace('\t', ' ') # to align the arrows
        text += "-> " + line + "\n"
        text += "   " + (" " * (self.pos_start.idx - idx_beg)) + "^" * (self.pos_end.idx - self.pos_start.idx)

        return text
