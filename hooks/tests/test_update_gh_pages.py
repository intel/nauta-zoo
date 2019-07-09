import json
import os

import pytest

from hooks.update_gh_pages import get_template_dirs, pack_template_dirs, parse_template_metadata, \
    get_templates_metadata, prepare_templates_json


def test_get_template_dirs():

    repository_filenames = [
    'tf-inference-batch/charts/values.yaml',
    'tf-inference-batch/tf_serving_nauta.sh',
    'tf-inference-stream/Dockerfile',
    'tf-inference-stream/charts/.helmignore',
    'tf-inference-stream/charts/Chart.yaml',
    'tf-inference-stream/charts/values.yaml',
    'tf-inference-stream/tf_serving_nauta.sh',
    'tf-training-tfjob-py2/Dockerfile',
    'tf-training-tfjob-py2/charts/.helmignore',
    'tf-training-tfjob-py2/charts/Chart.yaml',
    ]

    assert get_template_dirs(repository_filenames) == {'tf-inference-batch', 'tf-inference-stream',
                                                       'tf-training-tfjob-py2'}


def test_pack_template_dirs(tmpdir):
    root_test_dir = tmpdir.mkdir('packs')
    docs_dir = root_test_dir.mkdir('docs')
    test_directories = [root_test_dir.mkdir('pack-1'), root_test_dir.mkdir('pack-2'), root_test_dir.mkdir('pack-3')]
    for i, test_dir in enumerate(test_directories):
        chart_file = test_dir.join('Chart.yaml')
        chart_file.write(f'name: pack-{i}')

    pack_template_dirs(repo_path=root_test_dir.strpath, template_dirs={'pack-1', 'pack-2', 'pack-3'})

    assert all(pack in os.listdir(docs_dir.strpath) for pack in ['pack-1.tar.gz', 'pack-2.tar.gz', 'pack-3.tar.gz'])


def test_parse_template_metadata(tmpdir):
    chart_yaml = tmpdir.join('Chart.yaml')
    chart_yaml.write('''
    name: multinode-tf-training-tfjob-py2
    apiVersion: v1
    description: Tensorflow training chart for Kubernetes multi node
    version: 0.1.0
    ''')

    result = parse_template_metadata(chart_yaml.strpath, metadata_fields={'version', 'description'})

    assert result == {'version': '0.1.0', 'description': 'Tensorflow training chart for Kubernetes multi node'}


def test_parse_template_metadata_missing_field(tmpdir):
    chart_yaml = tmpdir.join('Chart.yaml')
    chart_yaml.write('''
        name: multinode-tf-training-tfjob-py2
        apiVersion: v1
        description: Tensorflow training chart for Kubernetes multi node
        ''')

    with pytest.raises(ValueError):
        parse_template_metadata(chart_yaml.strpath, metadata_fields={'version', 'description'})


def test_get_templates_metadata(tmpdir):
    templates_dir = tmpdir.mkdir('templates')
    test_templates = [templates_dir.mkdir('pack-1'), templates_dir.mkdir('pack-2'), templates_dir.mkdir('pack-3')]

    for i, test_dir in enumerate(test_templates):
        chart_yaml = test_dir.mkdir('charts').join('Chart.yaml')
        chart_yaml.write(f'''
                name: pack-{i}
                apiVersion: v1
                version: 1.0
                description: Test pack #{i}
                ''')

    result = get_templates_metadata(repo_path=templates_dir.strpath, template_dirs={'pack-1', 'pack-2', 'pack-3'})
    assert result == {'pack-1': {'version': '1.0', 'description': 'Test pack #0'},
                      'pack-2': {'version': '1.0', 'description': 'Test pack #1'},
                      'pack-3': {'version': '1.0', 'description': 'Test pack #2'},
                      }


def test_get_templates_metadata_missing_chart(tmpdir):
    templates_dir = tmpdir.mkdir('templates')
    test_templates = [templates_dir.mkdir('pack-1'), templates_dir.mkdir('pack-2'), templates_dir.mkdir('pack-3')]

    for i, test_dir in enumerate(test_templates[:-1]):
        chart_yaml = test_dir.mkdir('charts').join('Chart.yaml')
        chart_yaml.write(f'''
                name: pack-{i}
                apiVersion: v1
                version: 1.0
                description: Test pack #{i}
                ''')

    with pytest.raises(OSError):
        get_templates_metadata(repo_path=templates_dir.strpath, template_dirs={'pack-1', 'pack-2', 'pack-3'})


def test_prepare_templates_json(tmpdir):
    root_test_dir = tmpdir.mkdir('packs')
    docs_dir = root_test_dir.mkdir('docs')

    prepare_templates_json(repo_path=root_test_dir.strpath, template_dirs={'pack-1', 'pack-2'},
                           templates_metadata={'pack-1': {'version': '1.0', 'description': 'Test pack #0'},
                                               'pack-2': {'version': '1.0', 'description': 'Test pack #1'}})

    assert os.path.isfile(docs_dir.join('index.json').strpath)

    with open(docs_dir.join('index.json').strpath, mode='r') as json_file:
        assert json.load(json_file) == {'templates': [
            {'name': 'pack-1', 'version': '1.0', 'description': 'Test pack #0', 'url': 'pack-1.tar.gz'},
            {'name': 'pack-2', 'version': '1.0', 'description': 'Test pack #1', 'url': 'pack-2.tar.gz'}
        ]}
