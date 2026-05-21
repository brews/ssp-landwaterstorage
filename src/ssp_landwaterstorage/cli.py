"""
Logic for the CLI.
"""

from dataclasses import dataclass
import logging

import click
import numpy as np

from ssp_landwaterstorage.service import project_landwaterstorage, localize_projection


@dataclass
class ContextObjects:
    """
    Objs from global projection that localization needs access to
    """

    gslr: np.ndarray
    preprocess_config: dict


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@click.group(
    invoke_without_command=True,
    context_settings={
        "auto_envvar_prefix": "SSP_LANDWATERSTORAGE",
        "show_default": True,
    },
)
@click.pass_context
@click.option(
    "--pipeline-id",
    help="Unique identifier for this instance of the module.",
    required=True,
)
@click.option(
    "--output-gslr-file",
    help="Path to write output global SLR file.",
    default=None,
    type=str,
)
@click.option(
    "--pophist-file",
    help="Path to the historical population file.",
    required=True,
    type=str,
)
@click.option(
    "--reservoir-file",
    help="Path to the groundwater impoundment file.",
    required=True,
    type=str,
)
@click.option(
    "--popscen-file",
    help="Path to the population scenario file.",
    required=True,
    type=str,
)
@click.option(
    "gwd_files",
    "--gwd-file",
    help="Path to groundwater depletion file.",
    multiple=True,
    type=str,
    required=True,
)
@click.option(
    "--scenario",
    help="Use RCP or SSP scenario.",
    default="rcp85",
)
@click.option(
    "--dotriangular",
    help="Use triangular distribution for GWD.",
    default=False,
)
@click.option(
    "--baseyear",
    help="Base year to which projections are centered.",
    default=2000,
    type=click.IntRange(2000, 2010),
)
@click.option(
    "--pyear-start",
    help="Year for which projections start.",
    default=2000,
    type=click.IntRange(min=2000),
)
@click.option(
    "--pyear-end",
    help="Year for which projections end.",
    default=2100,
    type=click.IntRange(max=2300),
)
@click.option(
    "--pyear-step",
    help="Step size in years between start and end at which projections are produced.",
    default=10,
    type=click.IntRange(min=1),
)
@click.option(
    "--nsamps",
    help="Number of samples to generate.",
    default=20000,
)
@click.option(
    "--seed",
    help="Seed value for random number generator.",
    default=1234,
)
@click.option(
    "--dcyear-start",
    help="Year in which dam correction application is started.",
    default=2020,
)
@click.option(
    "--dcyear-end",
    help="Year in which dam correction application is ended.",
    default=2040,
)
@click.option(
    "--dcrate-lo",
    help="Lower bound of dam correction rate.",
    default=0.0,
)
@click.option(
    "--dcrate-hi",
    help="Upper bound of dam correction rate.",
    default=0.0,
)
@click.option("--debug/--no-debug", default=False)
def main(
    ctx,
    pophist_file,
    reservoir_file,
    popscen_file,
    gwd_files,
    scenario,
    dotriangular,
    baseyear,
    pyear_start,
    pyear_end,
    pyear_step,
    nsamps,
    seed,
    pipeline_id,
    dcyear_start,
    dcyear_end,
    dcrate_lo,
    dcrate_hi,
    output_gslr_file,
    debug,
) -> None:
    """
    Project groundwater depletion and dam impoundment contributions to sea level. See IPCC AR6 WG1 9.6.3.2.6.
    """
    if debug:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    logger.info("Hello from ssp-landwaterstorage!")

    gslr, conf = project_landwaterstorage(
        pophist_file,
        reservoir_file,
        popscen_file,
        gwd_files,
        scenario,
        dotriangular,
        baseyear,
        pyear_start,
        pyear_end,
        pyear_step,
        nsamps,
        seed,
        pipeline_id,
        dcyear_start,
        dcyear_end,
        dcrate_lo,
        dcrate_hi,
        output_gslr_file,
    )
    ctx.obj = ContextObjects(gslr=gslr, preprocess_config=conf)

    logger.info("ssp-landwaterstorage complete")


@main.command
@click.pass_context
@click.option(
    "--location-file",
    help="File containing name, id, lat, and lon of points for localization.",
    type=str,
    required=True,
    # default="location.lst",
)
@click.option(
    "--chunksize",
    help="Number of locations to process at a time.",
    default=50,
)
@click.option(
    "--output-lslr-file",
    help="Path to write output local SLR file.",
    required=True,
    type=str,
)
@click.option(
    "--fp-file",
    help="Path to fingerprint file.",
    type=str,
    required=True,
)
def local(
    ctx,
    location_file,
    chunksize,
    output_lslr_file,
    fp_file,
):
    logger.info("Starting to localize ssp-landwaterstorage projection")

    localize_projection(
        ctx.obj.gslr,
        preprocess_conf=ctx.obj.preprocess_config,
        baseyear=ctx.parent.params["baseyear"],
        scenario=ctx.parent.params["scenario"],
        fp_file=fp_file,
        location_file=location_file,
        chunksize=chunksize,
        nsamps=ctx.parent.params["nsamps"],
        output_lslr_file=output_lslr_file,
    )

    logger.info("Localizing ssp-landwaterstorage complete")
