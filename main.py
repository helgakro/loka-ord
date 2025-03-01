#!/usr/bin/python
import datetime
from pathlib import Path
import sys

from typing import Optional

import typer
from typing_extensions import Annotated

import lokaord

app = typer.Typer(
    chain=True,
    name=lokaord.Name,
    context_settings={'help_option_names': ['-h', '--help']},
    add_completion=False
)


def version(value: bool):
    if value:
        print('%s %s' % (lokaord.Name, lokaord.__version__))
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def common(
    version: Annotated[
        Optional[bool], typer.Option(
            '--version', '-v', callback=version, help='Print version and exit.'
        )
    ] = None,
    logger_name: Annotated[str, typer.Option('--logger-name', '-ln')] = lokaord.Name,
    log_directory: Annotated[
        Path, typer.Option(
            '--log-directory', '-ldir', help='Directory to write logs in. Should already exist.'
        )
    ] = './logs/',
    role: Annotated[lokaord.LoggerRoles, typer.Option('--role', '-r')] = 'cli'
):
    lokaord.Ts = datetime.datetime.now()
    if log_directory.match('logs') and not log_directory.exists():
        log_directory.mkdir()
    log_directory = log_directory.resolve()
    if not log_directory.exists():
        raise typer.BadParameter(f'Please ensure provided log-directory "{log_directory}" exists.')
    if not log_directory.is_dir():
        raise typer.BadParameter(f'Provided log-directory "{log_directory}" is not a directory.')
    lokaord.logman.init(logger_name, role=role, output_dir=log_directory)
    if len(sys.argv) <= 1:
        print('No commands provided. Try running with flag --help for info on available commands.')


@app.command('build-db', help='Import words from JSON datafiles to database.')
def build_db(
    rebuild: Annotated[Optional[bool], typer.Option('--rebuild', '-r')] = False,
    changes_only: Annotated[Optional[bool], typer.Option('--changes-only', '-ch')] = False
):
    if rebuild and changes_only:
        raise typer.BadParameter('build-db: --rebuild and --changes-only are mutually exclusive.')
    lokaord.build_db(rebuild, changes_only)


@app.command('backup-db', help='Create backup of current SQLite database file.')
def backup_db():
    lokaord.backup_db()


@app.command(help='Write words from database to JSON datafiles.')
def write_files(
    timestamp: Annotated[Optional[datetime.datetime], typer.Option('--timestamp', '-ts')] = None,
    time_offset: Annotated[Optional[lokaord.TimeOffset], typer.Option('--time-offset', '-to')] = None,
    this_run: Annotated[Optional[bool], typer.Option('--this-run', '-tr')] = False
):
    if timestamp is not None and time_offset is not None:
        logman.warning('Both timestamp and time_offset specified, using timestamp.')
    ts = timestamp
    if ts is None and time_offset is not None:
        ts = lokaord.get_offset_time(time_offset)
    if this_run is True:
        if ts is not None:
            logman.warning('Overriding timestamp with this_run.')
        ts = lokaord.Ts
    lokaord.write_files(ts)


@app.command(help='Build word search.')
def build_sight():
    lokaord.build_sight()


@app.command(help='Search for a single word in sight file.')
def search(word: str):
    if word == '':
        raise typer.BadParameter('Word can\'t be empty string.')
    lokaord.search(word)

@app.command(help='Search for words in a sentence in sight file.')
def scan_sentence(sentence: str):
    if sentence == '':
        raise typer.BadParameter('Sentence can\'t be empty string.')
    lokaord.scan_sentence(sentence)


@app.command(help='Short for the "scan-sentence" command.')
def ss(sentence: str):
    scan_sentence(sentence)


@app.command(help='Print database word count data in JSON string.')
def stats():
    lokaord.get_stats()


@app.command(help='Print database word count in Markdown table.')
def md_stats():
    lokaord.get_md_stats()


@app.command(help='Initialize lokaord (same as: "build-db write-files build-sight md-stats").')
def init(rebuild: Annotated[Optional[bool], typer.Option('--rebuild', '-r')] = False):
    lokaord.build_db(rebuild)
    lokaord.write_files()
    lokaord.build_sight()
    lokaord.get_md_stats()


@app.command(help='Update lokaord (same as: "build-db -ch write-files -tr build-sight md-stats").')
def update():
    lokaord.build_db(changes_only=True)
    lokaord.write_files(lokaord.Ts)
    lokaord.build_sight()
    lokaord.get_md_stats()


@app.command(help='Add word CLI.')
def add_word():
    lokaord.logman.error('todo: fix this command')
    raise typer.Exit()
    lokaord.add_word()


@app.command(help='Run fiddle.')
def run_fiddle():
    lokaord.run_fiddle()


if __name__ == '__main__':
    app(prog_name=lokaord.Name)
