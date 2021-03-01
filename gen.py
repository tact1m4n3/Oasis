from sym import D_NULL, D_INT, v_sizes

NO_REG = -1


class CodeGenerator(object):
    reg_status = [0, 0, 0, 0, 0, 0, 0, 0]
    reg_names = ["r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]
    breg_names = ["br8", "br9", "br10", "br11", "br12", "br13", "br14", "br15"]
    nasm_types_and_val = {
        D_INT: "0xFFFFFFFF"
    }

    nasm_type_names = {
        D_INT: "dword"
    }

    def __init__(self, fn):
        self.fn = fn
        self.file_content = ""
        self.bss_section = "section .bss\n"
        self.constant_pool = {}

    def close_file(self):
        with open(self.fn, "w+") as f:
            f.write(self.file_content + '\n' + self.bss_section)

    def free_register(self, reg):
        self.reg_status[reg] = 0

    def alloc_register(self):
        reg = NO_REG
        for i in range(len(self.reg_status)):
            if not self.reg_status[i]:
                reg = i
                self.reg_status[i] = 1
                break

        return reg

    def generate_beginning(self):
        self.write_line('section .text')
        self.write_line('extern _printf, _malloc, _free')
        self.write_line()
        self.write_line('PRINTF_INT: db "%d", 10, 0')
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
        self.write_line()

    def load_int(self, val):
        reg = self.alloc_register()

        self.write_line("\tmov\t{}, {}".format(self.reg_names[reg], val))

        return reg

    def add_int(self, r1, r2):
        self.write_line("\tadd\t{}, {}".format(self.reg_names[r1], self.reg_names[r2]))

        self.free_register(r2)

        return r1

    def sub_int(self, r1, r2):
        self.write_line("\tsub\t{}, {}".format(self.reg_names[r1], self.reg_names[r2]))

        self.free_register(r2)

        return r1

    def mul_int(self, r1, r2):
        self.write_line("\tmul\t{}, {}".format(self.reg_names[r1], self.reg_names[r2]))

        self.free_register(r2)

        return r1

    def div_int(self, r1, r2):
        self.write_line("\tmov\trax, {}".format(self.reg_names[r1]))
        self.write_line("\tidiv\t{}".format(self.reg_names[r2]))
        self.write_line("\tmov\t{}, rax".format(self.reg_names[r1]))

        self.free_register(r2)

        return r1

    def print_int(self, r):
        self.write_line("\tmov\trdi, {}".format(self.reg_names[r]))
        self.write_line("\tcall printint")

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
        
        self.write_line(f"\tmov\t{self.reg_names[r]}, _{name}")
        self.write_line(f"\tmov\t{self.reg_names[r]}, [{self.reg_names[r]}]")
        self.write_line(f"\tand\t{self.reg_names[r]}, {self.nasm_types_and_val[type_]}")
        
        return r

    def gen_load_local_var(self, type_, offset):
        r = self.alloc_register()

        self.write_line(f"\tmov\t{self.reg_names[r]}, {self.nasm_type_names[type_]} [rbp - {offset}]")

        return r
    
    def gen_assign_global_var(self, type_, name, r):
        r_addr = self.alloc_register()

        self.write_line(f"\tmov\t{self.reg_names[r_addr]}, _{name}")
        self.write_line(f"\tand\t{self.reg_names[r_addr]}, {self.nasm_types_and_val[type_]}")
        self.write_line(f"\tmov\tqword [{self.reg_names[r_addr]}], {self.reg_names[r]}")

        self.free_register(r_addr)
        self.free_register(r)
    
    def gen_assign_local_var(self, type_, offset, r):
        self.write_line(f"\tmov\t{self.nasm_type_names[type_]} [rbp - {offset}], {self.reg_names[r]}")

        self.free_register(r)
        
    def gen_align_stack(self):
        self.write_line("\tsub\trsp, 16")

    def write_line(self, ln=""):
        self.file_content += ln + "\n"
    
    def write_line_bss(self, ln=""):
        self.bss_section += ln + "\n"
