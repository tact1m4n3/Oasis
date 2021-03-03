from sym import D_CHAR, D_NULL, D_INT
from tokentypes import *

NO_REG = -1

class CodeGenerator(object):
    reg_status = [0, 0, 0, 0, 0, 0, 0, 0]
    reg_names = ["r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]
    breg_names = ["br8", "br9", "br10", "br11", "br12", "br13", "br14", "br15"]
    dreg_names = ["r8d", "r9d", "r10d", "r11d", "r12d", "r13d", "r14d", "r15d"]

    nasm_type_names = {
        D_INT: "dword",
        D_CHAR: "byte"
    }

    def __init__(self, fn):
        self.fn = fn
        self.file_content = ""
        self.bss_section = "section .bss\n"

        self.last_label_num = 0

    def close_file(self):
        with open(self.fn, "w+") as f:
            f.write(self.file_content + '\n' + self.bss_section)

    def free_register(self, reg):
        self.reg_status[reg] = 0
    
    def gen_next_label(self):
        self.last_label_num += 1
        return ".L" + str(self.last_label_num)

    def alloc_register(self):
        reg = NO_REG
        for i in range(len(self.reg_status)):
            if not self.reg_status[i]:
                reg = i
                self.reg_status[i] = 1
                break

        return reg

    def get_reg(self, name, type_):
        if type_ == D_CHAR:
            return name + "b"
        elif type_ == D_INT:
            return name + "d"

    def generate_beginning(self):
        self.write_line('section .text')
        self.write_line('extern _printf, _malloc, _free')
        self.write_line()
        self.write_line('PRINTF_INT: db "%d", 10, 0')
        self.write_line('PRINTF_CHAR: db "%c", 0')
        self.write_line()
        self.write_line('printint:')
        self.write_line('\tpush\trbp')
        self.write_line('\tmov\trbp, rsp')
        self.write_line('\tsub\trsp, 16')
        self.write_line('\tmov\t[rbp-4], edi')
        self.write_line('\tmov\teax, [rbp-4]')
        self.write_line('\tmov\tesi, eax')
        self.write_line('\tmov\trdi, PRINTF_INT')
        self.write_line('\tmov\teax, 0')
        self.write_line('\tcall\t_printf')
        self.write_line('\tmov\trsp, rbp')
        self.write_line('\tpop\trbp')
        self.write_line('\tret')
        self.write_line()
        self.write_line('printchar:')
        self.write_line('\tpush\trbp')
        self.write_line('\tmov\trbp, rsp')
        self.write_line('\tsub\trsp, 16')
        self.write_line('\tmov\t[rbp-1], dl')
        self.write_line('\tmov\tax, [rbp-1]')
        self.write_line('\tmov\tsi, ax')
        self.write_line('\tmov\trdi, PRINTF_CHAR')
        self.write_line('\tmov\teax, 0')
        self.write_line('\tcall\t_printf')
        self.write_line('\tmov\trsp, rbp')
        self.write_line('\tpop\trbp')
        self.write_line('\tret')
        self.write_line()
        self.write_line()

    def load_int(self, val):
        reg = self.alloc_register()

        self.write_line("\tmov\t{}, {}".format(self.get_reg(self.reg_names[reg], D_INT), val))

        return reg
    
    def load_char(self, val):
        reg = self.alloc_register()

        self.write_line("\tmov\t{}, {}".format(self.get_reg(self.reg_names[reg], D_CHAR), val))

        return reg

    def add_int(self, r1, r2):
        self.write_line("\tadd\t{}, {}".format(self.get_reg(self.reg_names[r1], D_INT), self.get_reg(self.reg_names[r2], D_INT)))

        self.free_register(r2)

        return r1

    def sub_int(self, r1, r2):
        self.write_line("\tsub\t{}, {}".format(self.get_reg(self.reg_names[r1], D_INT), self.get_reg(self.reg_names[r2], D_INT)))

        self.free_register(r2)

        return r1

    def mul_int(self, r1, r2):
        self.write_line("\tmul\t{}, {}".format(self.get_reg(self.reg_names[r1], D_INT), self.get_reg(self.reg_names[r2], D_INT)))

        self.free_register(r2)

        return r1

    def div_int(self, r1, r2):
        self.write_line("\tmov\teax, {}".format(self.get_reg(self.reg_names[r1], D_INT)))
        self.write_line("\tidiv\t{}".format(self.get_reg(self.reg_names[r2], D_INT)))
        self.write_line("\tmov\t{}, eax".format(self.get_reg(self.reg_names[r1], D_INT)))

        self.free_register(r2)

        return r1
    
    nasm_set_instructions = {
        T_DEQ: "sete",
        T_NEQ: "setne",
        T_LT: "setl",
        T_LTE: "setle",
        T_GT: "setg",
        T_GTE: "setge"
    }

    nasm_jmp_instructions_if = {
        T_DEQ: "jne",
        T_NEQ: "je",
        T_LT: "jge",
        T_LTE: "jg",
        T_GT: "jle",
        T_GTE: "jl"
    }

    def cmp_int(self, r1, r2, op):
        self.write_line("\tcmp\t{}, {}".format(self.get_reg(self.reg_names[r1], D_INT), self.get_reg(self.reg_names[r2], D_INT)))
        self.write_line("\t{}\t{}".format(self.nasm_set_instructions[op], self.get_reg(self.reg_names[r1], D_CHAR)))

        self.free_register(r2)
        
        return r1
    
    def cmp_char(self, r1, r2, op):
        self.write_line("\tcmp\t{}, {}".format(self.get_reg(self.reg_names[r1], D_CHAR), self.get_reg(self.reg_names[r2], D_CHAR)))
        self.write_line("\t{}\t{}".format(self.nasm_set_instructions[op], self.get_reg(self.reg_names[r1], D_CHAR)))

        self.free_register(r2)
        
        return r1
    
    def gen_jmp_if_false(self, r, t, label):
        self.write_line("\tcmp\t{}, {}".format(self.get_reg(self.reg_names[r], t), 0))
        self.write_line("\tje\t{}".format(label))

        self.free_register(r)

    def add_char(self, r1, r2):
        self.write_line("\tadd\t{}, {}".format(self.get_reg(self.reg_names[r1], D_CHAR), self.get_reg(self.reg_names[r2], D_CHAR)))

        self.free_register(r2)

        return r1

    def sub_char(self, r1, r2):
        self.write_line("\tsub\t{}, {}".format(self.get_reg(self.reg_names[r1], D_CHAR), self.get_reg(self.reg_names[r2], D_CHAR)))

        self.free_register(r2)

        return r1

    def mul_char(self, r1, r2):
        self.write_line("\tmul\t{}, {}".format(self.get_reg(self.reg_names[r1], D_CHAR), self.get_reg(self.reg_names[r2], D_CHAR)))

        self.free_register(r2)

        return r1

    def div_char(self, r1, r2):
        self.write_line("\tmov\tax, {}".format(self.get_reg(self.reg_names[r1], D_CHAR)))
        self.write_line("\tidiv\t{}".format(self.get_reg(self.reg_names[r2], D_CHAR)))
        self.write_line("\tmov\t{}, ax".format(self.get_reg(self.reg_names[r1], D_CHAR)))

        self.free_register(r2)

        return r1

    def print_int(self, r):
        self.write_line("\tmov\tedi, {}".format(self.get_reg(self.reg_names[r], D_INT)))
        self.write_line("\tcall printint")
    
    def print_char(self, r):
        self.write_line("\tmov\tdl, {}".format(self.get_reg(self.reg_names[r], D_CHAR)))
        self.write_line("\tcall printchar")

    def gen_function_beginning(self, func_name):
        self.write_line("global _{}".format(func_name))
        self.write_line("_{}:".format(func_name))
        self.write_line("\tpush\trbp")
        self.write_line("\tmov\trbp, rsp")

    def gen_function_end(self):
        self.write_line("\tmov\trsp, rbp")
        self.write_line("\tpop\trbp")
        self.write_line("\tret")

    def gen_decl_global_var(self, type_, name):
        self.write_line_bss(f"global _{name}")
        self.write_line_bss(f"_{name}:")

        self.write_line_bss(f"\tresb\t{type_}") # type_ has the value of its size
    
    def gen_load_global_var(self, type_, name):
        r = self.alloc_register()
        r_addr = self.alloc_register()
        
        self.write_line(f"\tmov\t{self.reg_names[r_addr]}, _{name}")
        self.write_line(f"\tmov\t{self.get_reg(self.reg_names[r], type_)}, {self.nasm_type_names[type_]} [{self.reg_names[r_addr]}]")
        
        self.free_register(r_addr)

        return r

    def gen_load_local_var(self, type_, offset):
        r = self.alloc_register()

        self.write_line(f"\tmov\t{self.get_reg(self.reg_names[r], type_)}, {self.nasm_type_names[type_]} [rbp - {offset}]")

        return r
    
    def gen_assign_global_var(self, type_, name, r):
        r_addr = self.alloc_register()

        self.write_line(f"\tmov\t{self.reg_names[r_addr]}, _{name}")
        self.write_line(f"\tmov\t{self.nasm_type_names[type_]} [{self.reg_names[r_addr]}], {self.get_reg(self.reg_names[r], type_)}")

        self.free_register(r)
    
    def gen_assign_local_var(self, type_, offset, r):
        self.write_line(f"\tmov\t{self.nasm_type_names[type_]} [rbp - {offset}], {self.get_reg(self.reg_names[r], type_)}")

        self.free_register(r)
        
    def gen_align_stack(self):
        self.write_line("\tsub\trsp, 16")

    def gen_label(self, name):
        self.write_line(name + ":")
    
    def gen_jmp_to_label(self, name):
        self.write_line("\tjmp\t{}".format(name))

    def write_line(self, ln=""):
        self.file_content += ln + "\n"
    
    def write_line_bss(self, ln=""):
        self.bss_section += ln + "\n"
