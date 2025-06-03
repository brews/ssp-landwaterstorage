"""
Logic for the CLI.
"""

from ssp_landwaterstorage.ssp_landwaterstorage_preprocess import (
    ssp_preprocess_landwaterstorage,
)
from ssp_landwaterstorage.ssp_landwaterstorage_fit import ssp_fit_landwaterstorage
from ssp_landwaterstorage.ssp_landwaterstorage_project import (
    ssp_project_landwaterstorage,
)
from ssp_landwaterstorage.ssp_landwaterstorage_postprocess import (
    ssp_postprocess_landwaterstorage,
)

import click


@click.command()
@click.option(
    "--scenario",
    envvar="SSP_LANDWATERSTORAGE_SCENARIO",
    help="Use RCP or SSP scenario.",
    default="rcp85",
)
@click.option(
    "--dotriangular",
    envvar="SSP_LANDWATERSTORAGE_DOTRIANGULAR",
    help="Use triangular distribution for GWD.",
    default=False,
)
@click.option(
    "--includepokherl",
    envvar="SSP_LANDWATERSTORAGE_INCLUDEPOKHERL",
    help="Include Pokhrl data for GWD.",
    default=False,
)
@click.option(
    "--baseyear",
    envvar="SSP_LANDWATERSTORAGE_BASEYEAR",
    help="Base year to which projections are centered.",
    default=2000,
    type=click.IntRange(2000, 2010),
)
@click.option(
    "--pyear-start",
    envvar="SSP_LANDWATERSTORAGE_PYEAR_START",
    help="Year for which projections start.",
    default=2000,
    type=click.IntRange(min=2000),
)
@click.option(
    "--pyear-end",
    envvar="SSP_LANDWATERSTORAGE_PYEAR_END",
    help="Year for which projections end.",
    default=2100,
    type=click.IntRange(max=2300),
)
@click.option(
    "--pyear-step",
    envvar="SSP_LANDWATERSTORAGE_PYEAR_STEP",
    help="Step size in years between start and end at which projections are produced.",
    default=10,
    type=click.IntRange(min=1),
)
@click.option(
    "--nsamps",
    envvar="SSP_LANDWATERSTORAGE_NSAMPS",
    help="Number of samples to generate.",
    default=20000,
)
@click.option(
    "--seed",
    envvar="SSP_LANDWATERSTORAGE_SEED",
    help="Seed value for random number generator.",
    default=1234,
)
@click.option(
    "--pipeline-id",
    envvar="SSP_LANDWATERSTORAGE_PIPELINE_ID",
    help="Unique identifier for this instance of the module.",
    required=True,
)
@click.option(
    "--dcyear-start",
    envvar="SSP_LANDWATERSTORAGE_DCYEAR_START",
    help="Year in which dam correction application is started.",
    default=2020,
)
@click.option(
    "--dcyear-end",
    envvar="SSP_LANDWATERSTORAGE_DCYEAR_END",
    help="Year in which dam correction application is ended.",
    default=2040,
)
@click.option(
    "--dcrate-lo",
    envvar="SSP_LANDWATERSTORAGE_DCRATE_LO",
    help="Lower bound of dam correction rate.",
    default=0.0,
)
@click.option(
    "--dcrate-hi",
    envvar="SSP_LANDWATERSTORAGE_DCRATE_HI",
    help="Upper bound of dam correction rate.",
    default=0.0,
)
@click.option(
    "--locationfile",
    envvar="SSP_LANDWATERSTORAGE_LOCATIONFILE",
    help="File container name, id, lat, and lon of points for localization.",
    default="location.lst",
)
@click.option(
    "--chunksize",
    envvar="SSP_LANDWATERSTORAGE_CHUNKSIZE",
    help="Number of locations to process at a time.",
    default=50,
)
def main(
    scenario,
    dotriangular,
    includepokherl,
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
    locationfile,
    chunksize,
) -> None:
    """
    Project groundwater depletion and dam impoundment contributions to sea level. See IPCC AR6 WG1 9.6.3.2.6.
    """
    click.echo("Hello from ssp-landwaterstorage!")
    ssp_preprocess_landwaterstorage(
        scenario,
        dotriangular,
        includepokherl,
        baseyear,
        pyear_start,
        pyear_end,
        pyear_step,
        pipeline_id,
    )
    ssp_fit_landwaterstorage(pipeline_id)
    ssp_project_landwaterstorage(
        nsamps, seed, dcyear_start, dcyear_end, dcrate_lo, dcrate_hi, pipeline_id
    )
    ssp_postprocess_landwaterstorage(locationfile, chunksize, pipeline_id)
