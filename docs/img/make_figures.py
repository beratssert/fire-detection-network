"""Draw the documentation figures (architecture, data model) as PNG into this folder.

Usage (from the repository root, any Python with matplotlib):
    python docs/img/make_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

OUT = Path(__file__).resolve().parent
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
NAVY, GREY, LIGHT, ORANGE = "#1F3B73", "#6B7280", "#EEF2F8", "#C2410C"


def box(ax, x, y, w, h, title, lines, tsize=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=LIGHT, ec=NAVY, lw=1.1))
    ax.text(x + w / 2, y + h - 0.16, title, ha="center", va="top", fontsize=tsize, weight="bold", color=NAVY)
    for i, line in enumerate(lines):
        ax.text(x + w / 2, y + h - 0.52 - i * 0.27, line, ha="center", va="top", fontsize=7.2, color="#111827")


def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops={"arrowstyle": "-|>", "color": NAVY, "lw": 1.2})


def architecture():
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 7.55)
    ax.axis("off")
    ax.add_patch(Rectangle((0.05, 2.0), 10.95, 5.2, fill=False, ec="#CBD5E1", lw=0.8, ls="--"))
    ax.add_patch(Rectangle((11.25, 2.0), 4.7, 5.2, fill=False, ec="#CBD5E1", lw=0.8, ls="--"))
    ax.text(0.15, 7.45, "Sensor network: 868 MHz LoRa", fontsize=7.3, color=GREY, va="top")
    ax.text(11.35, 7.45, "Laptop", fontsize=7.3, color=GREY, va="top")
    box(
        ax,
        0.3,
        3.55,
        3.2,
        3.35,
        "Leaf node",
        [
            "Wio-E5 (STM32WLE5JC):",
            "MCU + radio + AES",
            "T/RH sensor",
            "gas/VOC sensor",
            "battery",
            "role set by configuration",
        ],
    )
    box(
        ax,
        4.0,
        3.55,
        3.0,
        3.35,
        "Relay node",
        ["same board", "same firmware", "role = relay", "forwards frames", "hop count + 1", "sends own readings"],
    )
    box(
        ax,
        7.5,
        3.55,
        3.2,
        3.35,
        "Gateway node",
        [
            "same board",
            "role = gateway",
            "receives frames",
            "adds RSSI and SNR",
            "checks tag and counter",
            "sync beacon",
        ],
    )
    box(ax, 11.5, 5.05, 4.2, 1.85, "Frame logger", ["Python, serial port", "one row per frame"])
    box(ax, 11.5, 2.3, 4.2, 2.25, "Analysis", ["statistics, plots", "comparison with the", "preliminary model"])
    arrow(ax, 3.5, 5.2, 4.0, 5.2)
    arrow(ax, 7.0, 5.2, 7.5, 5.2)
    arrow(ax, 10.7, 6.0, 11.5, 6.0)
    ax.text(11.1, 6.12, "USB", ha="center", fontsize=6.6, color=NAVY)
    arrow(ax, 13.6, 5.05, 13.6, 4.55)
    ax.text(13.75, 4.8, "log files", fontsize=6.6, color=NAVY, va="center")
    ax.text(5.5, 2.95, "Alarms and hourly heartbeats over at least two hops,", ha="center", fontsize=6.8, color=ORANGE)
    ax.text(
        5.5,
        2.45,
        "in synchronous listen slots; 868.0-868.6 MHz, 1 % duty cycle.",
        ha="center",
        fontsize=6.8,
        color=ORANGE,
    )
    y0, h = 0.35, 0.75
    x, unit = 0.3, 15.4 / 27
    for name, size, col in [
        ("header 7 B", 7, "#DBEAFE"),
        ("data 12 B", 12, "#DCFCE7"),
        ("tag 8 B (AES-256-CCM)", 8, "#FFEDD5"),
    ]:
        ax.add_patch(Rectangle((x, y0), size * unit, h, fc=col, ec=GREY, lw=0.7))
        ax.text(x + size * unit / 2, y0 + h / 2, name, ha="center", va="center", fontsize=6.5)
        x += size * unit
    ax.text(
        0.3,
        y0 + h + 0.15,
        "Frame (27 B); header = node ID 2 B + epoch low byte 1 B + counter 4 B",
        fontsize=7.2,
        color=NAVY,
        weight="bold",
    )
    fig.tight_layout(pad=0.2)
    fig.savefig(OUT / "fig_architecture.png", dpi=220)
    plt.close(fig)


def entity(ax, x, y, w, name, fields):
    h = 0.42 + 0.3 * len(fields)
    ax.add_patch(Rectangle((x, y - h), w, h, fc="white", ec=NAVY, lw=1.0))
    ax.add_patch(Rectangle((x, y - 0.42), w, 0.42, fc=LIGHT, ec=NAVY, lw=1.0))
    ax.text(x + w / 2, y - 0.21, name, ha="center", va="center", weight="bold", color=NAVY, fontsize=8)
    for i, f in enumerate(fields):
        ax.text(
            x + 0.1, y - 0.6 - i * 0.3, f, va="center", fontsize=6.9, weight="bold" if f.endswith("(PK)") else "normal"
        )


def data_model():
    fig, ax = plt.subplots(figsize=(7.2, 1.85))
    ax.set_xlim(0, 14.4)
    ax.set_ylim(2.85, 6.5)
    ax.axis("off")
    entity(
        ax,
        0.2,
        6.4,
        3.9,
        "TestRun",
        [
            "run_id (PK)",
            "date, start/end time",
            "site (campus / forest)",
            "placement (trunk 2.5 m / ground)",
            "spreading factor, TX power",
            "distance or topology",
            "firmware version, notes",
        ],
    )
    entity(
        ax,
        10.3,
        6.4,
        3.9,
        "Node",
        [
            "node_id (PK)",
            "role (leaf / relay / gateway)",
            "parent_id (fixed routes)",
            "key_id (key derived from node_id)",
            "board serial",
        ],
    )
    entity(
        ax,
        5.0,
        6.4,
        4.4,
        "Frame",
        [
            "frame_id (PK)",
            "run_id (FK), node_id (FK)",
            "rx_time (laptop clock)",
            "epoch, counter",
            "msg_type (data / alarm / heartbeat)",
            "hop_count",
            "temperature, humidity, gas_resistance",
            "battery_voltage",
            "rssi, snr (at gateway)",
            "tag_ok, reject_reason",
        ],
    )
    for x1, x2, a, b in [(4.1, 5.0, "1", "N"), (10.3, 9.4, "1", "N")]:
        ax.plot([x1, x2], [5.6, 5.6], color=NAVY, lw=1.0)
        ax.text(x1 + (0.12 if x1 < x2 else -0.12), 5.72, a, ha="center", fontsize=7.5, color=NAVY)
        ax.text(x2 + (-0.12 if x1 < x2 else 0.12), 5.72, b, ha="center", fontsize=7.5, color=NAVY)
    fig.tight_layout(pad=0.2)
    fig.savefig(OUT / "fig_datamodel.png", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    architecture()
    data_model()
