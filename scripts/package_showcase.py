"""Package static Sites output from the exact committed source tree."""
from pathlib import Path
import io, subprocess, tarfile
root = Path(__file__).resolve().parents[1]
raw = subprocess.check_output(['git','archive','--format=tar','HEAD','.openai/hosting.json','site'],cwd=root)
output=root/'docs/presentation/sites-deploy.tar'
with tarfile.open(fileobj=io.BytesIO(raw)) as source, tarfile.open(output,'w') as target:
    for member in source.getmembers():
        if not member.isfile():
            continue
        payload=source.extractfile(member)
        if member.name.startswith('site/'):
            member.name='dist/'+member.name[5:]
        target.addfile(member,payload)
with tarfile.open(output) as check:
    assert 'dist/index.html' in check.getnames()
    assert '.openai/hosting.json' in check.getnames()
print(output)
