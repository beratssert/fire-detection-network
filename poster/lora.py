"""LoRa time on air (Semtech AN1200.13 formula). Shared by models.py, latency.py and energy code."""
import math
import params

def toa_ms(sf, pl_bytes, bw=params.LORA_BW_HZ, cr=params.LORA_CR, n_pre=params.LORA_N_PRE,
           crc=params.LORA_CRC, ih=params.LORA_IH):
    de = 1 if sf >= params.LORA_DE_MIN_SF else 0
    ts = (2 ** sf) / bw
    t_pre = (n_pre + 4.25) * ts
    num = 8 * pl_bytes - 4 * sf + 28 + 16 * crc - 20 * ih
    n_pay = 8 + max(math.ceil(num / (4 * (sf - 2 * de))) * (cr + 4), 0)
    return 1e3 * (t_pre + n_pay * ts)
