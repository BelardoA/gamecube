import os
import shutil

import click
import pandas as pd
from rich.progress import (
    Progress,
    BarColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    TextColumn,
)

from datarow import DataRow
from filesremaining import FilesRemainingColumn


SOURCE_GAMES_DIR = "D:\\GC Nkits"


@click.group(name="move")
def move():
    pass

@move.command(name="games")
@click.option(
    "--workbook",
    "-w",
    required=True,
    type=click.Path(exists=True),
    help="Path to the games workbook"
)
@click.option(
    "--destination",
    "-d",
    required=True,
    type=click.Path(exists=True),
    help="Path to the destination folder"
)
def main(workbook: str, destination: str):
    """
    Import games from a workbook and move them to a destination folder
    """
    move_games(workbook, destination)


def move_games(workbook: str, destination: str) -> None:
    """
    Parse the workbook, validate the selected games will fit on the destination,
    copy files with a progress bar, and validate they are on the destination

    :param str workbook: Path to the games workbook
    :param str destination: Path to the destination folder
    :return: None
    """
    # validate selected games will fit
    # copy files with progress bar
    # validate they are on the destination
    df = pd.read_excel(workbook)
    data = df.to_dict(orient="records")
    all_games = [DataRow(**row) for row in data]
    games = [game for game in all_games if game.include]
    total_space = sum(game.size for game in games)
    click.echo(f"Total space required: {total_space:.2f} GB")
    free_space = _get_available_space(destination, games)
    if total_space > free_space:
        click.echo("Not enough space on the destination drive. Please free up some space and try again.")
        return


    with Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total} files"),
        FilesRemainingColumn(),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task_id = progress.add_task("Moving games", total=len(games))
        missing_games = []
        existing_games = []
        for game in games:
            source_path = os.path.join(SOURCE_GAMES_DIR, game.game_name)
            destination_path = os.path.join(destination, game.game_name)
            if os.path.exists(destination_path):
                existing_games.append(game)
                progress.advance(task_id)
                continue
            if not os.path.exists(source_path):
                missing_games.append(game)
                # still advance so progress reflects attempted file
                progress.advance(task_id)
                continue
            shutil.copy2(source_path, destination_path)
            # advance whether included or not so numbers match total
            progress.advance(task_id)
    if missing_games:
        click.echo("The following games were marked for inclusion but were not found in the source directory:")
        for game in missing_games:
            click.echo(f"\t{game.game_name}")
    if existing_games:
        with click.open_file("existing_games.txt", "w") as f:
            for game in existing_games:
                click.echo(f"\t{game.game_name}")
                f.write(f"{game.game_name}\n")
        click.echo(
            f"Skipped {len(existing_games)} games that already exist in the destination directory, details written to existing_games.txt"
        )

def _get_available_space(destination: str, games: list) -> float:
    """
    Get the available space on the destination drive in GB

    :param str destination: Path to the destination folder
    :param list games: List of games to be moved, deducts their total size from the available
        space to give a more accurate estimate of whether they will fit
    :return: Available space in GB
    :rtype: float
    """
    if not os.path.exists(destination):
        raise ValueError(f"Destination path does not exist: {destination}")
    total, used, free = shutil.disk_usage(destination)
    click.echo("Disk usage for destination drive:")
    click.echo(f"\tTotal space: {total / (1024 ** 3):.2f} GB")
    click.echo(f"\tUsed space: {used / (1024 ** 3):.2f} GB")
    click.echo(f"\tFree space: {free / (1024 ** 3):.2f} GB")
    current_games = [game for game in games if os.path.exists(os.path.join(destination, game.game_name))]
    free = free / (1024 ** 3)  # convert to GB
    free += sum(game.size for game in current_games)
    return free

if __name__ == "__main__":
    # move()
    # For testing purposes, we can call the main function directly with hardcoded values
    move_games(workbook="64GB GameCube Game Selection.xlsx", destination="F:\GAMES")