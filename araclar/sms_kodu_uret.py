"""Satıcı için SMS entegrasyon kodu üretimi.

Kullanım:
    python araclar/sms_kodu_uret.py                # bu bilgisayar için
    python araclar/sms_kodu_uret.py a1b2c3d4e5f6    # müşteri makinesi için

Müşterinin makine kimliğini programdan öğrenebilirsiniz:
Panel → SMS sekmesindeki makine kimliği rozeti.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ops.lisans import makine_id  # noqa: E402
from ops.sms import kod_uret  # noqa: E402


def main() -> None:
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and
                             not (sys.argv[1].isalnum() and
                                  4 <= len(sys.argv[1]) <= 64)):
        print("Kullanım: python araclar/sms_kodu_uret.py [makine_id]")
        print("Bu bilgisayarın makine kimliği:", makine_id())
        raise SystemExit(1)
    makine = sys.argv[1] if len(sys.argv) == 2 else None
    print(kod_uret(makine))


if __name__ == "__main__":
    main()
