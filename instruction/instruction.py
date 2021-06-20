class Instruction:
    def __init__(self, op, num1, num2, result):
        self.op = op
        self.num1 = num1
        self.num2 = num2
        self.res = result if result else ""

    def __repr__(self):
        # print(f'{self.op}, {self.num1}, {self.num2}, {self.res}')
        return "{:<7}, {:<6}, {:<6}, {:<6}".format(self.op, self.num1, self.num2, self.res)


class InstructionManager:
    def __init__(self):
        self.instructions = []
        self.cur_tmpreg = 0

    def add_instruction(self, op, num1, num2, res):
        self.instructions.append(Instruction(op, num1, num2, res))

    def add_label(self, label):
        self.instructions[-1].res = label

    def print(self):
        fw = open(f'./result/intermediate_code.txt', 'w')
        for ins in self.instructions:
            print(ins)
            fw.write(str(ins))
            fw.write('\n')

    def get_temp_reg(self):
        res = "temp" + str(self.cur_tmpreg)
        self.cur_tmpreg += 1
        return res
