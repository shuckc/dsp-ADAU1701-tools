
import csv

def dec_5_23(bs: bytes)-> float:
    # 5.23 format (28 bits)
    assert len(bs) == 4
    param = int.from_bytes(bs)
    negative = bs[0] & 0x08 == 0x08
    if negative:
        param = (~param + 1) & 0x07ffffff
        param = -param
    fp = param / float(1<<23)
    # print(fp)
    return fp


assert dec_5_23(bytes.fromhex('0f800000')) == -1.0
assert dec_5_23(bytes.fromhex('02000000')) == 4.0

class ADAD1701_SPI:

    def __init__(self):
        self.parameter_ram = b''
        self.program_ram = b''
        self.control_regs: dict[int, bytes] = {}
        self.verbose = False

    def on_packet(self, packet, mosi, miso):
        # print(f"{packet:10} {mosi.hex()}, {miso.hex()}")
        is_write = mosi[0] == 0
        addr = int.from_bytes(mosi[1:3])
        data = mosi[3:] if is_write else miso[3:]
        direction = {True: "write", False:"read"}[is_write]
        assert addr <= 0x0827
        if is_write:
            if addr >= 0x0800:
                if len(data) > 5:
                    print(f"Warning: overlong control register write to {addr:04x} data {data.hex()}")
                    return
            if addr == 0x0000:
                assert len(data) == 1024*4 # 1024*32 bits
                self.parameter_ram = data
            elif addr == 0x0400:
                assert len(data) == 1024*5 # 1024x40 bits
                self.program_ram = data
            elif addr >= 0x0800:
                self.control_regs[addr] = data
            else:
                print('Warning: ignoring random read/write')
        if self.verbose:
            print(f"{packet:10} {direction:6}  {addr:04x} sz={len(data):04} {data.hex()}")

    def print_decode(self):
        print("Parameter block:")
        for i in range(1024):
            fp = dec_5_23(param := self.parameter_ram[i*4:4+i*4])
            print(f'  {i:04}: {fp:14.10f}   (raw {param.hex()})')

        print("Program block:")
        for i in range(1024):
            instr = self.program_ram[i*5:5+i*5]
            ins = int.from_bytes(instr)
            desc = self.describe_instr(instr)
            print(f"  {ins:040b} {desc}")

        print("Control registers:")
        for addr, value in self.control_regs.items():
            print(f'  {addr:04x}: {value.hex()}')

    def describe_instr(self, bs):
        # 40 bits instr
        #   10 bits must be input parameter select, or output parameter select
        #
        if int.from_bytes(bs) == 1:
            return "NOP"
        return "?"

# architecture is described as:
#  * 28-bit × 28-bit multiplier with 56-bit accumulator for full double-precision processing

# Read Salae Logic spi trace file and apply to model
adad = ADAD1701_SPI()

with open('cpu-dsp-spi.txt', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    packet_id = '0'
    mosi_bs = bytearray(8000)
    mosi_i = 0
    miso_bs = bytearray(8000)
    miso_i = 0
    for row in reader:
        if row['Packet ID'] != packet_id:
            adad.on_packet(packet_id, mosi_bs[0:mosi_i], miso_bs[0:miso_i])
            miso_i = 0
            mosi_i = 0
        mosi_bs[mosi_i] = int(row['MOSI'], base=16)
        mosi_i += 1
        miso_bs[miso_i] = int(row['MISO'], base=16)
        miso_i += 1
        packet_id = row['Packet ID']

    adad.print_decode()

