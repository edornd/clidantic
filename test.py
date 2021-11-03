import click


@click.group()
def cli1():
    pass


@cli1.command()
def cmd1():
    """Command on cli1"""


@click.group()
def cli2():
    pass


@cli2.command()
def cmd2():
    """Command on cli2"""


cli = click.CommandCollection(sources=[cli1, cli2])

if __name__ == '__main__':
    cli()
