"""Executa o núcleo original e os checks originais, sem renderizadores legados."""
import ast
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/references/original'


def original_namespace():
    source = (SOURCE / 'modelo/motor_original.py').read_text(encoding='utf-8')
    # O arquivo original mistura simulação e geração de documentos em /mnt/data.
    # Executamos as mesmas instruções numéricas, sem I/O nem bibliotecas de PDF.
    prefix = source[source.index('CAT='):source.index('# Additional observed market truth')]
    ns = {'math': math}
    exec(compile(prefix, 'motor_original.py:nucleo', 'exec'), ns)
    return ns


def audit():
    import pandas as pd
    ns = original_namespace()
    script = (SOURCE / 'auditoria/rotina_auditoria.py').read_text(encoding='utf-8')
    script = script[:script.index('results=[]')]
    script = script[script.index('root='):]
    start = script.index('# import engine via prefix')
    end = script.index('for st in', start)
    script = script[:start] + 'ns=original\n' + script[end:]
    script = script.replace("root=pathlib.Path('/mnt/data'); work=root/'datavoxen_revisado'", 'root=source; work=root/"modelo"')
    import pathlib
    audit_ns = {'pathlib': pathlib, 'pd': pd, 'json': json, 'math': math,
                'source': SOURCE, 'original': ns}
    exec(compile(script, 'rotina_auditoria.py:checks_originais', 'exec'), audit_ns)
    expected = {f'{st}/{sc}': ns['tot'](data, 'flow') for (st, sc), data in ns['rows'].items()}
    target = ROOT / 'docs/methodology'
    target.mkdir(parents=True, exist_ok=True)
    regression = target / 'regression.json'
    if regression.exists() and json.loads(regression.read_text(encoding='utf-8')) != expected:
        raise AssertionError('O motor original diverge da regressão preservada; investigue a fonte antes de atualizar.')
    if not regression.exists():
        regression.write_text(json.dumps(expected, indent=2), encoding='utf-8')
    (target / 'original-audit.json').write_text(json.dumps(audit_ns['checks'], indent=2), encoding='utf-8')
    print(f"{len(audit_ns['checks'])} checks originais aprovados")
    print(json.dumps(expected, indent=2))


if __name__ == '__main__':
    audit()
