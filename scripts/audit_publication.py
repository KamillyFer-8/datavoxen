"""Inventaria candidatos ao Git sem adicionar arquivos ou imprimir segredos."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    listed = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'], cwd=ROOT)
    names = sorted(set(listed.decode('utf-8').split('\0')) - {''})
    findings, binaries, broken = [], [], []
    patterns = {
        'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
        'github_token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b'),
        'aws_access_key': re.compile(r'\bAKIA[A-Z0-9]{16}\b'),
        'personal_windows_path': re.compile(r'C:[/\\]Users[/\\][^/\\\s]+', re.I),
    }
    for name in names:
        path=ROOT/name
        if not path.is_file(): continue
        content=path.read_bytes()
        if path.suffix.lower() in {'.png','.jpg','.pdf','.zip','.sqlite3'}:
            binaries.append({'path':name,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
            continue
        try: source=content.decode('utf-8-sig')
        except UnicodeDecodeError:
            findings.append({'path':name,'kind':'non_utf8_review'})
            continue
        for kind,pattern in patterns.items():
            if pattern.search(source): findings.append({'path':name,'kind':kind})
        if path.suffix=='.md':
            for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',source):
                target=target.split('#')[0]
                if not target or re.match(r'[a-z][a-z0-9+.-]*:',target,re.I): continue
                resolved=(path.parent/target).resolve()
                if not resolved.exists() or (resolved.is_file() and resolved.relative_to(ROOT).as_posix() not in names):
                    broken.append({'path':name,'target':target})
    report={'date':'2026-10-30','candidate_count':len(names),'files':names,'binary_files':binaries,'pattern_findings':findings,'broken_local_links':broken,'scope':'Padrões limitados; não é garantia de ausência de segredos ou autorização de direitos.'}
    target=ROOT/'docs/audit/publication-inventory.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'candidates':len(names),'binaries':len(binaries),'pattern_findings':findings,'broken_local_links':broken},ensure_ascii=False))
    if findings or broken: raise SystemExit(1)


if __name__=='__main__': main()
