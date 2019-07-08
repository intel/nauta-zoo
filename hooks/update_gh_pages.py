#!/bin/python3
# Pre commit hook script

import json
import subprocess
from typing import Sequence, Set, Dict


IGNORED_DIRS = {'docs', 'hooks'}


def get_repo_path() -> str:
    return subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], encoding='utf-8').strip()


def get_repository_filenames(repo_path: str):
    return subprocess.check_output(['git', 'ls-files'], encoding='utf-8', cwd=repo_path).split('\n')


def get_template_dirs(repository_filenames: Sequence[str]) -> Set[str]:
    template_dirs = set()
    for filename in repository_filenames:
        dir_name = filename.split('/')[0]
        if '/' in filename and dir_name not in IGNORED_DIRS:
            template_dirs.add(f'{dir_name}')

    return template_dirs


def pack_template_dirs(repo_path: str, template_dirs: Set[str]):
    for template_dir in template_dirs:
        subprocess.check_call(['tar', '-czf', f'{repo_path}/docs/{template_dir}.tar.gz', f'{repo_path}/{template_dir}'])

# TODO: Calculate packs checksums


def parse_template_metadata(chart_yaml_path: str, metadata_fields: Set[str]) -> Dict[str, str]:
    template_metadata = {}
    with open(chart_yaml_path, mode='r', encoding='utf-8') as chart_file:
        for line in chart_file.readlines():
            for metadata_field in metadata_fields:
                if f'{metadata_field}:' in line:
                    template_metadata[metadata_field] = line.split(':')[-1].strip()

    for metadata_field in metadata_fields:
    if not template_metadata.get(metadata_field):
        raise ValueError(f'Failed to get {metadata_field} field from {chart_yaml_path}')

    return template_metadata


def get_templates_metadata(repo_path: str, template_dirs: Set[str]) -> Dict[str, Dict]:
    templates_metadata = {}
    metadata_fields = {'version', 'description'}
    for template_dir in template_dirs:
        # TODO: handle errors properly
        try:
            templates_metadata[template_dir] = parse_template_metadata(f'{repo_path}/{template_dir}/charts/Chart.yaml',
                                                                       metadata_fields=metadata_fields)
        except (OSError, ValueError, KeyError):
            print(f'Failed to load metadata of {template_dir} template. Make sure that Chart.yaml file exists '
                  f'and contains following fields: {metadata_fields}')
            raise

    return templates_metadata


def prepare_templates_json(repo_path: str, template_dirs: Set[str], templates_metadata: Dict[str, Dict]):
    zoo_manifest = {
        'templates': [{'name': template_dir,
                       'url': f'{template_dir}.tar.gz',
                       'version': templates_metadata[template_dir]['version'],
                       'description': templates_metadata[template_dir]['description']}
                      for template_dir in template_dirs],
    }
    with open(f'{repo_path}/docs/index.json', mode='w+', encoding='utf-8') as manifest_file:
        json.dump(zoo_manifest, manifest_file, indent=2)


def main(argv=None):
    repo_path = get_repo_path()
    filenames = get_repository_filenames(repo_path)
    template_dirs = get_template_dirs(filenames)
    print(template_dirs)
    pack_template_dirs(repo_path, template_dirs)
    templates_metadata = get_templates_metadata(repo_path, template_dirs)
    prepare_templates_json(repo_path, template_dirs, templates_metadata)


if __name__ == '__main__':
    main()
