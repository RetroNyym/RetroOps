"""Satıcı için lisans anahtarı üretimi.

Kullanım:
    python araclar/lisans_uret.py 2027-10-05              # bu bilgisayar için
    python araclar/lisans_uret.py 2027-10-05 a1b2c3d4e5f6 # müşteri makinesi için

Müşterinin makine kimliğini programdan öğrenebilirsiniz:
Panel → Lisans → "Makine kimliği".
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ops.lisans import anahtar_uret, makine_id  # noqa: E402


def main() -> None:
    if len(sys.argv) < 2 or len(sys.argv[1]) != 10 or sys.argv[1][4] != "-":
        print("Kullanım: python araclar/lisans_uret.py YYYY-AA-GG [makine_id]")
        print("Bu bilgisayarın makine kimliği:", makine_id())
        raise SystemExit(1)
    bitis = sys.argv[1]
    makine = sys.argv[2] if len(sys.argv) > 2 else None
    print(anahtar_uret(bitis, makine))


if __name__ == "__main__":
    main()
