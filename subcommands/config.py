import click
import os


@click.command()
@click.pass_context
def config(cntx):
    x=5
    os.popen("export MARKO=321") # izgleda ne radi