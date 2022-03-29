import logging
from functools import update_wrapper
from pathlib import Path
from typing import List

import click
from click.core import Context
from shutterbug.application import (get_feature_calculators, get_graph_builder,
                                    get_photometer, initialize_application,
                                    make_dataset, make_file_loader,
                                    make_reader_writer)
from shutterbug.data_nodes import (CSVSaveNode, DatasetLeaf, DatasetNode,
                                   GraphSaveNode, StoreNode)
from shutterbug.process_nodes import DifferentialNode, VariabilityNode
from shutterbug.ux.progress_bars import ProgressBarManager


def processor(func):
    def new_func(*args, **kwargs):
        def processor(stream):
            return func(stream, *args, **kwargs)

        return processor

    return update_wrapper(new_func, func)


def generator(func):
    @processor
    def new_func(stream, *args, **kwargs):
        yield from stream
        yield from func(*args, **kwargs)

    return update_wrapper(new_func, func)


@click.group(chain=True, invoke_without_command=True)
@click.option("-d", "--debug", is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def cli(context: Context, debug: bool):
    config, engine = initialize_application(debug=debug)
    context.obj = {}
    context.obj["pbar_manager"] = ProgressBarManager()
    context.obj["config"] = config
    context.obj["database"] = engine


@cli.result_callback()
def process_commands(processors, *args, **kwargs):

    stream = ()

    for processor in processors:
        stream = processor(stream)
    logging.debug("Finished callbacks, starting execution")
    for node in stream:
        for _ in node.execute():
            pass
    logging.debug("Execution finished")


@cli.command("load")
@click.option(
    "-f",
    "--file",
    "files",
    multiple=True,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, path_type=Path
    ),
    help="Datasets to load",
)
@click.pass_context
@generator
def load(context: Context, files: List[Path]):
    config = context.obj["config"]
    engine = context.obj["database"]
    mag_limit = config.photometry["magnitude_limit"]
    distance_limit = config.photometry["distance_limit"]
    for f in files:
        logging.debug(f"Loading file: {f.name}")
        f_input = make_file_loader(f)
        db_reader, db_writer = next(
            make_reader_writer(
                engine=engine,
                dataset_name=f.name,
                magnitude_limit=mag_limit,
                distance_limit=distance_limit,
            )
        )
        StoreNode(f_input, db_writer).execute()
        dataset = make_dataset(dataset_name=f.name, reader=db_reader, writer=db_writer)
        yield DatasetLeaf(dataset)


@cli.command("process")
@click.option(
    "-i",
    "--iterations",
    "iterations",
    help="Number of differential/detection iterations",
    type=click.IntRange(min=1, max=3, clamp=True),
)
@click.pass_context
@processor
def process(nodes: List[DatasetNode], context: Context, iterations: int):
    variability_threshold = context.obj["config"].variability["threshold"]
    feature_calculators = get_feature_calculators()
    photometer = get_photometer()
    logging.info(f"Adding process nodes for {iterations} iterations to node tree")
    for node in nodes:
        for _ in range(iterations):
            node = DifferentialNode(node, photometer)
            node = VariabilityNode(node, feature_calculators, variability_threshold)
        yield node


@cli.command("save")
@click.option("-o", "--out-folder", type=click.Path())
@click.option("-g", "--graph", type=click.BOOL, is_flag=True, default=False)
@click.option("-c", "--csv", type=click.BOOL, is_flag=True, default=False)
@click.option(
    "-v" "--variable_only", "variable", type=click.BOOL, is_flag=True, default=False
)
@click.pass_context
@processor
def save(
    nodes: List[DatasetNode],
    context: Context,
    out_folder: Path,
    graph: bool,
    csv: bool,
    variable: bool,
):
    if out_folder is None:
        out_folder = context.obj["config"].data["output_folder"]
    graph_builder = get_graph_builder()
    for node in nodes:
        if graph:
            logging.info(f"Adding graph saving to node tree")
            node = GraphSaveNode(
                output_location=out_folder,
                only_variable=variable,
                datasets=node,
                graph_builder=graph_builder,
            )
        if csv:
            logging.info(f"Adding csv saving to node tree")
            node = CSVSaveNode(
                output_location=out_folder, only_variable=variable, datasets=node
            )
        yield node
