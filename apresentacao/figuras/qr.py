# Gera o QR code do slide final (link das referências). Uso: python3 qr.py [url] [saida.png]
import sys, segno
URL = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/brunomoraesdubois-bit/Bruno/blob/claude/aminas-vasoativas-project-w6qsns/apresentacao/referencias.md"
saida = sys.argv[2] if len(sys.argv) > 2 else "../deck/assets/qr-referencias.png"
qr = segno.make(URL, error="m")
qr.save(saida, scale=20, border=2, dark="#1b2a3a", light="#f5f3ee")
print(qr.version, qr.error, saida)
