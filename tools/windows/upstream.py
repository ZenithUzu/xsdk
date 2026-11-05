"""Merge original SDK source into a private Windows snapshot before touching the live SDK."""
import hashlib
import json
from pathlib import Path
import re
import time
import uuid

from source_update import overlay

UPSTREAM_REPOSITORY = 'https://github.com/xenosworks/xsdk.git'
UPSTREAM_BRANCH = 'main'


def resolve_document_conflicts(snapshot, names, execute, git):
    allowed = {'README.md', 'CODE_GUIDELINES.md', 'docs/HARDWARE.md'}
    if not names or set(names) - allowed:
        raise ValueError('Upstream conflicts need review; live SDK not changed: ' + ', '.join(names))
    for name in names:
        path = Path(snapshot) / name
        if name == 'README.md':
            execute([git, '-C', snapshot, 'checkout', '--ours', '--', name])
        else:
            text = path.read_text(encoding='utf-8')
            text, count = re.subn(r'^<<<<<<<[^\n]*\n(.*?)^=======\n(.*?)^>>>>>>>[^\n]*\n',
                                  lambda match: match[1] + match[2], text, flags=re.M | re.S)
            if not count or any(marker in text for marker in ('<<<<<<<', '>>>>>>>', '|||||||')):
                raise ValueError('Document conflict needs review: ' + str(path))
            path.write_text(text, encoding='utf-8')
        execute([git, '-C', snapshot, 'add', '--', name])


def integrate_original(git, target, windows_url, windows_branch, work, execute,
                       upstream_url=UPSTREAM_REPOSITORY, upstream_branch=UPSTREAM_BRANCH):
    target, work = Path(target).resolve(), Path(work).resolve()
    if work.is_relative_to(target):
        raise ValueError('Choose a work folder outside the SDK source folder.')
    if not (target / 'tools/windows/run.sh').is_file():
        raise ValueError('Prepare the Windows SDK first, then integrate original updates.')
    identity = hashlib.sha256((windows_url + '#' + windows_branch).encode()).hexdigest()[:12]
    cache = work / 'upstream-cache' / ('windows-' + identity)
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        execute([git, 'clone', '--branch', windows_branch, '--', windows_url, cache])
    else:
        if execute([git, '-C', cache, 'status', '--porcelain'], capture=True):
            raise ValueError('The upstream cache has local edits; choose another work folder.')
        execute([git, '-C', cache, 'fetch', 'origin', windows_branch])
        execute([git, '-C', cache, 'merge', '--ff-only', 'refs/remotes/origin/' + windows_branch])
    windows_revision = execute([git, '-C', cache, 'rev-parse', 'HEAD'], capture=True)
    execute([git, '-C', cache, 'fetch', '--no-tags', upstream_url, upstream_branch])
    upstream_revision = execute([git, '-C', cache, 'rev-parse', 'FETCH_HEAD'], capture=True)
    snapshot = work / 'upstream-merges' / (time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8])
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    execute([git, '-C', cache, 'worktree', 'add', '--detach', snapshot, windows_revision])
    print('Original SDK merge is prepared here before applying: ' + str(snapshot), flush=True)
    try:
        execute([git, '-c', 'user.name=xSDK local updater', '-c', 'user.email=xsdk-updater@localhost',
                 '-c', 'merge.conflictStyle=merge', '-C', snapshot, 'merge', '--no-ff', '--no-commit', upstream_revision])
    except Exception as error:
        # A failed merge stays in the private worktree for inspection. Never resolve runtime code blindly.
        conflicts = execute([git, '-C', snapshot, 'diff', '--name-only', '--diff-filter=U'], capture=True).splitlines()
        if not conflicts:
            raise ValueError('Original SDK merge failed; live SDK unchanged. Inspect ' + str(snapshot)) from error
        resolve_document_conflicts(snapshot, conflicts, execute, git)
    remaining = execute([git, '-C', snapshot, 'diff', '--name-only', '--diff-filter=U'], capture=True)
    if remaining:
        raise ValueError('Unresolved upstream conflicts; live SDK unchanged: ' + remaining)
    if not (snapshot / 'tools/windows/run.sh').is_file() or not (snapshot / 'cmake/xsdk.cmake').is_file():
        raise ValueError('Merged source lacks Windows compatibility; live SDK unchanged.')
    original_readme = execute([git, '-C', cache, 'show', upstream_revision + ':README.md'], capture=True)
    (snapshot / 'README-UPSTREAM.md').write_text(original_readme + '\n', encoding='utf-8')
    state = {'schema': 1, 'windows_revision': windows_revision, 'upstream_revision': upstream_revision,
             'upstream_repository': upstream_url, 'upstream_branch': upstream_branch}
    (snapshot / '.xsdk-upstream.json').write_text(json.dumps(state, indent=2), encoding='utf-8')
    execute([git, '-C', snapshot, 'add', '--', 'README-UPSTREAM.md', '.xsdk-upstream.json'])
    names = execute([git, '-C', snapshot, 'ls-files', '-z'], capture=True).split('\0')
    backup = work / 'source-backups' / ('upstream-' + time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8])
    revision = windows_revision + '+' + upstream_revision
    overlay(snapshot, target, [name for name in names if name], backup, revision)
    print('Original SDK integrated: ' + upstream_revision + '; Windows source: ' + windows_revision, flush=True)
    # Only remove the private worktree we just created, never the live source or a user checkout.
    if snapshot.resolve().is_relative_to((work / 'upstream-merges').resolve()):
        execute([git, '-C', cache, 'worktree', 'remove', '--force', snapshot])
    return state
